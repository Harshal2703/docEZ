
# docEZ

RAG (Retrieval Augmented Generation) application in which user uploads his documents and can chat with the documents using llm
it uses vector embeddings for semantic searching after that query and context from semantic search is passed through llm to generate the answer.





## Download Models

Download ollama from https://ollama.com/

in terminal run following commands

```bash
  ollama run llama3
```

```bash
  ollama run mxbai-embed-large
```
## Installations


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

```bash
  streamlit run app.py
```

