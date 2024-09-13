import os
from typing import Union
from langchain_community.vectorstores import Chroma
from configs.load_config import LoadConfig
from utils.data_process import csv2txt_product, csv2text_question

CFG_APP = LoadConfig()

def create_db(db_name: str) -> Union[str, Chroma, int]:
    """
    Load data chunked và tạo vector db cho data
    """
    db_path = os.path.join(CFG_APP.vector_database_directory, db_name)
    if db_name == "dieu_hoa":
        csv_path = CFG_APP.csv_product_directory
        data_chunked = csv2txt_product(csv_link=csv_path)
        top_K = CFG_APP.top_k_product

    else:
        csv_path = CFG_APP.csv_question_user
        data_chunked = csv2text_question(csv_link=csv_path)
        top_K = CFG_APP.top_k_question

    if not db_path:
        vectordb = Chroma.from_documents(documents=data_chunked, 
                                            embedding=CFG_APP.load_embed_openai_model(),
                                            persist_directory=db_path)
    else:
        vectordb = Chroma(persist_directory=db_path, 
                            embedding_function=CFG_APP.load_embed_openai_model())
    return data_chunked, vectordb, top_K