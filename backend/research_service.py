from openai import BadRequestError

from models import ResearchResponse, ResearchSource
from planner import create_fallback_task, generate_plan_text, parse_plan_text
from searcher import search_web
from summarizer import summarize_task


def conduct_research(topic: str) -> ResearchResponse:
    """按规划、搜索、总结的顺序完成研究并生成报告。"""
    plan_text = generate_plan_text(topic)

    try:
        todo_items = parse_plan_text(plan_text)
    except ValueError:
        todo_items = [create_fallback_task(topic)]

    report_lines = [
        f"# 研究主题：{topic}",
        "",
        "## 研究任务与搜索结果",
        "",
    ]

    for task in todo_items:
        query = task.query if task.query else task.title
        results = search_web(query, max_results=3)

        task.sources = [ResearchSource(**result) for result in results]

        try:
            task.summary = summarize_task(task.title, query, results)
        except BadRequestError as error:
            body = error.body
            details = body.get("error", {}) if isinstance(body, dict) else {}
            error_code = details.get("code") if isinstance(details, dict) else None

            if error_code != "data_inspection_failed":
                raise

            task.summary = "千问的内容安全审核拦截了这组输入，未能生成小结。"
            task.status = "failed"
        else:
            task.status = "completed"

        report_lines.extend([
            f"### 任务：{task.title}",
            f"**搜索词**：{query}",
            "",
        ])

        if not results:
            report_lines.extend(["没有找到相关结果。", ""])

        for index, result in enumerate(results, start=1):
            report_lines.extend([
                f"{index}. [{result['title']}]({result['url']})",
                f"   - 摘要：{result['snippet']}",
                "",
            ])

        report_lines.extend([
            "#### 研究小结",
            task.summary,
            "",
        ])

    report = "\n".join(report_lines)
    return ResearchResponse(report_markdown=report, todo_items=todo_items)