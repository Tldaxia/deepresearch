# 标准库 JSON 解析器：把模型返回的 JSON 文本转换成 Python 数据结构。
import json

# OpenAI SDK：这里用于连接兼容 OpenAI 接口的千问服务。
from openai import OpenAI

# 导入本项目的函数，从 backend/.env 读取模型 Key、地址和名称。
from config import load_llm_config

from models import TodoItem  # 导入数据模型类，用于表示研究子任务。

# 限制单次研究最多执行的子任务数量，避免搜索和模型调用过多。
MAX_TASKS = 5

# 输入研究主题，调用千问生成规划文本，并返回模型原始回答。
def generate_plan_text(topic: str) -> str:
    """调用千问生成研究规划，并返回它输出的原始文本。"""
    """调用大模型生成学习计划文本。"""
    # 读取并校验本地 .env 配置，包括 API Key、接口地址和模型名称。
    config = load_llm_config()
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    # 向模型发送聊天请求；system 说明它的角色和输出格式，user 给出研究主题。
    response = client.chat.completions.create(
        model=config.model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是研究规划助手。将用户主题拆分成3到5个互不重复、"
                    "适合搜索的研究子问题。只输出JSON，不要Markdown代码围栏或额外解释。"
                    "格式：{\"tasks\":[{\"title\":\"子问题标题\",\"query\":\"搜索问题\"}]}。"
                ),
            },
            {"role": "user", "content": topic},
        ],
    )

    # 从响应中取第一条回答的文本正文；若模型未返回文本，值可能是 None。
    plan_text = response.choices[0].message.content
    if not plan_text:
        raise ValueError("模型没有返回规划内容。请检查模型配置或输入主题。")

    return plan_text

# 输入模型返回的 JSON 文本，解析并取出 tasks 子任务列表。
def parse_plan_text(plan_text: str) -> list[dict[str, str]]:
    """把模型原始文本解析成任务列表，并检查外层数据结构。"""
    # 在模型返回的文本中查找第一个左花括号，JSON 前面可能有说明或 ```json 标记。
    json_start = plan_text.find("{")
    # find 找不到时返回 -1；这代表文本里没有可解析的 JSON 对象开头。
    if json_start == -1:
        raise ValueError("模型回答中没有找到 JSON 对象")

    try:
        # 从 JSON 开头解析；raw_decode 返回 (解析后的数据, 结束位置)。
        # 这里用 _ 接收并忽略结束位置，因为当前只需要解析后的数据。
        data, _ = json.JSONDecoder().raw_decode(plan_text[json_start:])
    except json.JSONDecodeError as error:
        # 如果花括号后面的内容不是合法 JSON，把底层错误改成更易懂的项目提示。
        # `from error` 保留原始错误原因，方便开发时排查。
        raise ValueError("模型返回的规划不是有效 JSON") from error

    if not isinstance(data, dict):
        raise ValueError("规划结果必须是 JSON 对象")

    tasks = data.get("tasks")  # 取出 tasks 字段；如果字段不存在，结果是 None。
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("规划结果必须包含非空的 tasks 列表")

    todo_items = []

    for index, task in enumerate(tasks[:MAX_TASKS], start=1):
        # 忽略不是 json 对象的任务项。
        if not isinstance(task, dict):
            continue

        title = task.get("title")
        query = task.get("query")

        # 标题和搜索问题必须是非空字符串，否则忽略该任务。
        if not isinstance(title, str) or not title.strip():
            continue
        if not isinstance(query, str) or not query.strip():
            continue

        # ID、状态和摘要由后端补齐；模型只负责提供标题和搜索问题。
        todo_items.append(
            TodoItem(
                id=f"task-{index}",
                title=title.strip(),
                query=query.strip(),
                status="pending",
                summary="",
            )
        )

    if not todo_items:
        raise ValueError("模型没有生成有效的任务列表。请检查模型配置或输入主题。")

    return todo_items

def create_fallback_task(topic: str) -> TodoItem:
    """模型规划不可用时，用原始主题创建一个默认任务。"""
    clean_topic = topic.strip()

    return TodoItem(
        id="task-1",
        title=f"研究主题：{clean_topic}",
        query=clean_topic,
        status="pending",
        summary="模型规划不可用，使用原始主题作为兜底任务。",
    )

# 仅当通过 `python planner.py` 直接运行时，才执行下面的命令行流程。
if __name__ == "__main__":
    topic = input("请输入研究主题：")  # 从终端读取用户输入的研究主题。
    plan_text = generate_plan_text(topic)  # 调用千问，取得原始规划文本。
    tasks = parse_plan_text(plan_text)  # 解析 JSON 并取得其中的 tasks 列表。
    print(tasks)  # 在终端显示解析后的 Python 列表，便于人工检查。
