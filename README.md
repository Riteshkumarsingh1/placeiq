# 📊 PlaceIQ — College Placement Intelligence Platform

> **College Placement Predictor • AI Resume Analyzer • GATE Score Calculator • Placement Chatbot**

PlaceIQ is an all-in-one career intelligence platform built for engineering students and job seekers. It combines **Machine Learning, NIRF data, SQL/database technologies, and Groq LLMs** to provide placement insights, resume feedback, GATE-based college recommendations, and an AI placement assistant.

> ⚠️ **Educational Project:** PlaceIQ is intended for educational and informational purposes. Predictions and recommendations should not be treated as guaranteed placement outcomes.

---

## 🚀 Features

### 📈 College Placement Predictor
- Predicts expected CTC using college and placement-related features.
- Uses NIRF ranking and historical placement statistics.
- Powered by a trained Scikit-learn model.

### 📄 AI Resume Analyzer
- Upload a resume in PDF format.
- Extracts and analyzes skills, education, and experience.
- Generates an AI-based resume score and improvement suggestions using Groq.

### 🎯 GATE Score Calculator
- Accepts GATE score and engineering branch.
- Recommends colleges based on available ranking and cutoff data.

### 🤖 AI Placement Chatbot
- Answers placement and college-related questions.
- Uses Groq LLM integration for conversational responses.
- Designed for questions around colleges, placements, rankings, and career decisions.

### 🔐 User Authentication
- User registration and login.
- JWT-based authentication using Flask-JWT-Extended.

### 🛠️ Admin Dashboard
- User and application management.
- Analytics and NIRF data management.
- Supports administrative workflows.

### 📊 NIRF Data Management
- Import and maintain college ranking and placement data.
- Uses real NIRF-related datasets for project analysis.

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      User / Admin    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Frontend Interface │
                    │ HTML / CSS / JS       │
                    │ Bootstrap 5           │
                    └──────────┬───────────┘
                               │
                         REST API / HTTP
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Flask Backend     │
                    │ Routes / Services    │
                    └───────┬───────┬──────┘
                            │       │
              ┌─────────────┘       └─────────────┐
              ▼                                   ▼
     ┌─────────────────┐                 ┌─────────────────┐
     │ Database Layer  │                 │ AI / ML Layer   │
     │ PostgreSQL /    │                 │ Scikit-learn    │
     │ SQLite          │                 │ Groq LLM        │
     └─────────────────┘                 └─────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Backend** | Python, Flask |
| **Frontend** | HTML, CSS, JavaScript, Bootstrap 5 |
| **Machine Learning** | Scikit-learn, Pandas, NumPy, SciPy |
| **Database** | SQLite, PostgreSQL |
| **AI / LLM** | Groq API |
| **Authentication** | Flask-JWT-Extended |
| **Migrations** | Flask-Migrate, Alembic |
| **API** | REST API, JSON |
| **Deployment** | Render / Heroku / PythonAnywhere |

---

## 📂 Project Structure

```text
placeiq/
│
├── app.py
├── models.py
├── config.py
├── extensions.py
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── placement.py
│   ├── resume.py
│   ├── gate.py
│   └── chatbot.py
│
├── migrations/
├── static/
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── placement.html
│   ├── resume.html
│   ├── gate.html
│   └── chatbot.html
│
├── indian-colleges-data/
├── college_ctc_model.pkl
├── nirf_top_200.csv
│
├── add_nirf_placement_data.py
├── add_real_nirf_data.py
├── train_real_model.py
├── estimate_placement.py
├── check_db_status.py
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Riteshkumarsingh1/placeiq.git
cd placeiq
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
FLASK_APP=app.py
FLASK_ENV=development

SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///placeiq.db

GROQ_API_KEY=your-groq-api-key
JWT_SECRET_KEY=your-jwt-secret-key
```

> 🔒 Never commit your `.env` file or API keys to GitHub.

### 5. Initialize Database

If migrations already exist:

```bash
flask db upgrade
```

For a new migration setup:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Load NIRF Data

```bash
python add_real_nirf_data.py
python add_nirf_placement_data.py
```

### 7. Run the Application

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

---

## 🧪 Feature Testing

### 1. Authentication
- Register a new account.
- Login with valid credentials.
- Verify JWT authentication.

### 2. Placement Predictor
- Select or enter college information.
- Submit the required features.
- Receive predicted placement/CTC information.

### 3. Resume Analyzer
- Upload a PDF resume.
- Allow the application to process the resume.
- Review the AI-generated score and suggestions.

### 4. GATE Calculator
- Enter GATE score.
- Select branch.
- View recommended colleges.

### 5. Chatbot
Example queries:

```text
Which college has the highest placement?

What is the average CTC at IIT Bombay?

Which IIT has the best CSE placements?
```

---

## 🧠 Machine Learning Workflow

```text
NIRF / Placement Data
        ↓
Data Cleaning
        ↓
Feature Engineering
        ↓
Model Training
        ↓
Scikit-learn Model
        ↓
Placement Prediction
        ↓
Application Dashboard
```

The trained model is stored as:

```text
college_ctc_model.pkl
```

---

## 🔐 Security

PlaceIQ uses several security-related practices:

- JWT-based authentication
- Environment variables for secrets
- `.gitignore` for sensitive files
- Database-backed user management
- API-based communication between frontend and backend

---

## 🌐 Deployment

The application can be deployed using platforms such as **Render, Heroku, or PythonAnywhere**.

For a production deployment, configure:

```env
DATABASE_URL=your-postgresql-connection-string
GROQ_API_KEY=your-groq-api-key
SECRET_KEY=your-production-secret
JWT_SECRET_KEY=your-production-jwt-secret
```

### Example Start Command

```bash
gunicorn app:app
```

> Deployment configuration may vary depending on the hosting platform and current project setup.

---

## 🐛 Common Issues

### `ModuleNotFoundError: No module named 'groq'`

```bash
pip install groq
```

### Database table does not exist

```bash
flask db upgrade
```

### Port 5000 already in use

Run the application on another port according to your Flask configuration.

### Groq API not working

Check that:

```env
GROQ_API_KEY=your-valid-api-key
```

is correctly configured in `.env`.

---

## 📸 Suggested Screenshots

For project documentation, add screenshots showing:

- Login / Registration
- Main Dashboard
- Placement Prediction
- Resume Analysis
- GATE Score Calculator
- AI Chatbot
- Admin Dashboard

Recommended folder:

```text
screenshots/
├── login.png
├── dashboard.png
├── placement.png
├── resume.png
├── gate.png
└── chatbot.png
```

---

## 📌 Future Improvements

- Improve placement prediction accuracy with additional features.
- Add more colleges and regularly updated datasets.
- Introduce advanced resume parsing and job matching.
- Add role-based admin permissions.
- Add automated model retraining.
- Improve chatbot responses using retrieval-augmented generation.
- Add monitoring and application logging.
- Add automated testing and CI/CD.

---

## 📚 Learning Outcomes

This project demonstrates practical experience with:

- Full-stack application development
- Flask backend development
- REST API design
- SQL and database integration
- JWT authentication
- Machine Learning model integration
- LLM/API integration
- Data preprocessing and visualization
- Deployment fundamentals
- Application workflow design

---

## 📜 License

This project is licensed under the **MIT License** and is intended for educational use.

---

## 👨‍💻 Author

**Ritesh Kumar Singh**

B.Tech — Data Science

> *“Empowering students with data-driven career insights.”*
