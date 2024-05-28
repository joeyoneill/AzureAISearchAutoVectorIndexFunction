# Azure Function: Document Indexer

This Azure Function is designed to run hourly and automatically index documents from Azure Blob Storage into a vector index in Azure AI Search.

## Prerequisites
- Azure subscription
- Azure Blob Storage account
- Azure AI Search service
- Python 3.11 environment
- Azure Functions Core Tools

## Setup
1. Clone this repository to your local machine.
2. Install the required packages using pip:
```pip install -r requirements.txt```
3. Configure your Azure Function settings.
4. Deploy the Azure Function to Azure using Azure Functions Core Tools or your preferred deployment method.
5. Configure the function to run hourly using a timer trigger.

## Usage
- Upload documents to your Azure Blob Storage container.
- The Azure Function will trigger hourly and index the documents into the specified Azure AI Search index.

## Resources
- [Azure Blob Storage documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Azure AI Search documentation](https://docs.microsoft.com/en-us/azure/search/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
