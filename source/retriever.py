
import dotenv
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_community.retrievers import BM25Retriever
from source.load_db import create_db
from configs.load_config import LoadConfig
from utils import timing_decorator

APP_CONFIG = LoadConfig()
dotenv.load_dotenv()


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
