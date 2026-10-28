# 加载 prompts.yaml 中的 prompt 配置
from pathlib import Path

import yaml


def load_yaml(file_path:str):
    with open(file_path,"r",encoding="utf-8") as f:
        return yaml.safe_load(f)

_yaml_path = Path(__file__).parents[1] /"prompt"/"prompts.yaml"
_yaml_dict = load_yaml(_yaml_path)

# 暴露主agent和subagents的配置
main_config = _yaml_dict["main_agent"]
sub_agents_config = _yaml_dict["sub_agents"]

if __name__ == '__main__':
    print(main_config)
    print(sub_agents_config)
