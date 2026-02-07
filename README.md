# Autonomous Job Application Platform (Agentic + Microservices)

## 📌 Vision
Build a fully automated, agent-assisted job application platform where a user uploads a resume once, defines preferences, and the system intelligently finds, matches, generates, and applies to jobs in the background.

This system is:
- Open-source only
- Python-first
- Microservices-based
- Agentic AI for planning (not execution)
- Low latency, safe, and replaceable by design

---

## 🧠 Core Architectural Principles
1. AI plans, code executes
2. Microservices over monolith
3. Deterministic first, AI second
4. Human-in-the-loop
5. No vendor lock-in

---

## 🗂️ Repository Structure
job-application-platform/
├── services/
├── agents/
├── automation/
├── frontend/
├── shared/
├── infra/
├── scripts/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md

---

## 🔧 Services Overview
- Orchestrator: workflow & state machine (no AI)
- Job Fetcher: fetch & normalize jobs
- Matching Engine: eligibility & similarity scoring
- Resume Engine: country & ATS-aware resume generation
- Apply Engine: deterministic application execution
- Notification: email & alerts

---

## 🤖 Agentic AI
Framework: CrewAI (open source)

Agents:
- Job Matching Agent
- Resume Strategy Agent
- Cover Letter Agent
- Application Strategy Agent

Rules:
- Agents output JSON only
- No side effects
- No browser control

---

## 🛠️ Tech Stack
Backend: Python, FastAPI, Celery, PostgreSQL
AI: CrewAI, Ollama, sentence-transformers, FAISS
Automation: Playwright
Frontend: React, Tailwind
Infra: Docker

---

## 🚀 Development Workflow
1. Scaffold folders
2. Build orchestrator skeleton
3. Add one job source
4. Add matching logic
5. Add resume engine
6. Add automation
7. Gradually add agents

---

## 🧠 Architect’s Note
This is a decision-driven automation platform, not a scraper or resume generator.
