from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents.runtime import InProcessRuntime
from plugins.AISearchPlugin import AISearchPlugin
import os
import dotenv

dotenv.load_dotenv()

class CddAgent:
    def __init__(self, source_erp: str, target_erp: str, additional_context: str = ""):
        self.source_erp = source_erp
        self.target_erp = target_erp
        self.additional_context = additional_context
        self.search_plugin = AISearchPlugin()
        self.runtime = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the CDD agent with specific instructions for ERP data conversion"""
        instructions = f"""You are a CDD (Cross-System Data Dictionary) specialist expert in converting data between ERP systems.

Your task is to help convert data from {self.source_erp} ERP to {self.target_erp} ERP.

Key responsibilities:
1. Search through historical CDD documentation for {self.source_erp} and {self.target_erp} systems
2. Analyze the data mapping requirements between source and target systems
3. Provide detailed field mapping recommendations
4. Suggest data transformation rules where needed
5. Identify potential data quality issues or incompatibilities

Additional context for this conversion:
{self.additional_context}

Always use the erp_search function to find relevant historical CDD data before providing recommendations.
Be specific about field names, data types, and transformation logic.
"""

        self.agent = ChatCompletionAgent(
            name="CDDAgent",
            description="A specialized agent for ERP data conversion and CDD documentation",
            instructions=instructions,
            service=AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL_ID"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            ),
            plugins=[self.search_plugin]
        )
    
    async def start_runtime(self):
        """Start the agent runtime"""
        if not self.runtime:
            self.runtime = InProcessRuntime()
            self.runtime.start()
    
    async def stop_runtime(self):
        """Stop the agent runtime"""
        if self.runtime:
            await self.runtime.stop_when_idle()
            self.runtime = None
    
    async def process_query(self, query: str):
        """Process a user query through the CDD agent"""
        from semantic_kernel.agents import GroupChatOrchestration, RoundRobinGroupChatManager
        
        if not self.runtime:
            await self.start_runtime()
        
        if not self.agent or not self.runtime:
            return "Error: Agent or runtime not properly initialized"
        
        # Enhanced query with ERP context
        enhanced_query = f"""
        Source ERP: {self.source_erp}
        Target ERP: {self.target_erp}
        Query: {query}
        
        Please search for relevant CDD documentation and provide specific mapping recommendations.
        """
        
        # Create a simple orchestration with just the CDD agent
        orchestration = GroupChatOrchestration(
            members=[self.agent],
            manager=RoundRobinGroupChatManager(max_rounds=1),
        )
        
        result = await orchestration.invoke(task=enhanced_query, runtime=self.runtime)
        response = await result.get()
        
        # Extract just the text content from the response
        if isinstance(response, list):
            if len(response) > 0:
                last_message = response[-1]
                if hasattr(last_message, 'content'):
                    return str(last_message.content)
                else:
                    return str(last_message)
            else:
                return "No response received"
        elif isinstance(response, str):
            return response
        else:
            # Try to get content attribute for other object types
            content = getattr(response, 'content', None)
            if content is not None:
                return str(content)
            return str(response)
    
    def update_context(self, source_erp: str, target_erp: str, additional_context: str):
        """Update the agent context with new ERP systems and additional info"""
        self.source_erp = source_erp
        self.target_erp = target_erp
        self.additional_context = additional_context
        self._initialize_agent() 