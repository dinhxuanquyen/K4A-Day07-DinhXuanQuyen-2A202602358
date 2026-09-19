from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(self._collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata) if doc.metadata else {}
        metadata["doc_id"] = doc.id
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not records:
            return []
        query_emb = self._embedding_fn(query)
        scored = []
        for r in records:
            score = _dot(query_emb, r["embedding"])
            scored_record = dict(r)
            scored_record["score"] = score
            scored.append(scored_record)
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return
            
        embeddings = [self._embedding_fn(doc.content) for doc in docs]
        
        if self._use_chroma:
            ids = []
            documents = []
            metadatas = []
            for doc in docs:
                # We need unique IDs for each chunk. If doc.id is duplicate, chroma might overwrite.
                # But here we just assume 1 doc = 1 chunk, or doc.id is already unique.
                # Wait, if one doc is chunked before, they might have same doc_id?
                # The lab expects doc.id to be unique here.
                # Actually, wait. We use self._next_index to guarantee uniqueness.
                unique_id = f"{doc.id}_{self._next_index}"
                self._next_index += 1
                ids.append(unique_id)
                documents.append(doc.content)
                m = dict(doc.metadata) if doc.metadata else {}
                m["doc_id"] = doc.id
                metadatas.append(m)
            self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        else:
            for doc, emb in zip(docs, embeddings):
                record = self._make_record(doc)
                # Assign a unique internal id just in case
                record["_internal_id"] = self._next_index
                self._next_index += 1
                record["embedding"] = emb
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self.search_with_filter(query, top_k=top_k, metadata_filter=None)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma:
            query_emb = self._embedding_fn(query)
            where = metadata_filter if metadata_filter else None
            results = self._collection.query(query_embeddings=[query_emb], n_results=top_k, where=where)
            ret = []
            if results and results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    ret.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": results["distances"][0][i]
                    })
            return ret
        else:
            filtered = self._store
            if metadata_filter:
                filtered = []
                for r in self._store:
                    m = r.get("metadata", {})
                    match = all(m.get(k) == v for k, v in metadata_filter.items())
                    if match:
                        filtered.append(r)
            return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma:
            before = self._collection.count()
            self._collection.delete(where={"doc_id": doc_id})
            return self._collection.count() < before
        else:
            before = len(self._store)
            self._store = [r for r in self._store if r.get("metadata", {}).get("doc_id") != doc_id]
            return len(self._store) < before
