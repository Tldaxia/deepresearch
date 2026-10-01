import os  # 读取系统环境变量，例如从 .env 加载后的 LLM_API_KEY。
from dataclasses import dataclass  # 提供简洁的数据类，用来把几项配置打包成一个对象。
from pathlib import Path  # 用跨平台的方式拼接和解析文件路径。

from dotenv import load_dotenv  # 从 .env 文件读取 KEY=VALUE 配置，并放入环境变量。

# 始终读取 config.py 文件所在目录下的 .env 文件
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

@dataclass(frozen=True)
class LLMConfig:
    """保存调用大模型所需的配置参数。"""

    api_key: str
    base_url: str
    model_name: str

def load_llm_config() -> LLMConfig:
    """从环境变量中读取大模型配置参数，并返回 LLMConfig 实例。"""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    model_name = os.getenv("LLM_MODEL_NAME", "").strip()

    # 列表推导式的用法，
    # 逐项检查配置是否为空；最后得到的 missing 是“缺少配置名”的列表。
    missing = [
        name  # 把缺少的配置变量名称放进结果列表。
        for name, value in [  # 依次遍历每一组“变量名、读取到的值”。
            ("LLM_API_KEY", api_key),  # API 密钥的环境变量名及其值。
            ("LLM_BASE_URL", base_url),  # 百炼兼容接口地址的变量名及其值。
            ("LLM_MODEL_NAME", model_name),  # 模型名称的变量名及其值。
        ]
        if not value  # 只保留值为空字符串的配置项。
    ]

    if missing:
        raise ValueError(
            f"缺少必要的环境变量: {', '.join(missing)}。请检查 .env 文件或系统环境变量。"
        )

    return LLMConfig(api_key=api_key, base_url=base_url, model_name=model_name)
