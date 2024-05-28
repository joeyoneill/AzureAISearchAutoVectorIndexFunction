# Imports
import os
import sys
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

###############################################################################
# Create Vector Search Index
###############################################################################
def create_user_search_index(unique_id: str):
    try:
        # Get Azure Search Client
        search_client = SearchIndexClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
        )

        # Initialize AI Search Index w/ vector search
        index = SearchIndex(
            name=unique_id,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(name="content", type=SearchFieldDataType.String, searchable=True),
                SimpleField(name="metadata", type=SearchFieldDataType.String, searchable=True),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name=f'{unique_id}-vector-config'
                )
            ],
            vector_search = VectorSearch(
                profiles=[VectorSearchProfile(
                    name=f'{unique_id}-vector-config',
                    algorithm_configuration_name=f'{unique_id}-algorithms-config'
                )],
                algorithms=[HnswAlgorithmConfiguration(name=f'{unique_id}-algorithms-config')],
            )
        )

        # Create AI Search Index
        search_client.create_index(index)
        
        # Return Success
        return True
    except:
        return False


###############################################################################
# Main Run Logic
###############################################################################
def main():
    if len(sys.argv) != 2:
        print("Usage: python .\\create_vector_index.py \"INDEX_NAME_HERE\"")
        sys.exit(1)
    
    # Get Index Name
    index_name = sys.argv[1]
    
    # Create Index
    create_user_search_index(index_name)

if __name__ == "__main__":
    main()