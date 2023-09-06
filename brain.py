from langchain.document_loaders import PyPDFLoader, BSHTMLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, LLMSingleActionAgent, AgentExecutor, ConversationalChatAgent
from langchain.agents import AgentType
import requests
from pathlib import Path
from animus import CustomPromptTemplate, template, CustomOutputParser
from langchain import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA


def get_html_content(url: str) -> str:
    """
    Fetch the HTML content of a given URL using the requests library.

    :param url: The URL of the webpage.
    :return: The HTML content of the webpage.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo-0613")

# openai.api_key = key
embeddings_model = OpenAIEmbeddings()

text_splitter = CharacterTextSplitter(
    separator='\n',
    chunk_size=10000,
    chunk_overlap=2000,
    length_function=len,
    add_start_index=True,
)
book_path = Path('temp', 'brain.pdf')
loader = PyPDFLoader(str(book_path.absolute()))
# index = VectorstoreIndexCreator().from_loaders([loader])
documents = loader.load()
texts = text_splitter.split_documents(documents)
chroma = Chroma.from_documents(texts, embeddings_model, collection_name='the-programmers-brain')
index = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=chroma.as_retriever())
tools = [
    Tool(name='search',
         func=index.run,
         description='used to cite the book "the programmers brain". input should be a query or question',
         return_direct=True)]
# Do you know where the mute button is...... NO... Maybe.... I had it a second ago!!
# it was under my name I think  ANd now it isn
# rude

# Like it isn't there anymore
# I can't unmute you, I tried
prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps", "history"]
)
output_parser = CustomOutputParser()
# agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
llm_chain = LLMChain(llm=llm, prompt=prompt)
tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=tool_names
)
memory = ConversationBufferWindowMemory(k=2)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, memory=memory, verbose=True)
