"""最小 FastAPI 应用：里程碑 1 健康检查。"""

from fastapi import FastAPI # 导入fastapi
from models import ResearchRequest, ResearchResponse, TodoItem # 导入模型类

app = FastAPI(title="自动化深度研究智能体") # 创建fastapi实例

# 用于测试服务是否正常
@app.get("/healthz")
def health_check() -> dict[str, str]:
    """返回服务健康状态。"""
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
def run_research(request:ResearchRequest) -> ResearchResponse:
    """处理研究请求，返回研究结果。"""
    return ResearchResponse(
        report_markdown=f"# 研究主题：{request.topic}\n\n这是一个自动生成的研究报告,用于验证前后端 API 的交互是否正常。",
        todo_items=[
            TodoItem(
                id="task-1",
                title=f"梳理 {request.topic} 相关的研究文献",
                status="completed",
                summary="这是固定的示例摘要，用于验证前后端 API 的交互是否正常。",
            )
        ],
    )
