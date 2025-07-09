# Azure AI Search Plugin
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from semantic_kernel.functions import kernel_function
import os
import dotenv
dotenv.load_dotenv()


class AISearchPlugin:
    def __init__(self):
        service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
        index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
        key = os.environ["AZURE_SEARCH_API_KEY"]

        self.search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))


    @kernel_function(description="Search ERP data")
    def search(self, query: str):
        return self.search_client.search(query)