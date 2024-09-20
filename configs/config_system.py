import os
from dotenv import load_dotenv
import yaml
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")
os.environ['GOOGLE_CSE_ID'] = os.getenv("GOOGLE_CSE_ID")


class LoadConfig:
    def __init__(self) -> None:
        with open("./configs/config.yml", mode='r') as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        
        self.load_directories(app_config=app_config)
        self.load_llm_config(app_config=app_config)
        self.load_retriver_config(app_config=app_config)

    def load_directories(self, app_config):
        # Load parameters directories from load_config.yml file 
        self.vector_database_directory = (
            app_config['directories']['vector_database_directory']
        )
        self.csv_dieu_hoa_directory = (
            app_config['directories']['csv_dieu_hoa_directory']
        )
        self.csv_question_user = (
            app_config['directories']['csv_question_user']
        )
        self.csv_all_product_directory = (
            app_config['directories']['csv_all_product_directory']
        )
        self.avt_user = app_config['directories']['avt_user']
        self.avt_bot = app_config['directories']['avt_bot']
        self.logo = app_config['directories']['logo']
        
    def load_llm_config(self, app_config):
        # Load parameters llm from load_config.yml file 
        self.rag_model = app_config['llm_config']['rag_model']
        self.chatchit_model = app_config['llm_config']['chatchit_model']
        self.temperature_rag = app_config['llm_config']['temperature_rag']
        self.temperature_chat = app_config['llm_config']['temperature_chat']
        self.max_token = app_config['llm_config']['max_token']
        
    def load_retriver_config(self, app_config):
        self.embedding_baai = app_config['retriever_config']['embedding_baai']
        self.vector_embed_baai = app_config['retriever_config']['vector_embed_baai']
        self.vector_embed_openai = app_config['retriever_config']['vector_embed_openai']
        self.embedding_openai = app_config['retriever_config']['embedding_openai']
        self.top_k_product = app_config['retriever_config']['top_k_product']
        self.top_k_question = app_config['retriever_config']['top_k_question']

    def load_embed_openai_model(self) -> OpenAIEmbeddings:
        embedding_model = OpenAIEmbeddings()
        return embedding_model
    
    def load_rag_model(self) -> ChatOpenAI:
        rag_model = ChatOpenAI(
            model=self.rag_model,
            streaming=True,
            temperature=self.temperature_rag,
            max_tokens=self.max_token,
            verbose=True,
        )
        return rag_model
    
    def load_chatchit_model(self) -> ChatOpenAI:
        chatchit_model = ChatOpenAI(
            model=self.rag_model,
            streaming=True,
            temperature=self.temperature_chat,
            max_tokens=self.max_token,
            verbose=True,
        )
        return chatchit_model
    
    def load_rewrite_model(self) -> ChatOpenAI:
        rewrite_model = ChatOpenAI(
            model=self.rag_model,
            temperature=self.temperature_rag,
            max_tokens=self.max_token,
            verbose=True,
        )
        return rewrite_model
    
SYSTEM_CONFIG = LoadConfig()