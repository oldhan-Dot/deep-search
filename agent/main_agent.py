# [核心] 智能体组装与执行逻辑
from deepagents import create_deep_agent

from agent.llm import llm
from agent.load_prompt import main_config
from agent.sub_agents.db_sub_agent import db_agent
from agent.sub_agents.internet_sub_agent import internet_agent
from agent.sub_agents.rag_sub_agent import rag_agent

main_agent = create_deep_agent(
        model = llm,
        system_prompt=main_config["system_prompt"],
        subagents=[db_agent,internet_agent,rag_agent]
)
