# RecruitIQ — AI Resume Screening & Recruitment Intelligence Platform

> A production-quality Flask application that uses NLP and Machine Learning to automatically parse resumes, score candidates against job descriptions, and surface data-driven hiring insights.

---

## Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Parsing** | Extracts name, email, phone, skills, experience, and education from PDF, DOCX, and TXT files |
| 🎯 **ATS Scoring** | Calculates a compatibility score using TF-IDF, semantic similarity (Sentence Transformers), and skill matching |
| 🏆 **Candidate Ranking** | Ranks all applicants for a job by their ATS score with one-click export to CSV |
| 📊 **Analytics Dashboard** | Interactive Chart.js dashboards for skill trends, score distributions, and experience histograms |
| 🔐 **Role-Based Access** | Admin, Recruiter, and Candidate roles with scoped views and permissions |
| 🤖 **ML Predictor** | Random Forest / Logistic Regression model predicts hire probability |
| 🔍 **Live Search** | Debounced full-text search across all candidate profiles |

---

## Tech Stack

**Backend:** Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate  
**NLP:** spaCy, NLTK, Sentence Transformers, scikit-learn (TF-IDF)  
**ML:** scikit-learn (Random Forest, Logistic Regression), joblib  
**Frontend:** Bootstrap 5.3, Chart.js, Plotly, Vanilla JS  
**Database:** SQLite (dev) — PostgreSQL-ready  
**Auth:** Flask-Login with Bcrypt password hashing

---

## Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd "AI Resume Screening & Recruitment Intelligence Platform"

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Linux/macOS

pip install -r requirements.txt
```

### 2. Download NLP Models

```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords punkt wordnet
```

### 3. Configure Environment

```bash
copy .env.example .env
# Edit .env and set a SECRET_KEY
```

### 4. Initialize Database

```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

### 5. Seed Demo Data

```bash
python scripts/seed_db.py
```

### 6. Run the App

```bash
python run.py
```

Open http://localhost:5000

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@recruitiq.dev | admin123! |
| Recruiter | recruiter@recruitiq.dev | recruiter123! |
| Candidate | alice.chen@email.com | candidate123! |

---

## Project Structure

```
├── app/
│   ├── blueprints/         # Flask blueprints (auth, dashboard, resume, jobs, matching, analytics, api, admin)
│   ├── models/             # SQLAlchemy ORM models
│   ├── nlp/                # NLP pipeline (parser, entity extractor, keyword extractor)
│   ├── ml/                 # ML pipeline (feature engineering, model training, predictor)
│   ├── services/           # Matching engine service
│   ├── utils/              # Decorators, validators, file handler
│   ├── static/             # CSS + JavaScript assets
│   └── templates/          # Jinja2 HTML templates
├── data/
│   └── skills_taxonomy.json  # 500+ skill definitions
├── scripts/
│   └── seed_db.py          # Demo data seeder
├── config.py               # Configuration classes
├── run.py                  # Application entry point
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search?q=` | Full-text search |
| GET | `/api/v1/resumes` | List resumes (paginated) |
| GET | `/api/v1/resumes/<id>` | Single resume detail |
| GET | `/api/v1/jobs` | List active jobs |
| GET | `/api/v1/matches/<job_id>` | Ranked match results |
| GET | `/api/v1/stats/overview` | Platform KPIs |
| GET | `/admin/api/health` | System health check |

---

## License

MIT License — Built as a capstone project demonstration.
