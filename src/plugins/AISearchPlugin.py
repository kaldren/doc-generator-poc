# Azure AI Search Plugin
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents._generated.models import VectorQuery, VectorizedQuery
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import logger
from semantic_kernel.functions import kernel_function
from azure.search.documents.aio import SearchClient
import os
import dotenv
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

dotenv.load_dotenv()


class AISearchPlugin:
    def __init__(self):
        service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
        index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
        key = os.environ["AZURE_SEARCH_API_KEY"]

        embedding_settings = {
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "deployment_name": os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_ID")
        }

        self.search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
        self.azure_embedding = AzureTextEmbedding.from_dict(embedding_settings)

    async def embed_query(self, query: str):
        result = await self.azure_embedding.generate_embeddings([query])
        return result[0]


    @kernel_function(name="erp_search", description="Use this function to search for anything related to ERP queries")
    async def search(self, query: str):
        logger.info(f"Searching for {query}")

        service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        key = os.getenv("AZURE_SEARCH_API_KEY")

        # 1) get embedding
        raw_vec = await self.embed_query(query)
        vec = raw_vec.tolist()

        # 2) build the vector query
        vq = VectorizedQuery(vector=vec, k_nearest_neighbors=3, fields="text_vector")

        async with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            paged = await search_client.search(
                search_text=query,
                vector_queries=[vq],
                select=["chunk"],
                top=3,
            )

            # 4) now you can `async for` over it
            chunks = []
            async for doc in paged:
                chunks.append(doc["chunk"])

            # 5) return the big string
            return "\n".join(chunks)