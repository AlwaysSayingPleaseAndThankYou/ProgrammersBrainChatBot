import pytesseract
from langchain.document_loaders import PyPDFLoader, BSHTMLLoader, TextLoader, UnstructuredPDFLoader
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
from pytesseract import image_to_string
import pypdfium2 as pdfium
from io import BytesIO
from PIL import Image
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.node_parser import SimpleNodeParser
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor


def convert_pdf_to_images(file_path, scale=300 / 72):
    ## 1/ This is used to load local files instead of fetching from url

    pdf_file = pdfium.PdfDocument(file_path)

    page_indices = [i for i in range(len(pdf_file))]

    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )

    final_images = []

    for i, image in zip(page_indices, renderer):
        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        final_images.append(dict({i: image_byte_array}))

    return final_images


def extract_text_from_img(list_dict_final_images):
    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []

    for index, image_bytes in enumerate(image_list):
        try:
            image = Image.open(BytesIO(image_bytes))
            raw_text = str(image_to_string(image))
            image_content.append(raw_text)
            print(raw_text)
        except pytesseract.TesseractError as e:
            print(e)

    return "\n".join(image_content)


llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo-0613")

# openai.api_key = key
embeddings_model = OpenAIEmbeddings()

text_splitter = CharacterTextSplitter(
    separator='\n',
    chunk_size=1024,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True,
)
book_path = Path('temp', 'brain.pdf')
book_text_path = Path('temp', 'brain.txt')

if not book_text_path.exists():
    images = convert_pdf_to_images(book_path)
    book_text = extract_text_from_img(images)
    book_text = book_text.replace('©Manning Publications Co. To comment go to liveBook', '')
    with book_text_path.open('w+') as f:
        f.write(book_text)
loader = TextLoader(str(book_text_path.absolute()))
# pdfloader = UnstructuredPDFLoader(str(book_path.absolute()))
# index = VectorstoreIndexCreator().from_loaders([loader])
documents = loader.load()
texts = text_splitter.split_documents(documents)
# texts = text_splitter.split_documents(pdfloader.load())
chroma = Chroma.from_documents(texts, embeddings_model, collection_name='the-programmers-brain')
# llama vector store
# reader = SimpleDirectoryReader(
#     input_files=[str(book_text_path)]
# )
# llama_data = reader.load_data()
# node_parser = SimpleNodeParser.from_defaults()
# nodes = node_parser.get_nodes_from_documents(llama_data)
# vector_index = VectorStoreIndex(nodes)
# retriever = index.as_query_engine()
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
