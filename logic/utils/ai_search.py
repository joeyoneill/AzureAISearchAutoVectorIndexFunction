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