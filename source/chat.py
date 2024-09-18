from typing import Dict
from langchain.memory import ConversationBufferWindowMemory
from source.retriever import get_context
from source.router import call_function
from module_elastic import  search_db, parse_string_to_dict
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
def chat_with_history(query: str, history) -> Dict[str, str]:
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

    type = call_function(query_rewrited)
    print(type)

    results = {"type": type, "out_text": None, "extract_similarity": False}


    if type == "LLM_predict": # LLM tự trả lời
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context="", 
                                            instruction_answer="")
        response  = SYSTEM_CONFIG.load_rag_model().invoke(input=prompt_final).content
        results['out_text'] = response

    elif type == "extract_similarity": # sản phẩm tương tự
        results["extract_similarity"] = True
        results['out_text'] = "Bạn hãy nhập thông tin về giá hoặc thông số kỹ thuật của sản phẩm bạn đang quan tâm:"

    elif type == "extract_product_text": # chroma db search
        instruction_answer = get_context(query=query_rewrited, db_name="Cau_hoi_thuong_gap") # lấy ra thông tin câu hỏi tương tự câu query
        context = get_context(query=query_rewrited, db_name="dieu_hoa") # thông tin điều hòa liên quan tới câu query
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=context, 
                                            instruction_answer=instruction_answer)
        response = SYSTEM_CONFIG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 

    else: # elastic search
        instruction_answer = get_context(query=query_rewrited, 
                                         db_name="Cau_hoi_thuong_gap")
        demands = parse_string_to_dict(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        response_elastic, products, check = search_db(demands)
        save_outtext = response_elastic
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=save_outtext, 
                                            instruction_answer=instruction_answer)
        response = SYSTEM_CONFIG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(results['out_text'])

    if isinstance(history, list):
        history.append((query, results['out_text']))

    return "", history

@timing_decorator
def chat_with_history_copy(query: str) -> Dict[str, str]:
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

    results_funcalled = call_function(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    type, arguments = results_funcalled['function_called'], results_funcalled['arguments'] 
    print(results_funcalled)

    results = {"type": type, "out_text": None, "extract_similarity": False}


    if type == "LLM_predict": # LLM tự trả lời
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context="", 
                                            instruction_answer="")
        response  = SYSTEM_CONFIG.load_rag_model().invoke(input=prompt_final).content
        results['out_text'] = response

    elif type == "extract_similarity": # sản phẩm tương tự
        results["extract_similarity"] = True
        results['out_text'] = "Bạn hãy nhập thông tin về giá hoặc thông số kỹ thuật của sản phẩm bạn đang quan tâm:"

    elif type == "extract_product_text": # chroma db search
        instruction_answer = get_context(query=query_rewrited, db_name="Cau_hoi_thuong_gap") # lấy ra thông tin câu hỏi tương tự câu query
        context = get_context(query=query_rewrited, db_name="dieu_hoa") # thông tin điều hòa liên quan tới câu query
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=context, 
                                            instruction_answer=instruction_answer)
        response = SYSTEM_CONFIG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 

    else: # elastic search
        instruction_answer = get_context(query=query_rewrited, 
                                         db_name="Cau_hoi_thuong_gap")
        
        demands = parse_string_to_dict(arguments)
        print("= = = = arguments from function calling = = = =:", demands)

        if len(demands['object']) >= 1:  # nếu có object thì mới search
            response_elastic, products, ok = search_db(demands)
            save_outtext = response_elastic
        else: 
            save_outtext = ""
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=save_outtext, 
                                            instruction_answer=instruction_answer)
        response = SYSTEM_CONFIG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(results['out_text'])

    return results['out_text']