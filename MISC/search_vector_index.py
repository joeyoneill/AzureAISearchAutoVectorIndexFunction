###############################################################################
# Imports
###############################################################################
import os
import sys
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

###############################################################################
# Search Vector Index Function
###############################################################################
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

###############################################################################
# Main Run Logic
###############################################################################
def main():
    if len(sys.argv) != 2:
        print("Usage: python .\\search_vector_index.py \"ENTER_QUERY_HERE\"")
        sys.exit(1)
    
    # Get Query from CMD
    query = sys.argv[1]
    
    # Create Index
    results = search_vector_index(
        query=query,
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
    )
    
    print(results)

if __name__ == "__main__":
    main()