import os
import shutil
from populate_database import split_documents, add_to_chroma, calculate_chunk_ids, clear_database
from langchain_community.document_loaders import PyPDFDirectoryLoader

import gc
import time

def get_or_build_bot_db_path(folder_name: str):
    db_dir = f"chroma_{folder_name}"
    if not os.path.exists(db_dir):
        data_path = os.path.join("data", folder_name)
        document_loader = PyPDFDirectoryLoader(data_path)
        documents = document_loader.load()
        chunks = split_documents(documents)
        add_to_chroma(chunks, persist_directory=db_dir)
    return db_dir

from populate_database import split_documents, calculate_chunk_ids
from langchain_chroma import Chroma
from get_embedding_function import get_embedding_function

def add_to_chroma(chunks, persist_directory):
    db = Chroma(persist_directory=persist_directory, embedding_function=get_embedding_function())
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]
    if new_chunks:
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
