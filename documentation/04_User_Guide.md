# 📖 User Guide: How to Run the System

## Prerequisites
- **PostgreSQL** installed and running.
- **Python 3.12+** installed.
- All dependencies installed (`pip install -r requirements.txt`).

## Step 1: Environment Setup
1.  Open the `.env` file in the project root.
2.  Ensure your PostgreSQL credentials are correct.
3.  Add your Google App Password to `MAIL_PASSWORD` and set `MAIL_MODE=SMTP` to send real emails, or `MAIL_MODE=SANDBOX` to intercept them locally.

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
1.  Open your browser to: `http://localhost:8000/` to view the Customer Application Portal.
2.  Fill out the beautiful loan application form and submit it.
3.  Go back to the Admin Dashboard at `http://localhost:8501`.
4.  Under the "Pending Approvals" tab, you will see the new application.
5.  Click either **Auto AI Decision** or a **Manual** button to process the loan and trigger the email dispatch!
