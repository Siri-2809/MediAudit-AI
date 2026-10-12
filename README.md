# MediAudit AI 🏥

**An Explainable AI-Based Medical Claims Auditing Prototype**

MediAudit AI is a medical claims auditing prototype that helps auditors identify unusual billing patterns, understand why a claim was flagged, and determine what evidence should be verified during an audit.

The system combines machine learning-based anomaly detection, transparent rule-based checks, and AI-generated explanations in an interactive dashboard.

> **Disclaimer:** MediAudit AI is a decision-support prototype. An anomaly or audit flag does not establish fraud or improper billing. All findings require human review and verification.

## 🚀 Features

- **CSV Claims Upload:** Upload a claims dataset through the dashboard to start a new audit.
- **Data Processing:** Handle missing values, prepare numerical and categorical fields, and derive useful features when the required columns are available.
- **Anomaly Detection:** Use Isolation Forest to identify claims with unusual characteristics compared with other claims in the dataset.
- **Rule-Based Audit Checks:** Apply transparent checks for potentially unusual payment amounts and other patterns supported by the available data.
- **Explainable Audit Findings:** Display the reasons for flagged claims and recommend what auditors should verify.
- **AI-Powered Explanations:** Use Google Gemini to generate natural-language explanations for individual claims.
- **Interactive Dashboard:** Browse claims, filter findings, view claim details, and inspect audit results.
- **Audit Report Export:** Download audit findings as a CSV report.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend processing and audit logic |
| Pandas & NumPy | Data preparation and numerical operations |
| Scikit-learn | Isolation Forest anomaly detection |
| FastAPI | Backend API |
| React | Frontend dashboard |
| Vite | Frontend development server |
| Google Gemini API | AI-generated claim explanations |
| Matplotlib | Data visualization |
| Git & GitHub | Version control |

## ⚙️ How It Works

1. **Upload:** The auditor uploads a medical claims CSV file.
2. **Preprocess:** The system reads the data, prepares suitable features, and derives additional fields where possible.
3. **Detect anomalies:** Isolation Forest identifies claims with unusual patterns.
4. **Apply audit rules:** Transparent checks identify records that meet configured audit conditions.
5. **Explain findings:** The system provides rule-based explanations and recommended verification steps. Gemini can provide additional natural-language explanations.
6. **Review and export:** The auditor examines the findings and exports the audit report.

```text
       Claims CSV
            |
            v
     Data Processing
            |
            v
    +------------------+
    |  Audit Analysis  |
    +------------------+
       /           \
      v             v
 Isolation       Audit Rules
  Forest             |
      \              /
       v            v
      Explainable Findings
               |
               v
      Gemini Explanations
               |
               v
       Auditor Dashboard
               |
               v
         CSV Audit Report
```

## 📂 Project Structure

```text
MediAudit-AI/
├── backend/
│   └── app/
│       ├── main.py
│       ├── data_processing.py
│       ├── anomaly_detection.py
│       ├── audit_rules.py
│       ├── explanations.py
│       ├── llm_explainer.py
│       └── report_generator.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── ...
├── data/
│   └── claims.csv
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

*The structure above highlights the main application files; other configuration and supporting files may also be present.*

## 📊 Dataset

The project uses the **CMS DE-SynPUF Sample 1 inpatient claims dataset**, a synthetic Medicare claims dataset.

The dataset provides claims-related information that can be used to explore unusual billing patterns and demonstrate medical claims auditing workflows.

The available columns determine which features and audit rules can be applied. For example, admission and discharge dates can be used to derive length of stay when both fields are available.

Because the dataset is synthetic and does not provide verified fraud labels for this prototype, the system identifies unusual claims for investigation rather than predicting confirmed fraud.

Place the default dataset at:

```text
data/claims.csv
```

Alternatively, upload a compatible CSV file through the dashboard.

## 💻 Installation and Setup

### Prerequisites

- Python 3.10 or a compatible Python version
- Node.js and npm
- Git
- A Google Gemini API key for AI-generated explanations

### 1. Clone the repository

```bash
git clone https://github.com/Siri-2809/MediAudit-AI.git
cd MediAudit-AI
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Set up the Python backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure the environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key.

**Security:** Never commit `.env` or expose your API key in frontend code or public repositories.

### 4. Start the backend

Run this command from the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually:

```text
http://localhost:5173
```

## 🔌 Backend API

The application exposes endpoints for claim analysis, browsing, explanations, uploads, and reporting.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/upload` | POST | Upload and analyze a claims CSV |
| `/api/summary` | GET | Retrieve audit summary statistics |
| `/api/claims` | GET | Retrieve claims for the dashboard |
| `/api/claims/{claim_id}` | GET | Retrieve claim details |
| `/api/report` | GET | Generate or download the audit report |
| `/api/claims/{claim_id}/ai-explanation` | GET | Request a Gemini-generated explanation |

For request and response details, start the backend and visit `/docs`.

## 🧠 Anomaly Detection and Audit Logic

### Isolation Forest

Isolation Forest is an unsupervised machine learning algorithm used to identify records that differ from typical observations.

In this project, it analyzes suitable numerical features from the claims data. The initial configuration uses a contamination parameter of `0.05`, which represents the model's assumed proportion of anomalies.

This setting is a modeling parameter, not an estimate of the actual fraud rate.

### Rule-Based Auditing

The system applies explicit checks to identify potentially unusual claim characteristics. Examples include:

- **HIGH_PAYMENT:** Payment exceeds a configured threshold.
- **NEGATIVE_PAYMENT:** A payment amount is negative.
- **ZERO_PAYMENT:** A payment amount is zero.
- **LONG_STAY:** The derived length of stay exceeds a configured threshold.
- **STAY_DAYS_MISMATCH:** Available stay-related fields disagree.

Rules are applied only where the relevant fields are available and suitable.

### Explainability

Each audit finding is intended to help the auditor understand:

- Which anomaly or audit rule was triggered.
- Which available claim fields support the finding.
- Why the pattern may deserve investigation.
- What supporting documents or claim details should be verified.

Gemini provides additional natural-language explanations; its output should be treated as assistance for human review, not as authoritative evidence.

## 📈 Expected Output

For an analyzed claims dataset, the dashboard helps the user:

- View an overview of audit findings.
- Browse individual claims and their relevant details.
- Identify records flagged by anomaly detection or audit rules.
- Review explanations and recommended verification steps.
- Request AI-generated explanations.
- Export findings for further review.

The exact results depend on the uploaded dataset, available columns, configured audit rules, and anomaly detection settings.

## 🔒 Data and Security Considerations

- Keep API keys in environment variables.
- Do not commit secrets, credentials, or sensitive claims data.
- Use synthetic or appropriately authorized data for demonstrations.
- Validate uploaded files before processing.
- Treat audit findings as candidates for review, not proof of fraud.

## 🔮 Future Improvements

Potential future enhancements include:

- More audit rules based on validated billing guidelines.
- Improved claim-level traceability and duplicate identifier handling.
- Additional visual analytics and report customization.
- Automated testing and stronger input validation.
- Evaluation against a verified, appropriately labeled dataset.

## 👩‍💻 Project Goal

MediAudit AI demonstrates how machine learning, transparent audit rules, and AI-generated explanations can support a more interpretable medical claims review workflow.

**The goal is to help auditors investigate unusual claims more efficiently while keeping the final decision with a human reviewer.**
