from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore



llm = ChatOpenAI(model="gpt-4o")
vectorstore = InMemoryVectorStore()