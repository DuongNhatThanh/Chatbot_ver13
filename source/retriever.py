
import os
import dotenv
from typing import List, Union
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_community.retrievers import BM25Retriever
from utils import timing_decorator
from utils.data_processer import csv2txt_product, csv2text_question
from configs.config_system import LoadConfig


APP_CONFIG = LoadConfig()
dotenv.load_dotenv()

def create_db(db_name: str) -> Union[str, Chroma, int]:
    """
    Load data chunked và tạo vector db cho data
    """
    db_path = os.path.join(APP_CONFIG.vector_database_directory, db_name)
    if db_name == "dieu_hoa":
        csv_path = APP_CONFIG.csv_product_directory
        data_chunked = csv2txt_product(csv_link=csv_path)
        top_K = APP_CONFIG.top_k_product

    else:
        csv_path = APP_CONFIG.csv_question_user
        data_chunked = csv2text_question(csv_link=csv_path)
        top_K = APP_CONFIG.top_k_question

    if not db_path:
        vectordb = Chroma.from_documents(documents=data_chunked, 
                                            embedding=APP_CONFIG.load_embed_openai_model(),
                                            persist_directory=db_path)
    else:
        vectordb = Chroma(persist_directory=db_path, 
                            embedding_function=APP_CONFIG.load_embed_openai_model())
    return data_chunked, vectordb, top_K

def init_retriever(vector_db: Chroma, data_chunked: List[Document], top_k: int) -> EnsembleRetriever:
    """
    Khởi tạo retriver để tìm kiếm context từ câu hỏi người dùng
    Arg: 
        vector db: vector db(Chroma) được khỏi tạo trong file create_db.py
        data_chunked: data được chunk (file từng sản phẩm hoặc file tất cả sản phẩm)
    Return:
        trả về  ensemble retriever kết hợp reranker 
    """

    # initialize the bm25 retriever
    retriever_BM25 = BM25Retriever.from_documents(data_chunked)
    retriever_BM25.k = top_k

    retriever_vanilla = vector_db.as_retriever(search_type="similarity", 
                                                search_kwargs={"k": top_k})
    
    retriever_mmr = vector_db.as_retriever(search_type="mmr", 
                                            search_kwargs={"k": top_k})
    
    # initialize the ensemble retriever with 3 Retrievers
    ensemble_retriever = EnsembleRetriever(
        retrievers=[retriever_vanilla, retriever_mmr, retriever_BM25], 
        weights=[0.3, 0.3, 0.4])
    # rerank with cohere
    # compressor = CohereRerank(cohere_api_key=os.getenv("COHERE_API_KEY"), top_n=APP_CONFIG.top_k)
    # compression_retriever = ContextualCompressionRetriever(
    #     base_compressor=compressor, 
    #     base_retriever=ensemble_retriever
    # )
    return ensemble_retriever

@timing_decorator
def get_context(query: str, db_name: str) -> str:
    """
    Hàm này để lấy context từ câu hỏi của người dùng
    Arg:
        query: câu hỏi của người dùng sau khi được rewrite.
        db_name: loại db chứa data cần tìm kiếm
    Return:
        phần context liên quan đến query cho llm
    """

    data_chunked, vector_db, top_K = create_db(db_name=db_name)

    retriever = init_retriever(vector_db=vector_db, data_chunked=data_chunked, top_k=top_K)
    contents = retriever.invoke(input=query)

    final_contents = "\n\n".join(doc.page_content for doc in contents)
    return final_contents
