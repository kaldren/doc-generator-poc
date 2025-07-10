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
        instructions = f"""
        You are a CDD (Conversion Design Document) specialist with expertise in ERP data conversion and in writing Conversion Design Documents.

        Your task is to produce a formal CDD document for migrating data from **{self.source_erp}** ERP to **{self.target_erp}** ERP.

        Use the Key responsibilities to guide your work, but make it look like a formal CDD document.

        Key responsibilities:
        1. Use historical CDD documentation for {self.source_erp} and {self.target_erp} to inform mappings.
        2. Analyze and document the data mapping between source and target tables.
        3. Define all transformation rules (prefixes, formatting, concatenation, etc.).
        4. Identify potential data quality risks or constraints.
        5. At the end, include a section of notes **based on insights extracted from the strategy document and the source/target ERP field definitions**. These may include:
        - Formatting requirements
        - Mandatory fields or exclusions
        - Default values, constraints, or transformation side-effects
        - Anything that would impact the conversion process

        Always use the `erp_search()` function to retrieve relevant historical CDDs before responding.
        Focus on clarity, accuracy, and domain-appropriate terminology.

        The CDD must contain the following **five sections**, in this exact structure and order (you are allowed to add more before and after the sections if it will make it better):

        ---

        **Section 1: Source Table Structure**

        | Column Name   | Data Type     | Required | Description                   | Sample Data          |
        |---------------|---------------|----------|-------------------------------|----------------------|
        | ...           | ...           | ...      | ...                           | ...                  |

        ---

        **Section 2: Target Table Structure**

        | Column Name     | Data Type     | Required | Constraints / Business Rules                | Sample Data        |
        |-----------------|---------------|----------|---------------------------------------------|--------------------|
        | ...             | ...           | ...      | ...                                         | ...                |

        ---

        **Section 3: Field Mapping Summary**

        | Source Field   | Target Field     | Transformation Logic                          | Notes                        |
        |----------------|------------------|-----------------------------------------------|------------------------------|
        | ...            | ...              | ...                                           | ...                          |

        ---

        **Section 4: Final Sample Transformed Output**

        | AccountNumber   | Supplier        | ContactName     | ContactEmail            | ContactPhone     | Changes applied |
        |-----------------|-----------------|------------------|--------------------------|------------------|------------------|
        | ...             | ...             | ...              | ...                      | ...              |

        ---

        The tables above are just examples. Build the tables based on the strategy document and the source/target ERP field definitions.
        Also, for Changes applied provide a summary of all the changes applied to the data. If there are no changes, just say "N/A".

        **Section 5: Notes**

        Use this section to provide any additional notes or insights that are not covered in the other sections but are part of the strategy document and the source/target ERP data. If you don't have any, just say "N/A".

        Use your understanding of what a CDD is and what it should contain to provide additional insights and notes. But never make up any information or add any information that is not part of the strategy document or the source/target ERP data.
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