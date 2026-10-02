# OpenAI SDK 用于调用兼容 OpenAI 接口的千问服务。
from openai import OpenAI

# 读取项目已有的千问配置，不需要再创建一套配置。
from config import load_llm_config


def summarize_task(
    task_title: str,
    query: str,
    search_results: list[dict[str, str]],
) -> str:
    """根据某个研究任务的网页搜索摘要，生成有来源依据的小结。"""

    # 没有搜索结果时不调用模型，直接返回明确提示。
    if not search_results:
        return "没有找到可用于总结的搜索资料。"

    # 把标题、摘要和链接整理成文本，供千问阅读。
    source_text = "\n\n".join(
        (
            f"[来源{index}] {result['title']}\n"
            f"链接：{result['url']}\n"
            f"搜索摘要：{result['snippet']}"
        )
        for index, result in enumerate(search_results, start=1)
    )

    # 读取已有的模型配置，并创建千问客户端。
    config = load_llm_config()
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    # 请求千问仅根据提供的搜索资料撰写小结，并标注来源编号。
    response = client.chat.completions.create(
        model=config.model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一名研究助理。请只依据用户提供的搜索资料，"
                    "为研究任务写一段简洁、准确的小结。"
                    "重要结论后标注对应来源编号，例如[来源1]。"
                    "资料没有说明的内容不要自行补充；资料不足时明确说明。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"研究任务：{task_title}\n"
                    f"搜索问题：{query}\n\n"
                    f"搜索资料：\n{source_text}"
                ),
            },
        ],
    )

    # 取出千问返回的小结正文。
    summary = response.choices[0].message.content

    # 防止模型没有返回正文，避免把空内容当成成功结果。
    if not summary or not summary.strip():
        raise ValueError("千问没有返回研究小结。")

    return summary.strip()