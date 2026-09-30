"""最小 FastAPI 应用：里程碑 1 健康检查。"""

from fastapi import FastAPI # 导入fastapi

app = FastAPI(title="自动化深度研究智能体") # 创建fastapi实例

# 用于测试服务是否正常
@app.get("/healthz")
def health_check() -> dict[str, str]:
    """返回服务健康状态。"""
    return {"status": "ok"}
