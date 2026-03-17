# 🏗️ Project Architecture & Data Flow

## System Components
The system is divided into four main layers:

### 1. The API Layer (FastAPI)
- **Role**: The "Front Door" of the system.
- **Function**: Receives incoming loan requests and orchestrates the other services.
- **Key File**: `api/main.py`

### 2. The Intelligence Layer (Machine Learning)
- **Role**: The "Decision Maker".
- **Function**: Uses an **XGBoost** model (trained on past loan data) to predict the status.
- **Key File**: `pipeline.py`, `models/xgb_model.pkl`

### 3. The Communication Layer (LLM + Email)
- **Role**: The "Messenger".
- **Function**: 
    - Uses OpenAI's GPT models to generate human-like email text.
    - Uses standard SMTP (via Gmail App Passwords typically) to handle secure email delivery on port 465.
- **Key File**: `llm/email_generator.py`, `mail_service/email_sender.py`

### 4. The Data Layer (PostgreSQL)
- **Role**: The "Memory".
- **Function**: Stores every application and every AI prediction permanently.
- **Key File**: `src/database.py`, `src/create_table.py`

## Data Flow Diagram
1. **Apply**: User submits the frontend web form to `POST /api/apply`.
2. **Pending**: Application is saved to PostgreSQL `loan_applications` with a PENDING status.
3. **Review**: Admin opens the Streamlit Dashboard, sees the pending application, and clicks an action.
4. **Process**: The dashboard calls either `/api/process-auto/{id}` (uses ML Model) or `/api/process-manual/{id}` (human override). Result is saved to `loan_predictions`.
5. **Notify**: LLM creates personalized text → SMTP service securely emails the applicant the decision.
