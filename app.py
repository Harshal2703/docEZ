import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import ollama
import chromadb
import os
from docx import Document
import re
import json
import uuid


st.set_page_config(page_title="docEZ",page_icon="logo.png",layout="wide")
abc, xyz , _= st.sidebar.columns(3,gap="small")
code = """
        <style>
            .big-font {
                font-size:50px !important;
                font-weight: bold;
            }
        </style>
"""
st.html(code)
abc.image(image="logo.png",use_column_width=True)
xyz.markdown('<h1 class="big-font">docEZ</h1>', unsafe_allow_html=True)


def getUploadedFileInfo():
    client = chromadb.PersistentClient(path="E:\Mini Projects\Mini Project (Sem 6)\docEZ\embeddings")
    collection = client.get_collection(name="uploadedFilesInfo")
    filesInfo = collection.get()
    filesInfo = [json.loads(i) for i in filesInfo["documents"]]
    return filesInfo


def loadChat(info):
    html = f"""<h2>chat with {info['ogFileName']}</h2>"""
    st.markdown(html, unsafe_allow_html=True)
    st.session_state["currentCollection"] = info
    chats = []
    with open(st.session_state["currentCollection"]["chatFile"] , "r") as f:
        chats = json.load(f)
    for i in chats:
        if i["role"] == "user":
            st.chat_message(i["role"], avatar="🧑‍💻").write(i["content"])
        else:
            st.chat_message(i["role"], avatar="logo.png").write(i["content"])   


if "currentCollection" not in st.session_state:
    filesInfo = getUploadedFileInfo()
    if filesInfo:
        loadChat(filesInfo[0])
    else:
        st.session_state["currentCollection"] = None
    

def showDeleteChatBtn():
    if st.session_state["currentCollection"] != None:
        deleteChat = st.button('delete chats')    
        if deleteChat and st.session_state["currentCollection"]:
            chat = [{"role" : "assistant" , "content" : f"ask me anything related to {st.session_state['currentCollection']['ogFileName']}"}]
            with open(st.session_state["currentCollection"]["chatFile"] , "w") as f:
                json.dump(chat, f, indent=4)


query = st.chat_input("Say something")
if query and st.session_state["currentCollection"]:
    loadChat(info=st.session_state["currentCollection"])
    client = chromadb.PersistentClient(path="E:\Mini Projects\Mini Project (Sem 6)\docEZ\embeddings")
    collection = client.get_collection(name=st.session_state["currentCollection"]["fileName"])
    response = ollama.embeddings(prompt=query, model="mxbai-embed-large")
    results = collection.query(query_embeddings=[response["embedding"]], n_results=3)
    context = ""
    for i in results["documents"][0]:
        context += i
    st.chat_message("user", avatar="🧑‍💻").write(query)
    st.session_state["full_message"] = ""
    def generate_response():
        prompt = f"'''Using this data: {context}'''. '''Respond to this prompt: {query}''' don't add anything extra from your side if you are unable to find answer of query in context just say out of context don't generate anything from your side"
        response = ollama.chat(model="llama3", stream=True, messages=[{"role": "user", "content": prompt}])
        for partial_resp in response:
            token = partial_resp["message"]["content"]
            st.session_state["full_message"] += token
            yield token
    st.chat_message("assistant", avatar="logo.png").write_stream(generate_response)
    fileLocation = st.session_state["currentCollection"]["chatFile"]
    chats = []
    with open(fileLocation , "r") as f:
        chats = json.load(f)
    chats.append({"role": "user", "content": query})
    chats.append({"role": "assistant", "content": st.session_state["full_message"]})
    with open(fileLocation , "w") as f:
        json.dump(chats, f, indent=4)


def saveUploadedFile(uploadedFile):
    path = os.path.join(os.getcwd(), "input_files", uploadedFile.name)
    with open(path, "wb") as f:
        f.write(uploadedFile.getvalue())
    return path


def extractTextFromPdf(filePath):
    text = ""
    with open(filePath, "rb") as pdf:
        pdfReader = PdfReader(pdf)
        for page in pdfReader.pages:
            text += page.extract_text()
    return text


def extractTextFromDocx(filePath):
    doc = Document(filePath)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)


def extractTextFromTxt(filePath):
    with open(filePath, "r") as f:
        text = f.read()
    return text


def extractTextFromFile(filePath):
    _, fileExtension = os.path.splitext(filePath)
    if fileExtension == ".pdf":
        return extractTextFromPdf(filePath)
    elif fileExtension == ".docx":
        return extractTextFromDocx(filePath)
    elif fileExtension == ".txt":
        return extractTextFromTxt(filePath)


def createChunksFromText(text):
    textSplitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=100, length_function=len
    )
    return textSplitter.split_text(text)


def createEmbeddingsFromChunk(collection, chunks):
    for i, d in enumerate(chunks):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(ids=[str(i)], embeddings=[embedding], documents=[d])


def validateCollectionName(collectionName):
    collectionName = collectionName.strip()
    collectionName = re.sub(r"[^\w\-]", "", collectionName)
    collectionName = re.sub(r"\.{2,}", "", collectionName)
    if collectionName.startswith(".") or collectionName.endswith("."):
        collectionName = collectionName.replace(".", "_")
    if len(collectionName) > 63:
        collectionName = collectionName[:63]
    if len(collectionName) < 3:
        collectionName = collectionName.ljust(3, "0")
    if not collectionName[0].isalnum():
        collectionName = "A" + collectionName[1:]
    if not collectionName[-1].isalnum():
        collectionName = collectionName[:-1] + "A"
    return collectionName


def deleteFile(j):
    client = chromadb.PersistentClient(path="E:\Mini Projects\Mini Project (Sem 6)\docEZ\embeddings")
    client.delete_collection(name=j["fileName"])
    collection = client.get_collection(name="uploadedFilesInfo")
    collection.delete(ids=[j["id"]])
    st.session_state["currentCollection"] = None
    st.rerun()


def displayStoredFiles():
    filesInfo = getUploadedFileInfo()
    col1, col2= st.sidebar.columns(2,gap="small")
    for i, j in enumerate(filesInfo):
        if col1.button(label=j["ogFileName"], key=i+1000000,use_container_width=True):
            loadChat(j)
        if col2.button(f"🗑️", key=i):
            deleteFile(j)
    
        
def hardClean():
    client = chromadb.PersistentClient(path="E:\Mini Projects\Mini Project (Sem 6)\docEZ\embeddings")
    t = [i.name for i in client.list_collections()]
    for i in t:
        client.delete_collection(name=i)
    client.create_collection(name="uploadedFilesInfo")
    st.rerun()

    
def main():
    client = chromadb.PersistentClient(
        path="E:\Mini Projects\Mini Project (Sem 6)\docEZ\embeddings"
    )
    collectionList = [i.name for i in client.list_collections()]
    st.sidebar.title("File Uploader")
    uploadedFile = st.sidebar.file_uploader(
        "Choose a file", type=["txt", "docx", "pdf"]
    )
    if uploadedFile is not None:
        fileName = validateCollectionName(collectionName=uploadedFile.name)
        if fileName not in collectionList:
            collection = client.create_collection(name=fileName)
            path = saveUploadedFile(uploadedFile=uploadedFile)
            text = extractTextFromFile(filePath=path)
            chunks = createChunksFromText(text=text)
            createEmbeddingsFromChunk(collection, chunks)
            collection = client.get_or_create_collection(name="uploadedFilesInfo")
            info = {
                "id" : str(uuid.uuid1()),
                "fileName": fileName,
                "ogFileName": uploadedFile.name,
                "pathToFile": path,
                "chatFile": os.path.join(os.getcwd() , "chats" , f"chat_{fileName}.json") 
            }
            json_str = json.dumps(info)
            collection.add(ids=[info["id"]], documents=[json_str])
            chat = [{"role" : "assistant" , "content" : f"ask me anything related to {uploadedFile.name}"}]
            with open(info["chatFile"] , "w") as f:
                json.dump(chat, f, indent=4)
    if st.sidebar.button(label="hard clean"):
        hardClean()


if __name__ == "__main__":
    main()
    displayStoredFiles()
    showDeleteChatBtn()
