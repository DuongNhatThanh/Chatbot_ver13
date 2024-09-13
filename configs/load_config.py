import os
from dotenv import load_dotenv
import yaml
import shutil
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
# os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
# os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")

class LoadConfig:
    def __init__(self) -> None:
        with open("./configs/config.yml") as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        
        self.load_directories(app_config=app_config)
        self.load_llm_config(app_config=app_config)
        self.load_chunk_config(app_config=app_config)
        self.load_retriver_config(app_config=app_config)

    def load_directories(self, app_config):
        # Load parameters directories from load_config.yml file 
        self.persist_vector_directory = (
            app_config['directories']['persist_vector_directory']
        )
        self.csv_product_directory = (
            app_config['directories']['csv_product_directory']
        )
        self.csv_question_user = (
            app_config['directories']['csv_question_user']
        )

        
    def load_llm_config(self, app_config):
        # Load parameters llm from load_config.yml file 
        self.rag_model = app_config['llm_config']['rag_model']
        self.chatchit_model = app_config['llm_config']['chatchit_model']
        self.temperature_rag = app_config['llm_config']['temperature_rag']
        self.temperature_chat = app_config['llm_config']['temperature_chat']
        self.max_token = app_config['llm_config']['max_token']
        
    def load_retriver_config(self, app_config):
        self.vector_embed_size = app_config['retriever_config']['vector_embed_size']
        self.embedding_model = app_config['retriever_config']['embedding_model']
        self.top_k_product = app_config['retriever_config']['top_k_product']
        self.top_k_question = app_config['retriever_config']['top_k_question']

    def load_chunk_config(self, app_config):
        self.chunk_size = app_config['chunk_config']['chunk_size']
        self.chunk_overlap = app_config['chunk_config']['chunk_overlap']


    def load_embed_openai_model(self) -> OpenAIEmbeddings:
        embedding_model = OpenAIEmbeddings()
        return embedding_model
    
    def load_embed_bge_model(self) -> FastEmbedEmbeddings:
        embedding_model = FastEmbedEmbeddings(model_name=self.embedding_model)
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