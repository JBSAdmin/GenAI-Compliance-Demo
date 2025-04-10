# GenAI Compliance Assistant - Document QA Chatbot

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, CSVLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from pathlib import Path
import tempfile

st.set_page_config(page_title="GenAI Compliance QA Chatbot", layout="wide")
st.title("📚 Ask Compliance Questions from Uploaded Documents")

# Sidebar for API Key
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# File uploader
uploaded_files = st.file_uploader("Upload your compliance documents (PDF, DOCX, XLSX, CSV)", type=["pdf", "docx", "xlsx", "csv"], accept_multiple_files=True)

query = st.text_input("Ask your question about compliance:", placeholder="e.g., What is the RPO compliance status in Maharashtra?")

if uploaded_files and query and openai_api_key:
    all_docs = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for file in uploaded_files:
        suffix = Path(file.name).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            tmp_path = Path(tmp.name)

        if suffix == ".pdf":
            loader = PyPDFLoader(str(tmp_path))
        elif suffix == ".docx":
            loader = UnstructuredWordDocumentLoader(str(tmp_path))
        elif suffix == ".csv":
            loader = CSVLoader(str(tmp_path))
        elif suffix == ".xlsx":
            loader = UnstructuredExcelLoader(str(tmp_path))
        else:
            st.warning(f"Unsupported file type: {file.name}")
            continue

        docs = loader.load()
        split_docs = text_splitter.split_documents(docs)
        for doc in split_docs:
            doc.metadata["source"] = file.name
        all_docs.extend(split_docs)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = FAISS.from_documents(all_docs, embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=openai_api_key)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    with st.spinner("Searching documents..."):
        result = qa_chain({"query": query})
        st.subheader("Answer")
        st.write(result["result"])

        st.subheader("Referenced Documents")
        for doc in result["source_documents"]:
            st.markdown(f"- **{doc.metadata.get('source', 'Unknown')}**")
else:
    st.info("Please upload documents, enter your API key, and type a question to begin.")