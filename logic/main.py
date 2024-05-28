# This Folder Contains Main Logic to be called in Function logic

# Imports
import os
import logging
import sys
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient, BlobClient

# In-App Dependencies
from logic.utils.blob_storage import list_files_in_container
from logic.utils.cosmos import is_file_in_cosmos, add_filename_to_cosmos
from logic.utils.ai_search import (
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
    save_text_to_vector_index
)

# Accepted file types
ok_file_types = ['.txt', '.pdf', '.docx']

# Main Function
def main():
    
    # Return List of Files from Blob Storage
    container_files = list_files_in_container(
        conn_str=os.getenv("AZURE_BLOB_CONN_STR"),
        container_name=os.getenv("AZURE_BLOB_CONTAINER")
    )
    
    # Get CosmosDB Container Client
    client = CosmosClient.from_connection_string(conn_str=os.getenv("COSMOS_CONN_STR"))
    database_client = client.get_database_client(os.getenv("COSMOS_DB_NAME"))
    container_client = database_client.get_container_client(os.getenv("COSMOS_FILENAMES_CONTAINER_NAME"))
    
    # Check if file exists in cosmos
    file_in_cosmos_bool_arr = []
    try:
        for filename in container_files:
            file_in_cosmos_bool_arr.append(
                is_file_in_cosmos(
                    filename=filename,
                    container_client=container_client
                )
            )
    except Exception as e:
        logging.error(f'ERROR IN CHECKING COSMOS FILES: {e}... EXITING...')
        sys.exit(1)
    
    # Ensure Lists are proper len
    if len(container_files) != len(file_in_cosmos_bool_arr):
        logging.error("ERROR: FILE ARRAYS LEN DO NOT MATCH... EXITING...")
        sys.exit(1)
    
    # Return List of NEW files in container
    files_for_index = [s for s, flag in zip(container_files, file_in_cosmos_bool_arr) if not flag]
    
    # Get Azure Blob Storage Client
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_CONN_STR"))
    
    # Iterate through files
    for filename in files_for_index:
        
        # Check File type
        # if not accepted file type, skip
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in ok_file_types:
            logging.info(f"NON-ACCEPTED FILE TYPE (.txt, .pdf, .docx): <filename> not indexed...")
            continue
        
        # Get Blob Client
        blob_client = blob_service_client.get_blob_client(
            container=os.getenv("AZURE_BLOB_CONTAINER"),
            blob=filename
        )
        
        # Download Blob Content as Bytes
        blob_data = blob_client.download_blob().readall()
        
        # extract text from file
        if file_extension == '.txt':
            file_text = extract_text_from_txt(blob_data)
        elif file_extension == '.docx':
            file_text = extract_text_from_docx(blob_data)
        elif file_extension == '.pdf':
            file_text = extract_text_from_pdf(blob_data)
        
        print(f'{filename}\n{file_text}\n\n')
        
        # Save File to index
        saved_to_index = save_text_to_vector_index(
            text=file_text,
            file_name=filename,
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
        )
        
        # If saved, save to cosmos
        if saved_to_index:
            add_filename_to_cosmos(
                filename=filename,
                container_client=container_client
            )
    
    return True