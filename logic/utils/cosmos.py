###############################################################################
# Imports
###############################################################################
import os
import uuid


###############################################################################
# Functions
###############################################################################
# Check if File exists in CosmosDB
def is_file_in_cosmos(filename: str, container_client) -> bool:
    
    # Query for filename
    query = f"SELECT * FROM c WHERE c.filename = '{filename}'"
    results = list(container_client.query_items(
        query,
        enable_cross_partition_query=True
    ))
    
    # If filename exists in table
    if results:
        return True
    else:
        return False

# Add File to CosmosDB
def add_filename_to_cosmos(filename: str, container_client) -> bool:
    
    # Generate UUID
    random_id = str(uuid.uuid4())
    
    # Check if the random ID already exists in the container
    id_exists = True
    while(id_exists):
        query = f"SELECT * FROM c WHERE c.id = '{random_id}'"
        results = list(container_client.query_items(
            query,
            enable_cross_partition_query=True
        ))
        if not results:
            id_exists = False
        else:
            random_id = str(uuid.uuid4())
    
    # Add Filename to Container
    container_client.upsert_item(body={
        'id': random_id,
        'filename': filename
    })
    
    # return success
    return True