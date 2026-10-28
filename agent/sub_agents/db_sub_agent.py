# 数据库助手子 agent
from agent.load_prompt import sub_agents_config
from tools.mysql_tools import get_table_data, execute_sql_query, list_sql_tables

db_agent = {
    "name":sub_agents_config["db"]["name"],
    "description":sub_agents_config["db"]["description"],
    "system_prompt": sub_agents_config["db"]["system_prompt"],
    "tools":[list_sql_tables,get_table_data,execute_sql_query]
}