# 🏦 Automated Enterprise Loan Approval System (AELAS)

A professional, end-to-end automated loan assessment system that combines Machine Learning (XGBoost) for decision-making and Large Language Models (OpenAI) for personalized customer communication.

## 🌟 Key Features
- **Industrial Admin Dashboard**: High-density Streamlit interface with glassmorphism aesthetics, real-time analytics, and advanced audit logs.
- **AI Decision Engine**: High-accuracy XGBoost model trained to predict loan approval status.
- **LLM Communication**: Uses OpenAI GPT-4o to generate professional, personalized decision emails.
- **Batch Intelligence**: Trigger AI evaluations for all pending applications in a single click via background workers.
- **Customer Application Portal**: A modern Next.js 15+ frontend for applicants to submit details securely.
- **Database Memory**: Full persistence using PostgreSQL for all applications and AI predictions.
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

## 📋 How to Test
1. Open the Customer Application Portal at `http://localhost:8000/`.
2. Fill out and submit a sample loan application.
3. Open the Admin Dashboard at `http://localhost:8501`.
4. Go to the "Pending Approvals" tab, locate your application, and click **🤖 Auto AI Decision** or a Manual button.
5. Check your email inbox to see the generated decision email!
## 📄 Documentation
Detailed technical architecture, beginner guides, and user manuals can be found in the `documentation/` folder.

---
*Created for secure, automated enterprise financial workflows.*
