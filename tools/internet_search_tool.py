# 搜索工具
import os
from typing import Literal

from dotenv import load_dotenv
from tavily import TavilyClient

from utils.logger_utils import logger

load_dotenv()


tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))

#网络搜索工具
def internet_search(
        query: str,  # 提问
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
):
    """使用Tavily进行网络搜索"""
    logger.info(f"=====执行internet_search工具 query={query}=======")
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )