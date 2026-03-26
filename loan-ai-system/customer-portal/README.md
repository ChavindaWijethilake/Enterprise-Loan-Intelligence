# 🏦 AELAS — Customer Application Portal

The public-facing loan application portal for the **Automated Enterprise Loan Approval System (AELAS)**. Built with [Next.js 15](https://nextjs.org), TypeScript, and TailwindCSS.

## Purpose

This portal allows loan applicants to:
1. Fill out a secure, responsive loan application form.
2. Submit their details to the FastAPI backend (`POST /api/apply`).
3. Receive a confirmation that their application is under review.

All submitted applications appear in the **Admin Dashboard** (`dashboard.py`) for AI or manual processing.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the portal.

> **Note**: The FastAPI backend (`uvicorn api.main:app --reload`) must be running on port 8000 for form submissions to work.

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Font**: Geist (via `next/font`)
