# 🏦 Automated Enterprise Loan Approval System (AELAS)

A professional, end-to-end automated loan assessment system that combines Machine Learning (XGBoost) for decision-making and Large Language Models (OpenAI) for personalized customer communication.

## 🌟 Key Features
- **AI Decision Engine**: High-accuracy XGBoost model trained to predict loan approval status.
- **LLM Communication**: Generates personalized, professional emails based on loan decisions using OpenAI.
- **Real-time Analytics**: Interactive Streamlit dashboard for monitoring application flow, approval rates, and CIBIL score trends.
- **RESTful API**: Fast and scalable FastAPI backend for seamless integration with frontend systems.
- **Email Sandbox**: Local capture mode to verify email content without requiring SendGrid credits.
- **Database Memory**: Full persistence using PostgreSQL for all applications and AI predictions.

## 🛠️ Tech Stack
- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Intelligence**: XGBoost, Scikit-Learn, OpenAI GPT-4o
- **Data**: PostgreSQL, Pandas, NumPy
- **Dashboard**: Streamlit, Plotly
- **DevOps**: SendGrid API, Python-Dotenv

## 🚀 Quick Start

### 1. Installation
```powershell
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file from the documentation template:
```env
DB_PASSWORD=your_password
SENDGRID_API_KEY=your_key
OPENAI_API_KEY=your_key
MAIL_MODE=SANDBOX
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
1. Open the API documentation at `http://127.0.0.1:8000/docs`.
2. Use the `/predict` endpoint to submit a loan application.
3. If `MAIL_MODE=SANDBOX`, view the resulting email in `mail_service/intercepted_emails/`.
4. Refresh the dashboard at `http://localhost:8501` to see the new data point.

## 📄 Documentation
Detailed technical architecture, beginner guides, and user manuals can be found in the `documentation/` folder.

---
*Created for secure, automated enterprise financial workflows.*
