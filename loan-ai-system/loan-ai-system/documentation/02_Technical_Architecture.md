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
    - Uses SendGrid (or Sandbox Mode) to handle email delivery.
- **Key File**: `llm/email_generator.py`, `mail_service/email_sender.py`

### 4. The Data Layer (PostgreSQL)
- **Role**: The "Memory".
- **Function**: Stores every application and every AI prediction permanently.
- **Key File**: `src/database.py`, `src/create_table.py`

## Data Flow Diagram
1. **Input**: User POSTs data to `/predict`.
2. **Predict**: ML Model analyzes the numbers → returns `APPROVED` or `REJECTED`.
3. **Store**: Results are saved to the PostgreSQL `loan_applications` and `loan_predictions` tables.
4. **Notify**: LLM creates personalized text → Email service delivers it (or saves to `intercepted_emails`).
5. **View**: The Streamlit Dashboard fetches data from SQL to show live status.
