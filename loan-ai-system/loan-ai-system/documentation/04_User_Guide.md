# 📖 User Guide: How to Run the System

## Prerequisites
- **PostgreSQL** installed and running.
- **Python 3.12+** installed.
- All dependencies installed (`pip install -r requirements.txt`).

## Step 1: Environment Setup
1.  Open the `.env` file in the project root.
2.  Ensure your `DB_PASSWORD` and `SENDGRID_API_KEY` are correct.
3.  Set `MAIL_MODE=SANDBOX` if you want to test without using email credits.

## Step 2: Initialize the Database
Run the following command to create the necessary tables:
```powershell
python src/create_table.py
```

## Step 3: Start the API Server
Launch the FastAPI server:
```powershell
uvicorn api.main:app --reload
```
The interactive documentation will be available at: `http://127.0.0.1:8000/docs`

## Step 4: Launch the Dashboard
In a new terminal, run:
```powershell
streamlit run dashboard.py
```
Open your browser to: `http://localhost:8501`

## Step 5: Testing the System
1.  Go to the API docs (/docs).
2.  Use the **POST /predict** endpoint.
3.  Enter sample applicant data and click **Execute**.
4.  Check the Admin Dashboard to see the application appear with **Rs.** currency formatting.
5.  Check the `mail_service/intercepted_emails/` folder to see the result!
