import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import ollama
import chromadb


def clearMsg():
    st.session_state.messages = []

st.set_page_config(page_title="docEZ")
st.header("Ask your PDF...")
pdf = st.file_uploader("Upload your PDF", type="pdf")
st.button("Clear chat", type="primary" , on_click=clearMsg)
def createChunks(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=100, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def createEmbeddingsFromChunk(collection, chunks):
    for i, d in enumerate(chunks):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(ids=[str(i)], embeddings=[embedding], documents=[d])



if pdf is not None:
    chunks = createChunks(pdf)
    client = chromadb.Client()
    collection = None
    for i in client.list_collections():
        if i.name == pdf.name:
            collection = client.get_collection(name=pdf.name)
    if not collection:
        collection = client.create_collection(name=pdf.name)
        createEmbeddingsFromChunk(collection, chunks)
        print(f"embeddings created! : {pdf.name}")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"])
        else:
            st.chat_message(msg["role"], avatar="Windows 10 Anniversary Update").write(msg["content"])


    if query := st.chat_input():
        response = ollama.embeddings(prompt=query, model="mxbai-embed-large")
        results = collection.query(
            query_embeddings=[response["embedding"]], n_results=3
        )
        context = ""
        for i in results["documents"][0]:
            context += i

        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user", avatar="🧑‍💻").write(query)
        st.session_state["full_message"] = ""
        def generate_response():
            prompt=f"'''Using this data: {context}'''. '''Respond to this prompt: {query}''' don't add anything extra from your side if you are unable to find answer of query in context just say out of context don't generate anything from your side"
            response = ollama.chat(model='llama3', stream=True, messages=[{'role': 'user', 'content': prompt}])
            for partial_resp in response:
                token = partial_resp["message"]["content"]
                st.session_state["full_message"] += token
                yield token
        st.chat_message("assistant", avatar="🤖").write_stream(generate_response)
        st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_message"]})


