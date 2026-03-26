# 🏗️ Project Architecture & Data Flow

## System Components
The system is divided into five main layers:

### 1. The Customer Portal (Next.js)
- **Role**: The "Applicant Gateway".
- **Function**: A modern Next.js 15+ / TypeScript frontend where loan applicants submit their details via a secure, responsive web form.
- **Key Dir**: `customer-portal/`

### 2. The API Layer (FastAPI)
- **Role**: The "Orchestrator".
- **Function**: Receives incoming loan requests from the portal and orchestrates AI prediction, email delivery, and database persistence. Supports individual auto-processing (`/api/process-auto`), batch processing (`/api/process-batch`), and manual overrides (`/api/process-manual`).
- **Key File**: `api/main.py`

### 3. The Intelligence Layer (Machine Learning)
- **Role**: The "Decision Maker".
- **Function**: Uses an **XGBoost** model (trained on past loan data) to predict the approval probability. A decision engine then maps the probability to APPROVED / REJECTED / CONDITIONAL using configurable thresholds.
- **Key Files**: `src/predict.py`, `pipeline.py`, `models/xgb_model.pkl`

### 4. The Communication Layer (LLM + Email)
- **Role**: The "Messenger".
- **Function**:
    - Uses OpenAI's GPT-4o to generate human-like, personalized decision emails.
    - Uses standard SMTP (via Gmail App Passwords) for secure email delivery on port 465.
    - Generates PDF loan agreement documents attached to notification emails.
- **Key Files**: `llm/email_generator.py`, `mail_service/email_sender.py`, `src/document_generator.py`

### 5. The Data Layer (PostgreSQL)
- **Role**: The "Memory".
- **Function**: Stores every application and every AI prediction permanently using a psycopg2 connection pool managed by `src/db_service.py`.
- **Key Files**: `src/db_service.py`, `src/create_table.py`

### 6. The Admin Dashboard (Streamlit)
- **Role**: The "Control Center".
- **Function**: A high-density, industrial-themed Streamlit dashboard with glassmorphism aesthetics. Features five views: Executive Overview, Credit Prediction Gateway (with Batch Intelligence), Email Dispatch Control, Quantitative Analytics (Plotly), and Institutional Audit Ledger.
- **Key File**: `dashboard.py`

## Data Flow Diagram
1. **Apply**: Applicant submits the Next.js web form → `POST /api/apply`.
2. **Pending**: Application is saved to PostgreSQL `loan_applications` with a PENDING status.
3. **Review**: Admin opens the Streamlit Dashboard, sees the pending application, and clicks an action.
4. **Process**: The dashboard calls either `/api/process-auto/{id}` (AI model), `/api/process-batch` (all pending), or `/api/process-manual/{id}` (human override). Result is saved to `loan_predictions`.
5. **Notify**: A background worker generates a PDF agreement, LLM creates personalized email text, and the SMTP service delivers it to the applicant.
