from langchain.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Carga tu FAQ
loader = JSONLoader(file_path="faq_trakii.json", jq_schema=".[].answer")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# Indexa y persiste
vectordb = Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory="knowledge_db")
vectordb.persist()
print("✅ Indexación completada")
