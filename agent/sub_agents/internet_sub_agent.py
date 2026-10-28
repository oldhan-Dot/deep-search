# 网络查询助手子 agent
from agent.load_prompt import sub_agents_config
from tools.internet_search_tool import internet_search

internet_agent = {
    "name":sub_agents_config["tavily"]["name"],
    "description":sub_agents_config["tavily"]["description"],
    "system_prompt": sub_agents_config["tavily"]["system_prompt"],
    "tools":[internet_search]
}