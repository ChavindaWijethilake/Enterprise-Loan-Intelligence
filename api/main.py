# =============================================================================
# api/main.py
# =============================================================================
# PURPOSE: Create a REST API using FastAPI that serves the Customer Portal
#          and handles backend loan processing for the Admin Dashboard.
#
# ENDPOINTS:
#   GET  /                       → Serves the Customer Application HTML Portal
#   GET  /health                 → Health check
#   POST /api/predict            → (Legacy) Submit loan, get instant prediction
#   POST /api/apply              → Submits a loan to PENDING status in the DB
#   POST /api/process-auto/{id}  → Triggers AI prediction + automated email
#   POST /api/process-manual/{id}→ Forces Human approval/rejection + email
#
# RUN:
#   uvicorn api.main:app --reload
#
# OPEN:
#   http://localhost:8000/docs
# =============================================================================

import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
sys.path.insert(0, PROJECT_DIR)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.logger import get_logger

logger = get_logger("api_main")
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import pandas as pd
import joblib

from llm.email_generator import generate_email
from mail_service.email_sender import send_email
from src.db_service import save_loan_application, save_loan_prediction, get_loan_application, update_loan_status

# ---------------------------------------------------------------------------
# Initialize FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Loan Approval API",
    description="AI-powered enterprise loan approval system using ML + LLM",
    version="1.0.0",
)

# Mount the static directory
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_DIR, "static")), name="static")

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load ML model
# ---------------------------------------------------------------------------
MODEL_PATH = os.path.join(PROJECT_DIR, "models", "xgb_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded from: {MODEL_PATH}")
except FileNotFoundError:
    logger.warning(f"Model not found at {MODEL_PATH}. Run train_model.py first!")
    model = None

APPROVE_THRESHOLD = 0.7
REJECT_THRESHOLD = 0.3

# ---------------------------------------------------------------------------
# Request Model
# ---------------------------------------------------------------------------
class LoanApplication(BaseModel):

    applicant_name: str = Field(..., description="Applicant name")
    applicant_email: str = Field(default="", description="Applicant email")

    no_of_dependents: int = Field(..., ge=0, le=10)
    education: int = Field(..., ge=0, le=1)
    self_employed: int = Field(..., ge=0, le=1)

    income_annum: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    loan_term: int = Field(..., gt=0)

    cibil_score: int = Field(..., ge=300, le=900)

    residential_assets_value: float
    commercial_assets_value: float
    luxury_assets_value: float
    bank_asset_value: float


# ---------------------------------------------------------------------------
# Response Model
# ---------------------------------------------------------------------------
class PredictionResponse(BaseModel):

    applicant_name: str
    decision: str
    approval_probability: float
    rejection_probability: float
    email_content: str


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return FileResponse(os.path.join(PROJECT_DIR, "static", "index.html"))


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


# ---------------------------------------------------------------------------
# Prediction Endpoint
# ---------------------------------------------------------------------------
@app.post("/predict", response_model=PredictionResponse)
def predict_loan(application: LoanApplication):

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run training first.",
        )

    # Convert request → DataFrame
    data = pd.DataFrame(
        [application.model_dump(exclude={"applicant_name", "applicant_email"})]
    )

    # Feature engineering
    data["total_assets"] = (
        data["residential_assets_value"]
        + data["commercial_assets_value"]
        + data["luxury_assets_value"]
        + data["bank_asset_value"]
    )

    data["loan_to_income"] = data["loan_amount"] / (data["income_annum"] + 1)

    data["assets_to_loan"] = data["total_assets"] / (data["loan_amount"] + 1)

    data["income_per_dependent"] = data["income_annum"] / (
        data["no_of_dependents"] + 1
    )

    data["loan_term_to_amount"] = data["loan_term"] / (data["loan_amount"] + 1)

    # Model prediction
    prediction = model.predict(data)[0]
    probabilities = model.predict_proba(data)[0]

    approval_prob = float(probabilities[1])
    rejection_prob = float(probabilities[0])

    # Decision engine
    if approval_prob > APPROVE_THRESHOLD:
        decision = "APPROVED"
    elif approval_prob < REJECT_THRESHOLD:
        decision = "REJECTED"
    else:
        decision = "CONDITIONAL"

    # Generate email using LLM
    try:

        email_content = generate_email(
            applicant_name=application.applicant_name,
            decision=decision,
            probability=approval_prob,
            loan_amount=application.loan_amount,
        )

        # Send email if address provided
        if application.applicant_email:

            send_email(
                recipient_email=application.applicant_email,
                subject="Loan Application Decision",
                body=email_content,
            )

    except Exception as e:

        email_content = f"[Email generation failed: {str(e)}. Check OPENAI_API_KEY]"

    # -----------------------------------------------------------------------
    # Database persistence
    # -----------------------------------------------------------------------
    try:
        loan_id = save_loan_application(application.model_dump(), decision)
        if loan_id:
            save_loan_prediction(
                loan_id=loan_id,
                status=decision,
                probability=approval_prob,
                email_sent=bool(application.applicant_email)
            )
            logger.info(f"Saved application to database (ID: {loan_id})")
    except Exception as db_err:
        logger.error(f"Database storage failed: {db_err}", exc_info=True)

    # Return API response
    return PredictionResponse(
        applicant_name=application.applicant_name,
        decision=decision,
        approval_probability=approval_prob,
        rejection_probability=rejection_prob,
        email_content=email_content,
    )

# ---------------------------------------------------------------------------
# New Workflow: Apply (Separated from Prediction)
# ---------------------------------------------------------------------------
@app.post("/api/apply")
def apply_loan(application: LoanApplication):
    # Save as pending
    loan_id = save_loan_application(application.model_dump(), "PENDING")
    if not loan_id:
        raise HTTPException(status_code=500, detail="Database error occurred while saving application.")
    
    return {"message": "Application submitted successfully", "loan_id": loan_id}


# ---------------------------------------------------------------------------
# Background Task Worker
# ---------------------------------------------------------------------------
def background_delivery_task(loan_id: int, applicant_name: str, applicant_email: str, loan_amount: float, decision: str, probability: float, model_type: str):
    email_content = ""
    email_sent_success = False
    
    try:
        from src.document_generator import generate_loan_agreement
        attachment_path = generate_loan_agreement(applicant_name, loan_amount, decision)
        
        email_content = generate_email(
            applicant_name=applicant_name,
            decision=decision,
            probability=probability,
            loan_amount=loan_amount,
        )
        if applicant_email:
            email_sent_success = send_email(
                recipient_email=applicant_email,
                subject=f"Loan Application Update: {decision}" if "MANUAL" not in model_type else f"Manual Loan Review: {decision}",
                body=email_content,
                attachment_path=attachment_path
            )
    except Exception as e:
        logger.error(f"Failed to generate/send email in background: {str(e)}", exc_info=True)
        
    try:
        save_loan_prediction(loan_id, model_type, probability, email_sent_success)
        logger.info(f"Background task completed for Loan ID: {loan_id}")
    except Exception as db_err:
        logger.error(f"Failed to save prediction in background: {db_err}", exc_info=True)

# ---------------------------------------------------------------------------
# New Workflow: Process Batch (AI Decision for all PENDING)
# ---------------------------------------------------------------------------
@app.post("/api/process-batch")
def process_batch(background_tasks: BackgroundTasks):
    """
    Finds all PENDING applications and triggers the AI processing workflow for each.
    """
    try:
        from src.db_service import get_all_loans
        loans = get_all_loans()
        pending_loans = [l for l in loans if l['status'] == 'PENDING']
        
        if not pending_loans:
            return {"message": "No pending applications found to process.", "count": 0}
            
        for loan in pending_loans:
            # Re-use the existing process_auto logic internally or trigger it
            # For efficiency in a batch, we'll trigger the background task directly
            loan_id = loan['loan_id']
            applicant_name = loan['applicant_name']
            applicant_email = loan.get('applicant_email', "")
            loan_amount = loan['loan_amount']
            
            # 1. Update status to PROCESSING to avoid double-picks
            update_loan_status(loan_id, "PROCESSING")
            
            # 2. Add to background tasks
            # Note: We use XGBoost and Auto mode
            background_tasks.add_task(
                process_auto_logic, 
                loan_id, 
                applicant_name, 
                applicant_email, 
                loan_amount
            )
            
        return {
            "message": f"Batch processing started for {len(pending_loans)} applications.",
            "count": len(pending_loans)
        }
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch process error: {str(e)}")

def process_auto_logic(loan_id, applicant_name, applicant_email, loan_amount):
    """Refactored logic to be shared between individual and batch processing."""
    try:
        from src.db_service import get_loan_by_id
        loan_data = get_loan_by_id(loan_id)
        if not loan_data:
            return
            
        # Prepare for prediction (exclude non-feature fields)
        exclude_fields = {"loan_id", "applicant_name", "applicant_email", "status", "created_at", "prediction_date", "model_used", "approval_prob", "email_sent"}
        features = {k: v for k, v in loan_data.items() if k not in exclude_fields}
        
        # Predict
        from src.predict import predict_loan
        result = predict_loan(features)
        
        # Update status
        update_loan_status(loan_id, result['decision'])
        
        # Trigger delivery (PDF + Email)
        background_delivery_task(
            loan_id,
            applicant_name,
            applicant_email,
            loan_amount,
            result['decision'],
            result['approval_probability'],
            "AI_BATCH_AUTO"
        )
    except Exception as e:
        logger.error(f"Auto-process logic failed for loan {loan_id}: {e}")
        update_loan_status(loan_id, "FAILED")

# ---------------------------------------------------------------------------
# New Workflow: Process Auto (AI Decision)
# ---------------------------------------------------------------------------
@app.post("/api/process-auto/{loan_id}")
def process_auto(loan_id: int, background_tasks: BackgroundTasks):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    app_data = get_loan_application(loan_id)
    if not app_data:
        raise HTTPException(status_code=404, detail="Loan application not found")
        
    if app_data["status"] != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot process an application that is already {app_data['status']}")

    # Convert request → DataFrame
    df_data = pd.DataFrame([{k: v for k, v in app_data.items() if k not in ["applicant_name", "applicant_email", "status"]}])

    # Feature engineering
    df_data["total_assets"] = (
        df_data["residential_assets_value"]
        + df_data["commercial_assets_value"]
        + df_data["luxury_assets_value"]
        + df_data["bank_asset_value"]
    )
    df_data["loan_to_income"] = df_data["loan_amount"] / (df_data["income_annum"] + 1)
    df_data["assets_to_loan"] = df_data["total_assets"] / (df_data["loan_amount"] + 1)
    df_data["income_per_dependent"] = df_data["income_annum"] / (df_data["no_of_dependents"] + 1)
    df_data["loan_term_to_amount"] = df_data["loan_term"] / (df_data["loan_amount"] + 1)

    # Model prediction
    probabilities = model.predict_proba(df_data)[0]
    approval_prob = float(probabilities[1])

    # Decision engine
    if approval_prob > APPROVE_THRESHOLD: decision = "APPROVED"
    elif approval_prob < REJECT_THRESHOLD: decision = "REJECTED"
    else: decision = "CONDITIONAL"

    # Update DB
    update_loan_status(loan_id, decision)
    
    # Offload LLM + Email + Prediction Save to background
    background_tasks.add_task(
        background_delivery_task,
        loan_id=loan_id,
        applicant_name=app_data["applicant_name"],
        applicant_email=app_data["applicant_email"],
        loan_amount=app_data["loan_amount"],
        decision=decision,
        probability=approval_prob,
        model_type=decision
    )
    
    return {
        "loan_id": loan_id,
        "decision": decision,
        "probability": approval_prob,
        "email_sent": "pending_background"
    }

# ---------------------------------------------------------------------------
# New Workflow: Process Manual (Human Decision)
# ---------------------------------------------------------------------------
class ManualDecisionRequest(BaseModel):
    decision: str

@app.post("/api/process-manual/{loan_id}")
def process_manual(loan_id: int, request: ManualDecisionRequest, background_tasks: BackgroundTasks):
    app_data = get_loan_application(loan_id)
    if not app_data:
        raise HTTPException(status_code=404, detail="Loan application not found")
        
    if app_data["status"] != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot process an application that is already {app_data['status']}")

    decision = request.decision.upper()
    if decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")

    # Update DB
    update_loan_status(loan_id, decision)
    
    # Offload LLM + Email + Prediction Save to background
    background_tasks.add_task(
        background_delivery_task,
        loan_id=loan_id,
        applicant_name=app_data["applicant_name"],
        applicant_email=app_data["applicant_email"],
        loan_amount=app_data["loan_amount"],
        decision=decision,
        probability=1.0 if decision == "APPROVED" else 0.0,
        model_type=f"MANUAL_{decision}"
    )

    return {
        "loan_id": loan_id,
        "decision": decision,
        "email_sent": "pending_background"
    }

# ---------------------------------------------------------------------------
# New Workflow: Download PDF Agreement
# ---------------------------------------------------------------------------
@app.get("/api/documents/{loan_id}")
def download_loan_agreement(loan_id: int):
    app_data = get_loan_application(loan_id)
    if not app_data:
        raise HTTPException(status_code=404, detail="Loan application not found")
        
    applicant_name = app_data["applicant_name"]
    docs_dir = os.path.join(PROJECT_DIR, "documents")
    expected_filename = f"Loan_Agreement_{applicant_name.replace(' ', '_')}.pdf"
    file_path = os.path.join(docs_dir, expected_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found for this loan.")
        
    return FileResponse(path=file_path, filename=expected_filename, media_type='application/pdf')