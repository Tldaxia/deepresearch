"""最小 FastAPI 应用：里程碑 1 健康检查。"""

from fastapi import FastAPI # 导入fastapi
from models import ResearchRequest, ResearchResponse
from research_service import conduct_research

app = FastAPI(title="自动化深度研究智能体") # 创建fastapi实例

# 用于测试服务是否正常
@app.get("/healthz")
def health_check() -> dict[str, str]:
    """返回服务健康状态。"""
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
def run_research(request: ResearchRequest) -> ResearchResponse:
    """接收研究请求，并委托研究服务完成业务流程。"""
    return conduct_research(request.topic)
