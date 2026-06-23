# app/rag.py
import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import requests
from dotenv import load_dotenv

load_dotenv()

# Chemins
KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base"
FAISS_PATH = Path(__file__).parent.parent / "data" / "faiss_index"

# Variable globale pour le vectorstore
_vectorstore = None

def build_vectorstore():
    """Construit l'index FAISS depuis les documents."""
    global _vectorstore

    print("🔨 Construction de la base de connaissances RAG...")

    # Charger tous les fichiers txt
    documents = []
    for txt_file in KB_PATH.glob("*.txt"):
        loader = TextLoader(str(txt_file), encoding="utf-8")
        documents.extend(loader.load())

    # Découper en chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n===", "\n\n", "\n", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"   {len(chunks)} chunks créés")

    # Créer les embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Construire l'index FAISS
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(FAISS_PATH))
    _vectorstore = vectorstore

    print("✅ Index FAISS construit et sauvegardé !")
    return vectorstore

def get_vectorstore():
    """Charge ou construit le vectorstore."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    if FAISS_PATH.exists():
        _vectorstore = FAISS.load_local(
            str(FAISS_PATH),
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        _vectorstore = build_vectorstore()

    return _vectorstore

def answer_question(question: str, disease_context: str = "") -> str:
    """Répond à une question en cherchant dans la base de connaissances."""

    vectorstore = get_vectorstore()

    # Enrichir la question avec le contexte de la maladie
    query = f"{disease_context} {question}".strip()

    # Rechercher les documents pertinents
    docs = vectorstore.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Construire le prompt
    prompt = f"""Tu es un expert agronome tunisien. Réponds en français à la question de l'agriculteur.

Contexte tiré de la base de connaissances :
{context}

Question de l'agriculteur : {question}

Réponds de façon claire, pratique et adaptée au contexte tunisien. 
Si l'information n'est pas dans le contexte, dis-le honnêtement.
"""

    # Appel Groq
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.5
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Erreur : {response.text}"