import os
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from maikol_utils.print_utils import print_separator

from src.config import Configuration

def cargar_y_indexar(CONFIG: Configuration):
    embeddings = OllamaEmbeddings(model=CONFIG.rag_embedding_model)

    if os.path.exists(CONFIG.db_path):
        print_separator("Cargando base de datos existente...")
        return Chroma(persist_directory=CONFIG.db_path, embedding_function=embeddings)
    print_separator(f"Escaneando PDFs en {CONFIG.pdf_path}")
    
    # DirectoryLoader busca todos los archivos .pdf y usa PyPDFLoader para cada uno
    loader = DirectoryLoader(
        CONFIG.pdf_path,
        glob="./*.pdf",
        loader_cls=PyPDFLoader
    )
    
    docs = loader.load()
    print(f" - Documentos cargados: {len(docs)} páginas encontradas.")

    # Dividimos el texto en trozos
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    print(f" - Creando base de datos vectorial con {len(splits)} fragmentos...")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=CONFIG.db_path
    )
    return vectorstore

def ask_rag(transcription:str, CONFIG:Configuration) -> str:
    vectorstore = cargar_y_indexar(CONFIG)
    llm = OllamaLLM(model=CONFIG.rag_model_name)

    system_prompt = (
        "Eres un asistente de investigación. Responde basándote estrictamente en el contexto."
        "Además no devuelvas ningún formato de texto, devuelvelo todo en texto plano, como si lo estuvieses leyendo."
        "\n\n"
        "Contexto: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    chain = create_retrieval_chain(
        vectorstore.as_retriever(search_kwargs={"k": 10}), 
        create_stuff_documents_chain(llm, prompt)
    )

    print(" - Buscando en la biblioteca...")
    res = chain.invoke({"input": transcription})

    return res["answer"]