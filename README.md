# 🔍 JD Resume Analyzer

**Build your personal resume database from job descriptions.**

Paste any job description → auto-extract structured fields → visualize skill trends.

No LLMs, no API keys, no external services. Pure Python keyword matching.

---

## ✨ Features

| | |
|---|---|
| 📥 **One-click paste** | Drop a JD and get structured data instantly |
| 🗃️ **Local database** | All data stored in a portable Excel file |
| 📊 **Interactive dashboard** | Filter, visualize, and explore your collection |
| 📈 **Skill analytics** | Top languages, ML frameworks, cloud tools, and more |
| 🏷️ **Smart extraction** | Recognizes 200+ skills, tools, conferences, and certifications |
| 📤 **CSV export** | Download filtered data anytime |

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the dashboard
streamlit run dashboard.py

# 3. Open in browser
#    → http://localhost:8501
```

---

## 🖥️ Dashboard

After launching, you'll see:

- **Paste box** — drop a JD, auto-extract, edit, and save
- **Filters** — by job category and date range
- **KPI cards** — record count, companies, cities, categories
- **Charts** — category distribution, top skills, word cloud, and more
- **Data table** — full records with CSV download

### Supported extractions

| Field | Example |
|-------|---------|
| Job Title | Senior NLP Engineer |
| Category | Algorithm Engineering / AI Agent / Development / Data |
| Company | DeepSeek, ByteDance, Tesla |
| Industry | Technology, Finance, Healthcare, FMCG |
| Location | Beijing / Shanghai / Remote |
| Core Knowledge | LLM, recommendation systems, NLP, CV |
| Programming | Python, C++, Go, TypeScript, SQL |
| Big Data Tools | Spark, Flink, Kafka, Hive |
| ML Frameworks | PyTorch, TensorFlow, LangChain |
| Cloud / DevOps | Docker, K8s, AWS, GCP |
| AI Coding Tools | Claude Code, Cursor, Copilot |
| Credentials | NeurIPS, ACL, KDD, CTF, PMP, CFA |

---

## 🧰 CLI Tool

```bash
# Extract and preview a JD from a text file
python -m jd_analyzer.cli extract sample.txt

# Add a record directly from JSON
python -m jd_analyzer.cli add '{"job_title": "...", ...}'

# List all records
python -m jd_analyzer.cli list

# Delete a record
python -m jd_analyzer.cli delete 3
```

---

## 📁 Project Structure

```
jd-resume-analyzer/
├── dashboard.py              # Streamlit web dashboard
├── requirements.txt          # Python dependencies
├── README.md
├── LICENSE
├── .gitignore
├── examples/
│   └── sample_jd.txt         # Sample job description for testing
├── data/                     # Created on first run
│   └── jd_records.xlsx       # Your resume database
└── jd_analyzer/
    ├── __init__.py
    ├── database.py            # Excel CRUD operations
    ├── extractor.py           # Keyword-based JD field extractor
    └── cli.py                 # Command-line tools
```

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — interactive dashboard
- **Pandas + openpyxl** — Excel database
- **Plotly** — interactive charts
- **WordCloud + matplotlib** — word clouds

---

## 💡 Why?

> "Every job posting is a signal about what the market needs."

Build a personal database to:
- Track skill demand over time
- Identify gaps in your own resume
- Spot industry trends at a glance
- Prepare smarter for interviews

---

## 📄 License

MIT — use freely, fork, and share.
