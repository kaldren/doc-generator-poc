from azure.search.documents import SearchClient
from semantic_kernel.agents import Agent, ChatCompletionAgent, GroupChatOrchestration, RoundRobinGroupChatManager
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents.runtime import InProcessRuntime
from plugins.AISearchPlugin import AISearchPlugin
from semantic_kernel.contents import ChatMessageContent

import os
import dotenv
import asyncio
dotenv.load_dotenv()

def agent_response_callback(message: ChatMessageContent) -> None:
    """Observer function to print the messages from the agents."""
    print(f"**{message.name}**\n{message.content}")

def get_agents() -> list[Agent]:
    """Return a list of agents that will participate in the group chat"""

    search_plugin = AISearchPlugin()

    source_agent =  ChatCompletionAgent(
        name="SourceAgent",
        description="A source agent that can answer questions about the source ERP data",
        instructions="Search ERP data for the given query",
        service=AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL_ID"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        ),
        plugins=[search_plugin]
    )

    target_agent =  ChatCompletionAgent(
        name="TargetAgent",
        description="A target agent that can answer questions about the target ERP data",
        instructions="Search ERP data for the given query",
        service=AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL_ID"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        ),
        plugins=[search_plugin]
    )

    return [source_agent, target_agent]

async def main():

    agents = get_agents()

    group_chat_orchestration = GroupChatOrchestration(
        members=agents,
        # max_rounds is odd, so that the writer gets the last round
        manager=RoundRobinGroupChatManager(max_rounds=15),
        agent_response_callback=agent_response_callback,
    )


    # 2. Create a runtime and start it
    runtime = InProcessRuntime()
    runtime.start()

    # 3. Invoke the orchestration with a task and the runtime
    orchestration_result = await group_chat_orchestration.invoke(
        task="Create a slogan for a new electric SUV that is affordable and fun to drive.",
        runtime=runtime,
    )

    # 4. Wait for the results
    value = await orchestration_result.get()
    print(f"***** Result *****\n{value}")

    # 5. Stop the runtime after the invocation is complete
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())