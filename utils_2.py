from langchain.prompts import PromptTemplate
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser 
import streamlit as st
from langchain_community.document_loaders import UnstructuredURLLoader
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import time 
from langchain_community.vectorstores import Qdrant
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA

from langchain_openai import OpenAIEmbeddings
import qdrant_client
import os 
import pyttsx3
load_dotenv()



def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()



#------------------------------------------------------------------------
"""LOad All the Pdf Data """

def pdf_to_text(pdf_files):
    all_pdf_text_list = []
    source_list = []
    for file in pdf_files:
        pdf = PdfReader(file)
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            text = page.extract_text()
            all_pdf_text_list.append(text)
            source_list.append(file.name + "_page_" + str(page_number))
            
    text_splitter = RecursiveCharacterTextSplitter( chunk_size = 1000, chunk_overlap = 0, length_function = len,)
    
    pdf_docs = text_splitter.create_documents(all_pdf_text_list, metadatas = [{"sounrce" : s} for s in source_list])
    
    st.write( "pdf_docs -------> ",pdf_docs)
    
    url="https://0c48d6c0-91d3-48ae-95b9-414ed284aad7.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="JHbe2Onl9d7skuq9POOZgK3Zma_iJQu59zPtks7F0o9WrtAiKJcpcw",
    qdrant = Qdrant.from_documents(pdf_docs,
                                   OpenAIEmbeddings(), 
                                   url=url[0],
                                   prefer_grpc=True,
                                   api_key=api_key[0],
                                   collection_name="mycollection")
    return qdrant
    

# #-----------------------------------------------------------------------------------------------------
# """It Loads all the url  Data"""

def web_data_loader(urls):
    try:
        loader = SeleniumURLLoader(urls=urls)
        web_text = loader.load()
    except:
        st.write("SeleniumURLLoader Error Occurred ")
        print("\n\n ----------->> SeleniumURLLoader Error Occurred <<------------ \n\n ")
        try:
            web_data = WebBaseLoader(urls)
            web_text = web_data.load()
        except:
            st.write("WebBaseLoader Error Occurred ")
            print("\n\n --------->> WebBaseLoader Error Occurred <<--------- \n\n ")
            web_data = UnstructuredURLLoader(urls)
            web_text = web_data.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)

    web_docs = text_splitter.split_documents(web_text)
    st.write("web_docs -------------> ", web_docs)

    embeddings = OpenAIEmbeddings()

    # Creating a dummy class with page_content and metadata attributes
    class Document:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata 

    # Iterate over each document and create Chroma database
    
    st.write(f"\n\n total ---> {len(web_docs)} documents are these \n\n ")
    st.write("\n\n Document Saving in DB ......\n\n " )
    
    for i, doc_content in enumerate(web_docs):
        document = Document(doc_content.page_content, doc_content.metadata)
        print(document)     
        
        url="https://0c48d6c0-91d3-48ae-95b9-414ed284aad7.us-east4-0.gcp.cloud.qdrant.io:6333"
        api_key="JHbe2Onl9d7skuq9POOZgK3Zma_iJQu59zPtks7F0o9WrtAiKJcpcw"
        qdrant = Qdrant.from_documents([document],
                               OpenAIEmbeddings(),
                               url=url,
                               prefer_grpc=True,
                               api_key=api_key,
                               collection_name="mycollection")
        
        st.write( f"{i+1}/{len(web_docs)}" )
    return qdrant





url="https://0c48d6c0-91d3-48ae-95b9-414ed284aad7.us-east4-0.gcp.cloud.qdrant.io:6333"
api_key="JHbe2Onl9d7skuq9POOZgK3Zma_iJQu59zPtks7F0o9WrtAiKJcpcw"
    
embeddings = OpenAIEmbeddings( )
client = qdrant_client.QdrantClient(  url=url, prefer_grpc=True, api_key=api_key)

vectorstore = Qdrant(client=client,
                     collection_name= 'mycollection',
                     embeddings=embeddings)

# # ------------------------------------------------------------------------

def genrating_answer_from_db( query , vectorstore =  vectorstore):  

    # print("vectorstore-->", vectorstore)
    qa = RetrievalQA.from_chain_type(llm=OpenAI( ),
                                chain_type="stuff",
                                retriever=vectorstore.as_retriever() )

    answer = qa.run(query)
    return answer


    


    
