"""最小 FastAPI 应用：里程碑 1 健康检查。"""

from fastapi import FastAPI # 导入fastapi
from models import ResearchRequest, ResearchResponse # 导入数据模型类，用于表示研究请求和研究结果。
from planner import create_fallback_task, generate_plan_text, parse_plan_text # 导入规划器函数，用于生成研究规划和解析模型输出。

app = FastAPI(title="自动化深度研究智能体") # 创建fastapi实例

# 用于测试服务是否正常
@app.get("/healthz")
def health_check() -> dict[str, str]:
    """返回服务健康状态。"""
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
def run_research(request:ResearchRequest) -> ResearchResponse:
    # 调用千问生成规划文本，并解析出其中的 TodoItem 列表。
    plan_text = generate_plan_text(request.topic)

    try:
        todo_items = parse_plan_text(plan_text)
    except ValueError:
        todo_items = [create_fallback_task(request.topic)]

    # 报告暂时是模拟内容；后续里程碑再加入搜索和总结。
    report = (
        f"# 研究主题：{request.topic}\n\n"
        "研究计划已由千问生成，后续里程碑会加入搜索和总结功能。\n\n"
    )

    return ResearchResponse(report_markdown=report, todo_items=todo_items)
