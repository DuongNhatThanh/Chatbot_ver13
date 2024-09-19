# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
# from langchain import hub
# from langchain.agents import AgentExecutor, create_openai_tools_agent
# from configs.config_system import SYSTEM_CONFIG

# llm = SYSTEM_CONFIG.load_rag_model()

# def search_similar_product(query: str) -> str:
#     api_wrapper = TavilySearchAPIWrapper()
#     tavily_tool = TavilySearchResults(api_wrapper=api_wrapper,
#                                       max_results=2)

#     instructions = """You are an experienced researcher who always finds high-quality and relevant information on the Internet."""
#     base_prompt = hub.pull("langchain-ai/openai-functions-template")
#     prompt = base_prompt.partial(instructions = instructions)

#     tools = [tavily_tool]
#     agent = create_openai_tools_agent(
#         llm=llm,
#         tools=tools,
#         prompt=prompt
#     )
#     agent_excutor = AgentExecutor(
#         agent=agent,
#         tools=tools,
#         verbose=True
#     )

#     response = agent_excutor.invoke({"input": query})['output']
#     return response

# if __name__ == '__main__':
#     query = "Tôi muốn mua điều hòa 10 triệu"
#     response = search_similar_product(query=query)
#     print(response[0]['content'])



from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.retrievers.web_research import WebResearchRetriever
from langchain_community.utilities import GoogleSearchAPIWrapper 
import os
import faiss
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.docstore.in_memory import InMemoryDocstore
from configs.config_system import SYSTEM_CONFIG



embeddings_model = SYSTEM_CONFIG.load_embed_openai_model()  
vectorstore = Chroma(embedding_function=SYSTEM_CONFIG.load_embed_openai_model(), 
                     persist_directory="data/vector_db/search_web")


search = GoogleSearchAPIWrapper()

web_retriever = WebResearchRetriever.from_llm(
        vectorstore=vectorstore,
        llm=SYSTEM_CONFIG.load_rag_model(), 
        search=search, 
        num_search_results=3,
        allow_dangerous_requests=True
    )

# class StreamHandler(BaseCallbackHandler):
#     def __init__(self, container, initial_text=""):
#         self.container = container
#         self.text = initial_text

#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         self.text += token
#         self.container.info(self.text)


# class PrintRetrievalHandler(BaseCallbackHandler):
#     def __init__(self, container):
#         self.container = container.expander("Context Retrieval")

#     def on_retriever_start(self, query: str, **kwargs):
#         self.container.write(f"**Question:** {query}")

#     def on_retriever_end(self, documents, **kwargs):
#         # self.container.write(documents)
#         for idx, doc in enumerate(documents):
#             source = doc.metadata["source"]
#             self.container.write(f"**Results from {source}**")
#             self.container.text(doc.page_content)

qa_chain = RetrievalQAWithSourcesChain.from_chain_type(SYSTEM_CONFIG.load_rag_model(), 
                                                       retriever=web_retriever)

question = "anh muốn chốt đơn điều hòa 1 chiều giá 10 triệu"
result = qa_chain({"question": question})['answer']
print(result)