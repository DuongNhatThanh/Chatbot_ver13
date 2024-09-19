from configs import SYSTEM_CONFIG
from utils import PROMPT_ROUTER, SeachingDecision


def decision_search_type(query: str) -> str: 
    """
    Arg:
        query: câu hỏi của người dùng
        history: lịch sử của người dùng
        Sử dụng LLM để  phân loại câu hỏi của người dùng thành 1 trong 3 loại: TEXT, ELS, SIMILARITY
    Return:
        trả về loại câu hỏi
    """
    llm_with_output = SYSTEM_CONFIG.load_rewrite_model().with_structured_output(SeachingDecision)
    type = llm_with_output.invoke(PROMPT_ROUTER.format(query=query)).type
    return type