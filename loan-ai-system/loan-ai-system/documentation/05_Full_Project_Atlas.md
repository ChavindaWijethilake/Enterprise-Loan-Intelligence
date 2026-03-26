# 🗺️ Project Atlas: Full Technical Documentation

This document serves as the "Master Map" for the Automated Enterprise Loan Approval System (AELAS). It provides a deep dive into every directory, core file, and technical decision made across the codebase.

## 🌟 Project Concept
**Problem**: Traditional enterprise loan processing is slow, prone to human bias, and requires manual credit-scoring and individual letter writing.
**Solution**: A modular "Decision Intelligence" system that automates the entire pipeline—from application submission to risk prediction (ML) and personalized outcome communication (LLM).

---

## 📂 Directory Structure Map

### `root/`
The gateway to the entire ecosystem.
- `README.md`: High-level entry point with quick-start and demo credentials.
- `requirements.txt`: Unified dependency list ensuring environment reproducibility.
- `.env`: Secure configuration store for OpenAI keys, Database credentials, and SMTP settings.

### `api/`
The **Central Nervous System**.
- `main.py`: A high-performance **FastAPI** application. It serves as the bridge between the ML models and the front-end portals.

### `customer-portal/`
The **User Interface (Applicants)**.
- **Next.js 15+ & TailwindCSS**: A modern, responsive portal where applicants submit financial data. It communicates with the Backend via REST API.

### `dashboard.py`
The **Command Center (Admin)**.
- **Streamlit**: An industrial-grade monitoring platform for loan officers. Features institutional branding, real-time analytics, and a "Zero-Jitter" glassmorphism UI.

### `llm/`
The **Language Engine**.
- `email_generator.py`: Orchestrates **OpenAI GPT-4o** to transform raw prediction data into empathetic, professional decision letters.

### `models/`
The **Intelligence Artifacts**.
- `loan_model.pk1`: A serialized **XGBoost** model calibrated for high-precision credit risk assessment.

### `pipeline.py`
The **Data Orchestrator**.
- Encapsulates the end-to-end flow: Preprocessing → Feature Engineering → Prediction → Database Sync.

### `src/`
The **Utility Backbone**.
- `db_service.py`: Standardized PostgreSQL connection pooling.
- `feature_engineering.py`: Mathematical transformations used to ensure model input consistency.
- `preprocess.py`: Sanitization logic for raw user inputs.

### `tests/`
The **Quality Guard**.
- Unit tests for the ML pipeline, API endpoints, and database connectivity.

### 🛠️ Utility Scripts (Root)
Supporting tools for system maintenance:
- `reset_db.py`: Wipes and re-initializes all PostgreSQL tables for a clean slate.
- `fix_auth.py`: Ensures the authentication logic and session state are correctly synced.
- `generate_docx.py`: Template engine for generating offline Word-based loan documents.
- `list_dbs.py`: Debugging utility to inspect active PostgreSQL databases and connection health.
- `verify_real_data.py`: Sanity-check script to ensure the model performs correctly on production-grade inputs.

---

## 🛠️ Technology Rationale: "The Why"

| Technology | Why we used it |
| :--- | :--- |
| **FastAPI** | Chosen for its asynchronous speed and native OpenAPI (Swagger) integration, making it ideal for a high-traffic financial backend. |
| **XGBoost** | The gold standard for tabular data. It provides the "Decision Tree" transparency needed for financial accountability while maintaining industry-leading accuracy. |
| **Streamlit** | Allowed for rapid prototyping of a data-dense "Bloomberg-style" dashboard without the overhead of a full React build for internal admin tools. |
| **Next.js 15** | Used for the applicant portal to leverage Server Components and superior SEO/speed for public-facing user experiences. |
| **PostgreSQL** | Offers robust ACID compliance, ensuring that sensitive financial transaction records are never lost or corrupted. |
| **OpenAI GPT-4o** | Provides the "Human Touch" at scale. It automates the writing of personalized approval/rejection letters that would normally take officers hours. |

---

## 🏗️ Architectural Philosophy

The system follows a **Separation of Concerns** (SoC) model:
1.  **Stateful Storage**: PostgreSQL holds the "System of Record".
2.  **Stateless API**: FastAPI handles request processing without storing local state.
3.  **Intelligence services**: ML and LLM are treated as modular "pluggable" workers, allowing for easy updates to the models without breaking the UI.

---
*This codebase is designed for industrial scalability and technical transparency.*
