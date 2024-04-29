
# docEZ

docEZ is an innovative RAG (Retrieval Augmented Generation) application that allows users to upload their documents and engage in conversations with them using advanced language models (LLMs). Leveraging vector embeddings for semantic searching, docEZ enables efficient retrieval of information from uploaded documents. The application seamlessly integrates query and context from semantic searches through LLMs to generate accurate responses.





## Download Models

To get started with docEZ, you can download the necessary models from ollama.com. After downloading, you can use the following commands in your terminal:

```bash
  ollama pull llama3
```

```bash
  ollama pull mxbai-embed-large
```
## Installations
To set up docEZ on your local machine, follow these installation steps:

```bash
  python -m venv docEZ_env
```
```bash
  docEZ_env/Scripts/Activate.ps1
```
```bash
  pip install -r requirements.txt
```


## Run
Once installed, you can run docEZ using the following command:
```bash
  streamlit run app.py
```
Experience the convenience of interacting with your documents in a whole new way with docEZ!
