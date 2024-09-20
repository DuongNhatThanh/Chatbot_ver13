import os
from typing import Dict, Tuple
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from source.retriever import get_context
from source.router import decision_search_type
from module_elastic import  search_db, classify_intent
from utils import (
    PROMPT_HEADER, PROMPT_HISTORY,
    GradeReWrite, timing_decorator
)
from configs.config_system  import SYSTEM_CONFIG


def get_session_history(user_name: str, seasion_id: str) -> BaseChatMessageHistory:
    stores = {}
    if not os.path.join(CONVERSATION_PATH) and len(os.path.getsize(CONVERSATION_PATH)) > 0:

    else:
        store[(user_name, seasion_id)] = ConversationBufferWindowMemory(k=3).load_memory_variables({})
    return store[(user_name, seasion_id)]


def initlize_chatbot(query: int, user_name: str, user_info: str, history):

    query_rewrited = rewrite_query(query=query, history=history_conversation)
    print(query_rewrited)

    type = decision_search_type(query_rewrited) # sử dụng function calling để gọi các hàm custom.
    print(type)
    results = {"type": type, "out_text": None, "extract_similarity": False}

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