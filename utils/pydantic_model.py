from langchain_core.pydantic_v1 import BaseModel, Field

class GradeReWrite(BaseModel):
    """Viết lại câu hỏi của người dùng dựa trên câu hỏi và lịch sử."""
    rewrite: str = Field(description="Viết lại câu hỏi của người dùng dựa vào câu hỏi và lịch sử")