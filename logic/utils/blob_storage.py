###############################################################################
# Imports
###############################################################################
from azure.storage.blob import BlobServiceClient

###############################################################################
# Functions
###############################################################################
def list_files_in_container(conn_str: str, container_name: str):
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # List all blobs in the container
    blob_list = container_client.list_blobs()

    # Return a list of blob names
    return [blob.name for blob in blob_list]