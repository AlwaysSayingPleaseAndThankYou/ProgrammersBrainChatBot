from langchain.document_loaders import PyPDFLoader, BSHTMLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, LLMSingleActionAgent, AgentExecutor
from langchain.agents import AgentType
import requests
from pathlib import Path
from animus import CustomPromptTemplate, template, CustomOutputParser
from langchain import LLMChain
from langchain.memory import ConversationBufferWindowMemory

def get_html_content(url: str) -> str:
    """
    Fetch the HTML content of a given URL using the requests library.

    :param url: The URL of the webpage.
    :return: The HTML content of the webpage.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


key = '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'

os.environ['OPENAI_API_KEY'] = key

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

# openai.api_key = key
embeddings_model = OpenAIEmbeddings()

text_splitter = CharacterTextSplitter(
    chunk_size=10000,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True,
)
book_path = Path('temp','brain.pdf')
loader = PyPDFLoader(book_path.absolute().__str__())
index = VectorstoreIndexCreator().from_loaders([loader])

tools = [
    Tool(name='search',
         func=index.query,
         description='used to cite the book "the programmers brain". input should be a query or question',
         return_direct=True)]

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
memory=ConversationBufferWindowMemory(k=2)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, memory=memory, verbose=True)
