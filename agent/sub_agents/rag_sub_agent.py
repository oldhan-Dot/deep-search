# ragflow 助手子 agent
# 网络查询助手子 agent
from agent.load_prompt import sub_agents_config

rag_agent = {
    "name":sub_agents_config["ragflow"]["name"],
    "description":sub_agents_config["ragflow"]["description"],
    "system_prompt": sub_agents_config["ragflow"]["system_prompt"],
    "tools":[]
}