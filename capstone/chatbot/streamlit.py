import time
import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
# Use JSONDirectoryLoader here
from langchain_community.document_loaders import JSONLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Replace with your actual model import
# import rag_chat
# from product.models import Product, Review

import os
load_dotenv()

# load the GROQ And OpenAI API KEY
groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Define the target URL
target_url = "http://127.0.0.1:8000/"  # Replace with your desired URL

# Create a button
if st.button("Go Back"):
    # Display the link as a clickable HTML element
    st.markdown(f"[Click here to proceed to the URL]({target_url})")

st.title("Database Model Document Q&A")


llm = ChatGroq(groq_api_key=groq_api_key,
               model_name="Llama3-8b-8192")

prompt = ChatPromptTemplate.from_template(
    """
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions:{input}

"""
)

jq_query = ".[]"


def vector_embedding():
    if "vectors" not in st.session_state:
        with st.spinner("Loading and processing documents... Please wait."):
            time.sleep(2)  # Simulate a small delay for better UX

            # Step 1: Get review data from the database
            st.session_state.loader = JSONLoader(
                "product_reviews.json", jq_schema=".[]", text_content=False
            )

            # Load documents into session state
            st.session_state.docs = st.session_state.loader.load()

            # Step 2: Split reviews into chunks
            st.session_state.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            )

            st.session_state.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )  # Chunk Creation

            # Split the reviews into chunks for processing
            st.session_state.final_documents = st.session_state.text_splitter.split_documents(
                st.session_state.docs[:20]
            )

            # Step 3: Create the vector store from documents
            st.session_state.vectors = FAISS.from_documents(
                st.session_state.final_documents, st.session_state.embeddings
            )

        st.success("Vector Store DB is Ready ✅")


# Button to trigger embedding process
if st.button("Documents Embedding"):
    vector_embedding()


prompt1 = st.text_input("Enter Your Question From Documents")

if prompt1:
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    start = time.process_time()
    response = retrieval_chain.invoke({'input': prompt1})
    print("Response time :", time.process_time()-start)
    st.write(response['answer'])

    # With a streamlit expander
    with st.expander("Document Similarity Search"):
        # Find the relevant chunks
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------")
