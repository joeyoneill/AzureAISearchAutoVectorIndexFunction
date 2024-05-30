###############################################################################
# Imports
###############################################################################
import os
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dataclasses import dataclass
from typing import List, Optional
import uuid

###############################################################################
# Functions
###############################################################################
# Extracts Text from .docx Files
def extract_text_from_docx(file_data):
    file_stream = BytesIO(file_data)
    doc = Document(file_stream)
    return "\n".join([para.text for para in doc.paragraphs])


# Extracts Text from .pdf Files
def extract_text_from_pdf(file_data):
    # init ret var
    text = ''
    
    # init file stream
    file_stream = BytesIO(file_data)
    
    # init pdf reader
    reader = PdfReader(file_stream)
    
    # Iterate through each page and concatenate its text
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # Check if text was extracted
            text += page_text + '\n'
    
    # Return pdf text
    return text


# Extracts Text from .txt Files
def extract_text_from_txt(file_data):
    return file_data.decode('utf-8')  # Assuming UTF-8 encoded text file


# Chunks and Embeds Text from Files and uploads to vector index store
# Stores chunks in Content Nodes and generates entities
def save_text_to_vector_index(text: str, file_name: str, index_name: str):
    
    # Use AzureOpenAIEmbeddings with an Azure account
    embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY"),
    )
    
    # Get Azure AI Search Vector Store Index Instance
    vector_store: AzureSearch = AzureSearch(
        azure_search_endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
        azure_search_key=os.getenv('AZURE_SEARCH_ADMIN_KEY'),
        index_name=index_name,
        embedding_function=embeddings.embed_query,
    )
    
    # Load Recursive Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Get Documents from Text
    docs = text_splitter.create_documents([text])
    
    # Update Document Metadata
    updated_metadata = {
        "source": f'/{index_name}/{file_name}',
        "container": index_name,
        "file_name": file_name,
    }
    for doc in docs:
        # Update Document Metadata
        doc.metadata = updated_metadata.copy()
    
    # Embed & Store Docs in Vector Store
    vector_store.add_documents(documents=docs)
    
    # Return Success
    return True


# Doc DataClass
@dataclass
class Doc:
    docId: Optional[str] = None
    docTitle: Optional[str] = None
    description: Optional[str] = None
    descriptionVector: Optional[List[float]] = None


# Saves to Index Created by Teams AI Setup
def save_to_index(text: str, file_name: str):
    
    # Use AzureOpenAIEmbeddings with an Azure account
    embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY"),
    )
    
    # Load Recursive Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Get Documents from Text
    docs = text_splitter.create_documents([text])
    
    # Embed the docs
    docs_content = [doc.page_content for doc in docs]
    embedded_docs = embeddings.embed_documents(docs_content)
    if (len(docs) != len(embedded_docs)):
        return False
    
    # Returns the filename without extension
    filename_wo_extenstion = os.path.splitext(file_name)[0].lower()
    
    # Generate Id
    random_id = str(uuid.uuid4())
    search_client = SearchClient(
        os.getenv("AZURE_SEARCH_ENDPOINT"),
        os.getenv("AZURE_SEARCH_INDEX_NAME"),
        AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
    )
    id_exists = True
    while id_exists:
        try:
            result = search_client.get_document(key=f"{random_id}_1")
        except:
            id_exists = False
            break
        random_id = str(uuid.uuid4())
        
    
    # Transform Docs
    transformed_docs = []
    for i, doc in enumerate(docs):
        temp_doc = {
            "docId": f'{random_id}_{i+1}',
            "docTitle": f'{filename_wo_extenstion}_{i}',
            "description": doc.page_content,
            "descriptionVector": embedded_docs[i]
        }
        transformed_docs.append(temp_doc)
    
    # Get Azure AI Search Credentials
    credentials = AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
    
    # Get AI Search Client
    search_client = SearchClient(
        os.getenv("AZURE_SEARCH_ENDPOINT"),
        os.getenv("AZURE_SEARCH_INDEX_NAME"),
        credentials
    )
    
    # Upsert Documents to AI Search
    search_client.merge_or_upload_documents(transformed_docs)
    
    # Return Success
    return True

# Returns the n most similar documents to a given query
def search_vector_index(query: str, index_name: str, n: int = 3):
    
    # Use AzureOpenAIEmbeddings with an Azure account
    embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY"),
    )
    
    # Get Azure AI Search Vector Store Index Instance
    vector_store: AzureSearch = AzureSearch(
        azure_search_endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
        azure_search_key=os.getenv('AZURE_SEARCH_ADMIN_KEY'),
        index_name=index_name,
        embedding_function=embeddings.embed_query,
    )
    
    # Perform a similarity search
    return vector_store.similarity_search(
        query=query,
        k=n,
        search_type="similarity",
    )