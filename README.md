# 🏦 Automated Enterprise Loan Approval System (AELAS)

A professional, end-to-end automated loan assessment system that combines Machine Learning (XGBoost) for decision-making and Large Language Models (OpenAI) for personalized customer communication.

## 🌟 Key Features
- **AI Decision Engine**: High-accuracy XGBoost model trained to predict loan approval status.
- **LLM Communication**: Generates personalized, professional emails based on loan decisions using OpenAI.
- **Real-time Analytics**: Interactive Streamlit dashboard for monitoring application flow, approving/rejecting manually, and triggering AI decisions.
- **RESTful API**: Fast and scalable FastAPI backend for seamless integration with frontend systems.
- **Customer Application Portal**: A modern, glassmorphism web interface for applicants to submit their details.
- **Email Sandbox**: Local capture mode to verify email content without sending, or SMTP to send via Gmail.
- **Database Memory**: Full persistence using PostgreSQL for all applications and AI predictions.

## 🛠️ Tech Stack
- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Intelligence**: XGBoost, Scikit-Learn, OpenAI GPT-4o
- **Data**: PostgreSQL, Pandas, NumPy
- **Dashboard**: Streamlit, Plotly
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

**Start the Monitoring Dashboard:**
```powershell
streamlit run dashboard.py
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
