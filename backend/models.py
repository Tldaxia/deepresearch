from pydantic import BaseModel, Field, field_validator

# 表示前端发给后端的研究请求，并定义请求字段及其校验规则。
class ResearchRequest(BaseModel):
    topic: str = Field(...,min_length=1, description="用户提交的研究主题")

    # 告诉 Pydantic：下面的方法用于校验 topic 字段；处理请求数据时会自动调用。
    @field_validator('topic')
    # 把下面的方法声明为类方法，所以第一个参数是 cls（类本身），不是 self（对象本身）。
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('研究主题不能为空')
        return value

# 表示研究计划中的一个子任务；后端会用它描述任务标题、状态和摘要。
class TodoItem(BaseModel):
    id: str
    title: str
    status: str
    summary: str = ""

# 表示后端返回给前端的研究结果，包含 Markdown 报告和子任务列表。
class ResearchResponse(BaseModel):
    report_markdown: str
    todo_items: list[TodoItem] = Field(default_factory=list)
