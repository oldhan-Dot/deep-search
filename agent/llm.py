# LLM 初始化
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv(override=True)
llm = init_chat_model(
    model= "deepseek-flash",
    model_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

if __name__ == '__main__':
    result = llm.invoke("你好")
    print(result.content)