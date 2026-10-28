# ragflow工具
# 1. get_assistant_list: 获取所有聊天助手列表。
# 2. create_ask_delete: 创建会话，提问，完成后删除会话
import os

from dotenv import load_dotenv
from ragflow_sdk import RAGFlow, Chat

from utils.logger_utils import logger

load_dotenv(override=True)

# 创建ragflow的客户端对象
_ragflow_client = RAGFlow(
    base_url=os.getenv("RAGFLOW_API_URL"),
    api_key=os.getenv("RAGFLOW_API_KEY"),
)


# 1. get_assistant_list: 获取所有聊天助手列表。
def get_assistant_list():
    """
     获取ragflow服务中所有的聊天助手信息! 用于后续具体提问的筛选!
     返回格式: 助手名称:xxx , 描述: xx , 关联的知识库: x,x,x,x \n
             助手名称:xxx , 描述: xx , 关联的知识库: x,x,x,x \n
    """
    logger.info("==========获取聊天助手列表=============")

    try:
        # 得到所有聊天助手列表
        chat_list: list[Chat] = _ragflow_client.list_chats()

        # 如果没有，返回没有提示
        if not chat_list:
            return "没有一个可用的聊天助手"

        # 有，遍历每个助手对象，取出name/description/datasets ,并拼接成指定格式字符串
        result = ""
        for chat in chat_list:
            print(chat)
            name = chat.name
            description = chat.description
            datasets = chat.datasets
            dataset_names_str = ",".join([dataset["name"] for dataset in datasets])
            result += f"助手名称:{name} , 描述: {description} , 关联的知识库: {dataset_names_str} \n"

        logger.info(f"获取到助手列表：{result}")
        return result
    except Exception as e:
        return f"获取聊天助手列表失败：{str(e)}"






# 2. create_ask_delete: 创建会话，提问，完成后删除会话
def create_ask_delete(chat_name: str, query: str):


    """
         向指定的助手提问,并获取返回结果!
         参数 chat_name就是助手的名称,名称需要get_assistant_list查询和确认
             question是本次提问的问题
         返回结果就是提问的回答
    """

    logger.info(f"==========向ragflow提问, chat_name={chat_name}, query={query}=============")

    try:
        # 根据chat_name查询得到一个聊天助手对象
        chat_list: list[Chat] = _ragflow_client.list_chats(name=chat_name)
        # 如果没有，返回没有提示
        if not chat_list:
            return "没有一个可用的聊天助手"
        chat = chat_list[0]

        # 通过聊天助手创建一个会话
        session = chat.create_session(name="temp_session")

        # 通过会话来提问
        stream = session.ask(query,stream=True)

        # 读取返回的结果数据
        result = ""
        for chunk in stream:
            # print("===", chunk)
            result = chunk.content
        # 删除会话
        # chat.delete_sessions([session.id])
        logger.info(f"提问结果:{result}")
        # 返回结果
        return result
    except Exception as e:
        return f"向ragflow提问失败：{str(e)}"

if __name__ == '__main__':
    # get_assistant_list()
    create_ask_delete(chat_name="法律助手", query="列表2条重要的刑法规则")