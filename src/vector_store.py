import os
import logging
import numpy as np
from langchain_core.embeddings import Embeddings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiLangChainEmbeddings(Embeddings):
    """
    Adapter class to bridge our AIEngine with LangChain's embeddings interface.
    """
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # To handle API rate limits and batches, we do a simple batch processing
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        try:
            return self.ai_engine.get_embeddings_batch(texts)
        except Exception as e:
            # Fallback to list comprehension if batch fails
            logger.warning(f"Batch embedding failed, falling back to individual embeddings. Error: {e}")
            return [self.ai_engine.get_embedding(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.ai_engine.get_embedding(text)


class SimpleVectorStore:
    """
    A pure NumPy-based Vector Store fallback.
    Requires no C-extensions (like FAISS) and runs successfully on all environments.
    """
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.vectors = []
        self.texts = []
        self.metadatas = []

    def add_texts(self, texts: list[str], metadatas: list[dict] = None):
        if not texts:
            return
        embeddings = [self.ai_engine.get_embedding(t) for t in texts]
        self.vectors.extend(embeddings)
        self.texts.extend(texts)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{} for _ in texts])
            
        logger.info(f"Added {len(texts)} texts to SimpleVectorStore (total: {len(self.texts)})")

    def similarity_search(self, query: str, k: int = 4) -> list[dict]:
        if not self.vectors:
            return []
            
        query_vector = self.ai_engine.get_embedding(query)
        
        # Calculate cosine similarity manually using NumPy
        A = np.array(self.vectors)
        B = np.array(query_vector)
        
        # Cosine similarity formula: dot(A, B) / (norm(A) * norm(B))
        dot_products = np.dot(A, B)
        norms_A = np.linalg.norm(A, axis=1)
        norm_B = np.linalg.norm(B)
        
        # Prevent division by zero
        norms_A[norms_A == 0] = 1e-10
        if norm_B == 0:
            norm_B = 1e-10
            
        similarities = dot_products / (norms_A * norm_B)
        
        # Get top K indices sorted by descending similarity
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_k_indices:
            results.append({
                "text": self.texts[idx],
                "metadata": self.metadatas[idx],
                "score": float(similarities[idx])
            })
            
        return results


class SmartEduVectorStore:
    """
    Main manager for the vector database.
    Attempts to use FAISS via LangChain, but falls back to SimpleVectorStore if FAISS fails.
    """
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.embeddings_adapter = GeminiLangChainEmbeddings(ai_engine)
        self.use_faiss = False
        self.faiss_db = None
        self.fallback_db = None
        
        # Try to import FAISS to see if it is available
        try:
            from langchain_community.vectorstores import FAISS
            self.FAISS_class = FAISS
            self.use_faiss = True
            logger.info("FAISS vector store imported successfully.")
        except ImportError:
            logger.warning("FAISS library not found. Falling back to NumPy SimpleVectorStore.")
            self.fallback_db = SimpleVectorStore(ai_engine)

    def initialize_db(self, texts: list[str], metadatas: list[dict] = None):
        """
        Creates a new vector store index from chunks.
        """
        if not texts:
            return
            
        # Ensure metadata matches lengths
        if not metadatas:
            metadatas = [{"source_index": i} for i in range(len(texts))]
            
        if self.use_faiss:
            try:
                logger.info("Initializing FAISS Vector Store...")
                self.faiss_db = self.FAISS_class.from_texts(
                    texts=texts,
                    embedding=self.embeddings_adapter,
                    metadatas=metadatas
                )
                logger.info("FAISS Vector Store initialized successfully.")
            except Exception as e:
                logger.error(f"FAISS initialization failed: {e}. Falling back to SimpleVectorStore.")
                self.use_faiss = False
                self.fallback_db = SimpleVectorStore(self.ai_engine)
                self.fallback_db.add_texts(texts, metadatas)
        else:
            logger.info("Initializing NumPy SimpleVectorStore...")
            self.fallback_db = SimpleVectorStore(self.ai_engine)
            self.fallback_db.add_texts(texts, metadatas)

    def search(self, query: str, k: int = 4) -> list[dict]:
        """
        Performs similarity search and returns a standard list of chunk dicts:
        [{'text': '...', 'metadata': {...}}]
        """
        if self.use_faiss and self.faiss_db is not None:
            try:
                docs = self.faiss_db.similarity_search(query, k=k)
                return [
                    {
                        "text": doc.page_content,
                        "metadata": doc.metadata
                    } for doc in docs
                ]
            except Exception as e:
                logger.error(f"FAISS search failed: {e}. Attempting fallback DB search.")
                if self.fallback_db is not None:
                    return self.fallback_db.similarity_search(query, k=k)
                return []
        elif self.fallback_db is not None:
            return self.fallback_db.similarity_search(query, k=k)
        else:
            logger.warning("No vector store database initialized.")
            return []
