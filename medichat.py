import os
import streamlit as st

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

DB_FAISS_PATH='vectorstore/db_faiss'
@st._cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

    return db

def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])
    return prompt


def load_llm(huggingface_repo_id,HF_TOKEN):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        token=HF_TOKEN,  # ✅ Fix: token should be passed here
        model_kwargs={"max_length": 512}  # ✅ Fix: Use integer, not string
    )
    return llm

def main():
    st.title("Medi Chat !")

    # Initialize session state for storing messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        # Display user message and store it
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', 'content': prompt})


    CUSTOM_PROMPT_TEMPLATE = """
    Use the pieces of information provided in the context to answer user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Don't provide anything out of the given context.

    Context: {context}
    Question: {question}

    Start the answer directly. No small talk please.
    """

    HUGGINGFACE_REPO_ID = "mistralai/Mistral-7B-Instruct-v0.3"
    HF_TOKEN = os.environ.get("HF_TOKEN")



    try:
        vectorstore=get_vectorstore()
        if vectorstore is None:
            st.error("Failed to load the vectorstore")

        qa_chain = RetrievalQA.from_chain_type(
            llm=load_llm(huggingface_repo_id=HUGGINGFACE_REPO_ID,HF_TOKEN=HF_TOKEN),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
        )

        response = qa_chain.invoke({"query": prompt})
        result=response["result"]
        source_documents=response["source_documents"]
        result_to_show=result+str(source_documents)
        st.chat_message('assistant').markdown(result_to_show) 
        st.session_state.messages.append({'role': 'assistant', 'content': result_to_show})

    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
