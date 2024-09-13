from typing import Dict
from langchain.memory import ConversationBufferWindowMemory
from source.retriever import get_context
from source.router import call_funcion
from utils.base_model import GradeReWrite
from utils.prompt import PROMPT_HISTORY, PROMPT_HEADER
from elastic_search.few_shot_sentence import classify_intent
from elastic_search.retrieval import search_db
from logs.logger import set_logging_error, set_logging_terminal
from configs.load_config import LoadConfig

APP_CFG = LoadConfig()
logger_error = set_logging_error()    
logger_terminal = set_logging_terminal()

memory = ConversationBufferWindowMemory(memory_key="chat_history", k=3)

def get_history() -> str:
    history = memory.load_memory_variables({})
    return history['chat_history']


def rewrite_query(query: str, history: str) -> str: 
    
    """
    Sử dụng LLM để viết lại câu hỏi của người dùng thành 1 câu mới dựa vào lịch sử trước đó và câu hỏi hiện tại.

    Arg:
        query: câu hỏi của người dùng
        history: lịch sử của người dùng
    Return:
        trả về câu hỏi được viết lại.
    """
    logger_terminal.info(f"Query User: {query}")

    llm_with_output = APP_CFG.load_rewrite_model().with_structured_output(GradeReWrite)
    query_rewrite = llm_with_output.invoke(PROMPT_HISTORY.format(question=query, chat_history=history)).rewrite
    logger_terminal.info(f"Query Rewrite: {query_rewrite}")
    
    return query_rewrite


def chat_with_history(query: str, history) -> Dict[str, str]:
    """
    Hàm này để trả lời câu hỏi của người dùng theo flow: get_history + query-> rewrite_query -> router -> get_context OR search_db OR out_text -> LLM -> response

    Args: 
        query: câu hỏi của người dùng
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

    type = call_funcion(query_rewrited)
    print(type)

    results = {"type": type, "out_text": None, "extract_similarity": False, "extract_inventory": False}


    if type == "LLM_predict": # LLM tự trả lời
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context="", 
                                            instruction_answer="")
        response  = APP_CFG.load_rag_model().invoke(input=prompt_final).content
        results['out_text'] = response

    elif type == "extract_inventory": # sản phẩm tồn kho
        results["extract_inventory"] = True
        results['out_text'] = "Anh/chị vui lòng nhập mã hoặc tên sản phẩm và mã tỉnh theo mẫu sau:"

    elif type == "extract_similarity": # sản phẩm tương tự
        results["extract_similarity"] = True
        results['out_text'] = "Bạn hãy nhập thông tin về giá hoặc thông số kỹ thuật của sản phẩm bạn đang quan tâm:"

    elif type == "extract_product_text": # chroma db search
        instruction_answer = get_context(query=query_rewrited, db_name="Cau_hoi_thuong_gap") # lấy ra thông tin câu hỏi tương tự câu query
        context = get_context(query=query_rewrited, db_name="dieu_hoa") # thông tin điều hòa liên quan tới câu query
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=context, 
                                            instruction_answer=instruction_answer)
        response = APP_CFG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 

    else: # elastic search
        instruction_answer = get_context(query=query_rewrited, 
                                         db_name="Cau_hoi_thuong_gap")
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        if len(demands['object']) >= 1:
            response_elastic, products, ok = search_db(demands)
            save_outtext = response_elastic
        else: 
            save_outtext = ""
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=save_outtext, 
                                            instruction_answer=instruction_answer)
        response = APP_CFG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(results['out_text'])

    if isinstance(history, list):
        history.append((query, results['out_text']))

    return "", history

def chat_with_history_copy(query: str) -> Dict[str, str]:
    """
    Hàm này để trả lời câu hỏi của người dùng theo flow: get_history + query-> rewrite_query -> router -> get_context OR search_db OR out_text -> LLM -> response

    Args: 
        query: câu hỏi của người dùng
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

    type = call_funcion(query_rewrited)
    print(type)

    results = {"type": type, "out_text": None, "extract_similarity": False, "extract_inventory": False}


    if type == "LLM_predict": # LLM tự trả lời
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context="", 
                                            instruction_answer="")
        response  = APP_CFG.load_rag_model().invoke(input=prompt_final).content
        results['out_text'] = response

    elif type == "extract_inventory": # sản phẩm tồn kho
        results["extract_inventory"] = True
        results['out_text'] = "Anh/chị vui lòng nhập mã hoặc tên sản phẩm và mã tỉnh theo mẫu sau:"

    elif type == "extract_similarity": # sản phẩm tương tự
        results["extract_similarity"] = True
        results['out_text'] = "Bạn hãy nhập thông tin về giá hoặc thông số kỹ thuật của sản phẩm bạn đang quan tâm:"

    elif type == "extract_product_text": # chroma db search
        instruction_answer = get_context(query=query_rewrited, db_name="Cau_hoi_thuong_gap") # lấy ra thông tin câu hỏi tương tự câu query
        context = get_context(query=query_rewrited, db_name="dieu_hoa") # thông tin điều hòa liên quan tới câu query
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=context, 
                                            instruction_answer=instruction_answer)
        response = APP_CFG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 

    else: # elastic search
        instruction_answer = get_context(query=query_rewrited, 
                                         db_name="Cau_hoi_thuong_gap")
        demands = classify_intent(query_rewrited)
        print("= = = = result few short = = = =:", demands)
        if len(demands['object']) >= 1:
            response_elastic, products, ok = search_db(demands)
            save_outtext = response_elastic
        else: 
            save_outtext = ""
        prompt_final = PROMPT_HEADER.format(question=query_rewrited, 
                                            context=save_outtext, 
                                            instruction_answer=instruction_answer)
        response = APP_CFG.load_rag_model().invoke(prompt_final).content
        results['out_text'] = response 
    
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(results['out_text'])

    return results['out_text']
