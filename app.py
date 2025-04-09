
# GenAI Compliance Assistant - Streamlit App (Enhanced)

import streamlit as st
import openai
import pandas as pd
import fitz  # PyMuPDF for PDF text extraction
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import tempfile

openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...your-key...")

st.set_page_config(page_title="GenAI Compliance Assistant", layout="wide")
st.title("🔍 GenAI-Powered Compliance Assistant for Renewable Energy")

page = st.sidebar.radio("Choose a Module", [
    "📄 Generate Compliance Reports",
    "📚 Summarize Regulatory Circulars",
    "📝 Permit/License Generator",
    "📅 Compliance Calendar",
    "💬 Chat with Compliance Docs"
])

@st.cache_data
def extract_text_from_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

@st.cache_resource
def load_qa_chain(uploaded_pdf):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name
    loader = PyPDFLoader(tmp_path)
    docs = loader.load_and_split()
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4"),
        retriever=db.as_retriever()
    )
    return qa_chain

if page == "📄 Generate Compliance Reports":
    st.header("Auto-generate RPO or REC Reports")
    uploaded_log = st.file_uploader("Upload SCADA Log (CSV)", type=["csv"])
    if uploaded_log:
        df = pd.read_csv(uploaded_log)
        st.dataframe(df.head())
        prompt = f"Generate an RPO compliance summary report based on this SCADA data:\n{df.head().to_string()}"
        if st.button("Generate Report"):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            st.subheader("Generated Report")
            st.write(response['choices'][0]['message']['content'])

elif page == "📚 Summarize Regulatory Circulars":
    st.header("Summarize CERC/MNRE Circulars")
    uploaded_pdf = st.file_uploader("Upload a regulatory circular (PDF)", type=["pdf"])
    if uploaded_pdf:
        text = extract_text_from_pdf(uploaded_pdf)
        summary_prompt = f"Summarize this regulatory circular for asset managers:\n{text}"
        if st.button("Summarize Circular"):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            st.subheader("Summary")
            st.write(response['choices'][0]['message']['content'])

elif page == "📝 Permit/License Generator":
    st.header("Generate CEIG/Sync Requests")
    state = st.selectbox("Choose State", ["Gujarat", "Maharashtra", "Rajasthan"])
    asset_name = st.text_input("Asset Name")
    if st.button("Generate Permit Application"):
        permit_prompt = f"Generate a CEIG permit application for {asset_name} located in {state}."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": permit_prompt}]
        )
        st.subheader("Permit Application")
        st.write(response['choices'][0]['message']['content'])

elif page == "📅 Compliance Calendar":
    st.header("Compliance Deadlines")
    st.info("Upload your compliance tracker Excel to show upcoming tasks.")
    uploaded_xlsx = st.file_uploader("Upload Excel", type=["xlsx"])
    if uploaded_xlsx:
        df = pd.read_excel(uploaded_xlsx)
        st.dataframe(df)

elif page == "💬 Chat with Compliance Docs":
    st.header("Ask a question from the document corpus")
    uploaded_pdf = st.file_uploader("Upload a document (PDF)", type=["pdf"])
    question = st.text_input("Ask your question")
    if uploaded_pdf and question:
        qa_chain = load_qa_chain(uploaded_pdf)
        if st.button("Get Answer"):
            answer = qa_chain.run(question)
            st.subheader("Answer")
            st.write(answer)
