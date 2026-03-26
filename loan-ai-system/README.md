# 🏦 Automated Enterprise Loan Approval System (AELAS)

A professional, end-to-end automated loan assessment system that combines Machine Learning (XGBoost) for decision-making and Large Language Models (OpenAI) for personalized customer communication.

## 🌟 Key Features (Version 2.0)
- **Institutional Admin Dashboard**: High-density Streamlit interface with glassmorphism aesthetics, real-time analytics, and modular page-header components.
- **Improved Layout Stability**: Redesigned login portal and dashboard containers for a "Zero-Jitter" experience.
- **AI Decision Engine**: High-accuracy XGBoost model trained to predict loan approval status.
- **LLM Communication**: Uses OpenAI GPT-4o to generate professional, personalized decision emails.
- **Batch Intelligence**: Trigger AI evaluations for all pending applications in a single click via background workers.
- **Customer Application Portal**: A modern Next.js 15+ frontend for applicants to submit details securely.
- **Database Memory**: Full persistence using PostgreSQL for all applications and AI predictions.
- **Currency Standardization**: Institutional-grade formatting using **Rs.** across all financial modules.
- **Email Sandbox**: Local capture mode to verify email content without sending, or SMTP to send via Gmail.

## 🛠️ Tech Stack
- **Frontend (Applicant)**: Next.js 15, TypeScript, TailwindCSS
- **Backend (API)**: Python 3.12, FastAPI, Uvicorn
- **Dashboard (Admin)**: Streamlit, Plotly (Glassmorphism UI)
- **Intelligence**: XGBoost, Scikit-Learn, OpenAI GPT-4o
- **Data**: PostgreSQL, Pandas, NumPy
- **DevOps**: smtplib (SSL), Python-Dotenv

## 🚀 Quick Start

### 1. Installation
```powershell
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file from the documentation template:
```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=loan_system
DB_USER=postgres
DB_PASSWORD=your_password

OPENAI_API_KEY=your_key

MAIL_MODE=SMTP
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
```

### 3. Initialize Database
```powershell
python src/create_table.py
```

### 4. Run the System
**Start the API Server:**
```powershell
uvicorn api.main:app --reload
```

**Start the Admin Dashboard:**
```powershell
streamlit run dashboard.py
```

**Start the Customer Portal (Next.js):**
```powershell
cd customer-portal
npm install
npm run dev
```

## 📋 Demo & Testing Guide

For recruitment or review purposes, you can test the end-to-end flow using these credentials and local mappings:

### 👤 Local Demo Access
| Portal | URL | Default Credentials |
| :--- | :--- | :--- |
| **Admin Dashboard** | `http://localhost:8501` | **admin / admin** |
| **Customer Portal** | `http://localhost:3000` | No Login Required |
| **API Documentation** | `http://localhost:8000/docs` | Swagger / OpenAPI |

### 🔄 End-to-End Workflow
1.  **Submit**: Fill out a loan form on the **Customer Portal** (`:3000`).
2.  **Authenticate**: Log in to the **Admin Dashboard** (`:8501`) using `admin` / `admin`.
3.  **Analyze**: Locate the new request in the **Credit Prediction Gateway**.
4.  **Decide**: Click **🤖 Auto AI Decision**. The system will use XGBoost for prediction and GPT-4o for email generation.
5.  **Audit**: Review the final decision and letter in the **Institutional Ledger** (Audit Log).
## 📄 Documentation
Detailed technical architecture, beginner guides, and user manuals can be found in the `documentation/` folder.

---
*Created for secure, automated enterprise financial workflows.*
