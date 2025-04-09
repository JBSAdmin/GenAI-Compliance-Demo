# ⚡ GenAI Compliance Assistant for Renewable Energy

This is a reference demo app that showcases how Generative AI (via OpenAI GPT-4) can support compliance automation for Indian Renewable Energy Generation companies.

## 🧰 Features

- 🔄 Auto-generate RPO/REC compliance reports from SCADA logs
- 📚 Summarize regulatory circulars (MNRE/CERC) from uploaded PDFs
- 📝 Generate CEIG/grid sync requests via GenAI
- 📅 Visualize compliance deadlines via Excel tracker
- 💬 Chat with uploaded documents using LangChain + FAISS

## 🏗️ Tech Stack

- Python + Streamlit
- Azure OpenAI (GPT-4)
- LangChain + FAISS
- PyMuPDF for PDF parsing
- Azure-ready deployment via App Services

## 🚀 Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Deploying on Azure App Services

1. Create an App Service (Linux, Python 3.10+).
2. Upload the code.
3. Set the startup command to:

```bash
bash startup.sh
```

4. Set the application setting:

```
OPENAI_API_KEY = <your-key>
```

---

Maintained by JBS. For questions, reach out to the Data & AI team.