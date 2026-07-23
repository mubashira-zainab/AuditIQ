<div align="center">

# 📊 AuditIQ Financial AI Agent

**An Enterprise-Grade, AI-Powered Financial Auditing & Forecasting Platform**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 🚀 Overview

**AuditIQ** is a state-of-the-art financial ledger and forecasting agent designed to automate financial analysis, risk assessment, and report generation. Built with a unified architecture, the FastAPI backend natively serves the enterprise dashboard, eliminating CORS overhead and proxy complexities—providing a single, streamlined deployment target.

---

## 📂 Project Architecture

```text
AuditIQ/
├── app/                  # FastAPI application factory, routers, and schemas
├── backend/              # Core business logic and domain engines
│   ├── core/             # Security sanitization & domain exceptions
│   └── services/         # In-memory session store, AI pipeline, and forecaster
├── web/                  # Frontend assets (HTML5, CSS3, Vanilla JS interface)
├── tests/                # Automated testing suite (pytest)
├── requirements.txt      # Python dependencies
└── render.yaml           # Deployment blueprint