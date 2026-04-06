'''
RAG (Retrieval-Augmented Generation) module.

Responsibilities:
1. Chunk .md files from the knowledge/ folder by section heading
2. Embed chunks using a local sentence-transformers model (no API key needed)
3. Store and persist embeddings in ChromaDB
4. Retrieve the top-k most relevant chunks for a given query
'''

import os
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Local embedding model — runs entirely on-device, no API key required
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "knowledge_base"
TOP_K = 5  # number of chunks to retrieve per query


def _chunk_markdown(text: str, source: str) -> list[dict]:
    '''
    Split a markdown document into chunks at ## and ### heading boundaries.
    Each chunk carries the heading as a title and the source filename.
    '''
    # Split on lines that start with ## (includes ###, ####, etc.)
    parts = re.split(r'(?=^#{2,}\s)', text, flags=re.MULTILINE)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Extract heading as the first line
        lines = part.splitlines()
        heading = lines[0].lstrip('#').strip() if lines else "intro"
        chunks.append({
            "text": part,
            "heading": heading,
            "source": source,
        })
    return chunks


def build_vector_store(knowledge_dir: str, persist_dir: str) -> chromadb.Collection:
    '''
    Read all .md files in knowledge_dir, chunk them, embed, and store in ChromaDB.
    If the collection already exists and is non-empty, skip re-embedding.
    Returns the ChromaDB collection.
    '''
    client = chromadb.PersistentClient(path=persist_dir)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )

    # Skip re-embedding if collection already populated
    if collection.count() > 0:
        return collection

    md_files = list(Path(knowledge_dir).glob("*.md"))
    all_texts, all_ids, all_metadata = [], [], []

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        chunks = _chunk_markdown(text, source=md_file.name)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{md_file.stem}__chunk_{i}"
            all_ids.append(chunk_id)
            all_texts.append(chunk["text"])
            all_metadata.append({"source": chunk["source"], "heading": chunk["heading"]})

    # Embed and store in batches
    collection.add(documents=all_texts, ids=all_ids, metadatas=all_metadata)
    return collection


def retrieve(collection: chromadb.Collection, query: str, top_k: int = TOP_K) -> str:
    '''
    Embed the query and return the top-k most relevant chunks as a single
    formatted string, ready to be injected into the LLM prompt.
    '''
    results = collection.query(query_texts=[query], n_results=top_k)

    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append(f"[Source: {meta['source']} — {meta['heading']}]\n{doc}")

    return "\n\n---\n\n".join(chunks)