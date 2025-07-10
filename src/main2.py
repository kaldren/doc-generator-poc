import asyncio
import logging

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

from plugins.AISearchPlugin import AISearchPlugin

import os
import dotenv

dotenv.load_dotenv()

async def main():
    kernel = Kernel()

    chat_completion = AzureChatCompletion(
        deployment_name=os.environ["AZURE_OPENAI_CHAT_MODEL_ID"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    kernel.add_service(chat_completion)

    setup_logging()
    logging.getLogger("kernel").setLevel(logging.DEBUG)

    kernel.add_plugin(AISearchPlugin(), plugin_name="AISearchPlugin")

    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()

    userInput = None

    while True:

        userInput = input("User > ")

        if userInput == "exit":
            break

        history.add_user_message(userInput)

        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )

        print("Assistant > " + str(result))

        history.add_assistant_message(str(result))

        print("--------------------------------")

if __name__ == "__main__":
    asyncio.run(main())

