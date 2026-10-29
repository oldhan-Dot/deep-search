# [核心] 智能体组装与执行逻辑
import shutil
from pathlib import Path

from deepagents import create_deep_agent

from agent.llm import llm
from agent.load_prompt import main_config
from agent.sub_agents.db_sub_agent import db_agent
from agent.sub_agents.internet_sub_agent import internet_agent
from agent.sub_agents.rag_sub_agent import rag_agent
from api.context import set_thread_context, set_session_context, reset_session_context
from api.monitor import monitor
from tools.markdown_tools import generate_markdown
from tools.pdf_tools import convert_md_to_pdf
from tools.upload_file_read_tool import read_file_content
from utils.logger_utils import logger

main_agent = create_deep_agent(
        model = llm,
        system_prompt=main_config["system_prompt"],
        subagents=[db_agent,internet_agent,rag_agent],
        tools=[generate_markdown, convert_md_to_pdf, read_file_content],
)


# 向浏览器端报告当前执行的状态
def _report_agent_status(chunk):
        for key, value in chunk.items():
                # print(f"=={key}==")
                # print(value)
                if not value or "messages" not in value: continue
                message = value["messages"][-1]
                if key == "model":
                        if message.tool_calls:
                                for tool_call in message.tool_calls:
                                        # 区分子智能体和工具
                                        if tool_call["name"] == "task":
                                                # print(f"--准备调用子智能体{tool_call['args']['subagent_type']}, 参数：{tool_call['args']['description']}")
                                                monitor.report_assistant(tool_call['args']['subagent_type'],
                                                                         {"query": tool_call['args']['description']})
                                        else:  # 只有主智能体的工具才会进来，子智能体的工具不会进来
                                                # print(f"--智能体准备调用工具{tool_call['name']}, 参数：{tool_call['args']}")
                                                monitor.report_tool(tool_call['name'], tool_call['args'])
                        elif message.content:
                                # print(f"--智能体返回最终结果: {message.content}")
                                monitor.report_task_result(message.content)
                # elif key == "tools":
                #     if message.name == "task":
                #         print(f"--调用子智能体返回的结果为：{message.content}")
                #     else:
                #         print(f"--调用工具{message.name}返回的结果为：{message.content}")


# 异步流式运行主智能体的函数
async def run_deep_agent(query: str, thread_id: str):
        # 缓存thread_id和session_dir_str， 并将session_dir_str报告给浏览器
        thread_token = set_thread_context(thread_id)  # 缓存thread_id
        project_dir = Path(__file__).parents[1].resolve()  # 项目目录的path
        session_dir = project_dir / "output" / f"session_{thread_id}"  # 当前会话的目录的path
        session_dir.mkdir(parents=True, exist_ok=True)  # 如果目录不存在，创建出来
        session_dir_str = str(session_dir).replace("\\", "/")  # 会话目录的绝对对象
        session_token = set_session_context(session_dir_str)  # 缓存当前会话目录的绝对路径
        monitor.report_session_dir(session_dir_str)  # 向浏览器端报告创建了会话目录 =》 用于显示界面右侧的列表栏

        # 将已上传的文件拷贝到session目录
        upload_dir = project_dir / "upload" / f"session_{thread_id}"
        uploaded_file_info = ""
        if upload_dir.exists():
                # 读取upload_dir中的所有文件，得到所有文件的文件名
                file_names = [item.name for item in upload_dir.iterdir() if item.is_file()]
                uploaded_file_info = f"""
[已上传文件]：
	{"\n".join([f"  - {name}" for name in file_names])}
请优先使用工具读取并参考这些文件
"""
                # 遍历拷贝文件
                for name in file_names:
                        if not (session_dir / name).exists():
                                shutil.copy(upload_dir / name, session_dir / name)

        # 生成一个相对于项目目录的相对session目录
        relative_session_dir_str = str(session_dir.relative_to(project_dir)).replace("\\", "/")
        work_instruction = f"""
【工作环境指令】
[工作目录]：{relative_session_dir_str}

{uploaded_file_info}

[规则]：
    1. 新生成文件必须保存到工作目录：'{relative_session_dir_str}'
    2. 读取已上传的文件时，请直接将文件名作为 filename 参数传入（read_file_content）读取工具，不要带上任何目录前缀。
    3. 使用相对路径，禁止使用绝对路径
    4. 若存在上传文件，请先分析内容
    """
        logger.error(work_instruction)

        # 给提问补充一些关于工作区的提示词
        content = f"提问:{query},工作环境指令:{work_instruction}"

        try:
                # 异步流式运行主智能体
                astream_result = main_agent.astream(
                        {
                                "messages": [
                                        {"role": "user", "content": content}
                                ]
                        },
                        # config={
                        #     "configurable": {"thread_id": thread_id},  # 用于 MemorySaver 记忆上下文
                        # }
                )

                # 异步遍历流式结果
                async for chunk in astream_result:
                        # 向浏览器端报告当前执行的状态
                        _report_agent_status(chunk)
        except Exception as e:
                # 将错误信息报告给浏览器端
                monitor.report_error(f"智能处理失败：{str(e)}")
                raise
        finally:
                # 重置缓存的thread_id和session_dir_str
                reset_session_context(session_token, thread_token)


if __name__ == "__main__":
        result = main_agent.invoke({
                "messages": [
                        {"role": "user", "content": "打人犯法吗？"}
                ]
        })
        logger.info(result["messages"][-1].content)