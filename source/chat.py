from typing import Dict, Tuple
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from source.retriever import get_context
from source.router import decision_search_type
from module_elastic import  search_db, classify_intent
from utils import (
    PROMPT_HEADER, PROMPT_HISTORY,
    GradeReWrite, timing_decorator
)
from logs.logger import set_logging_error, set_logging_terminal
from configs.config_system  import SYSTEM_CONFIG

logger_error = set_logging_error()    
logger_terminal = set_logging_terminal()
memory = ConversationBufferWindowMemory(memory_key="chat_history", k=3)


def get_history() -> str:
    history = memory.load_memory_variables({})
    return history['chat_history']

@timing_decorator
def rewrite_query(query: str, history: str) -> str: 
    
    """
    Sử dụng LLM để viết lại câu hỏi của người dùng thành 1 câu mới dựa vào lịch sử trước đó và câu hỏi hiện tại.

    Arg:
        - query: câu hỏi của người dùng
        - history: lịch sử của người dùng
    Return:
        - trả về câu hỏi được viết lại.
    """
    logger_terminal.info(f"Query User: {query}")

    llm_with_output = SYSTEM_CONFIG.load_rewrite_model().with_structured_output(GradeReWrite)
    query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
    logger_terminal.info(f"Query Rewrite: {query_rewrite}")
    
    return query_rewrite

@timing_decorator
def chat_with_history(query: str, history) -> Tuple[str, str]:
    """
    Hàm này để trả lời câu hỏi của người dùng theo flow: get_history + query-> rewrite_query -> router -> get_context OR search_db OR out_text -> LLM -> response

    Args: 
        - query: câu hỏi của người dùng
    Return:
        Dictionary chứa các thông tin sau:
            - type: loại câu hỏi
            - out_text: câu trả lời của chatbot
            - extract_similarity: trả về True nếu câu hỏi là extract_similarity
            - extract_inventory: trả về True nếu câu hỏi là extract
    """

    history_conversation = get_history()
    query_rewrited = rewrite_query(query=query, history=history_conversation)
    print(query_rewrited)

    type = decision_search_type(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    print(type)
    results = {"type": type, "out_text": None, "extract_similarity": False}

    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question', 'instruction_answer'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | SYSTEM_CONFIG.load_rag_model() | StrOutputParser()

    if type == "LLM_predict": # LLM tự trả lời
        response = rag_chain.invoke({'context':"", 
                                     'question': query_rewrited, 
                                     'instruction_answer': ""})
        results['out_text'] = response

    elif type == "extract_similarity": # sản phẩm tương tự
        results["extract_similarity"] = True
        results['out_text'] = "Bạn hãy nhập thông tin về giá hoặc thông số kỹ thuật của sản phẩm bạn đang quan tâm:"

    elif type == "extract_product_text": # chroma db search
        instruction_answer = get_context(query=query_rewrited, db_name="Cau_hoi_thuong_gap") # lấy ra thông tin câu hỏi tương tự câu query
        context = get_context(query=query_rewrited, db_name="dieu_hoa") # thông tin điều hòa liên quan tới câu query
        response = rag_chain.invoke({'context': context, 
                                     'question': query_rewrited, 
                                     'instruction_answer': instruction_answer})
        results['out_text'] = response 

    else: # elastic search
        instruction_answer = get_context(query=query_rewrited, 
                                         db_name="Cau_hoi_thuong_gap")
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products, check = search_db(demands)
        response = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewrited, 
                                     'instruction_answer': instruction_answer})
        results['out_text'] = response 
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(results['out_text'])

    if isinstance(history, list):
        history.append((query, results['out_text']))

    return "", history

@timing_decorator
def chat_with_history_copy(query: str) -> str:
    """
    Hàm này để trả lời câu hỏi của người dùng theo flow: get_history + query-> rewrite_query -> router -> get_context OR search_db OR out_text -> LLM -> response

    Args: 
        - query: câu hỏi của người dùng
    Return:
        Dictionary chứa các thông tin sau:
            - type: loại câu hỏi
            - out_text: câu trả lời của chatbot
            - extract_similarity: trả về True nếu câu hỏi là extract_similarity
            - extract_inventory: trả về True nếu câu hỏi là extract
    """

    history_conversation = get_history()
    query_rewrited = rewrite_query(query=query, history=history_conversation)
    print(query_rewrited)

    function_called = decision_search_type(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    print(function_called)
    results = {"type": function_called, "out_text": None, "extract_similarity": False}

    PROMPT_HEADER_TEMPLATE = PromptTemplate(
        input_variables=['context', 'question', 'instruction_answer'],
        template=PROMPT_HEADER)
    rag_chain = PROMPT_HEADER_TEMPLATE | SYSTEM_CONFIG.load_rag_model() | StrOutputParser()

    if type == "SIMILARITY": # sản phẩm tương tự
        results["extract_similarity"] = True
        results['out_text'] = "Bạn hãy nhập thông tin về giá hoặc thông số kỹ thuật của sản phẩm bạn đang quan tâm:"

    elif type == "TEXT": # chroma db search
        instruction_answer = get_context(query=query_rewrited, db_name="Cau_hoi_thuong_gap") # lấy ra thông tin câu hỏi tương tự câu query
        context = get_context(query=query_rewrited, db_name="dieu_hoa") # thông tin điều hòa liên quan tới câu query
        response = rag_chain.invoke({'context': context, 
                                     'question': query_rewrited, 
                                     'instruction_answer': instruction_answer})
        results['out_text'] = response 

    else: # elastic search
        instruction_answer = get_context(query=query_rewrited, 
                                         db_name="Cau_hoi_thuong_gap")
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products, check = search_db(demands)
        # print(response_elastic)
        response = rag_chain.invoke({'context': response_elastic, 
                                     'question': query_rewrited, 
                                     'instruction_answer': instruction_answer})
        results['out_text'] = response 
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(results['out_text'])


    return results['out_text']