"""
Embedding utilities for generating and managing vector embeddings.
"""

import numpy as np
from typing import List, Dict, Any, Union, Optional
import os
import logging
from pathlib import Path
import json

# Initialize logger
logger = logging.getLogger(__name__)

# Default model settings
DEFAULT_EMBEDDING_MODEL = os.getenv("DEFAULT_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))  # Dimension for all-MiniLM-L6-v2

try:
    # Try to import sentence-transformers for production use
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
    USING_MOCK = False
    logger.info(f"Initialized embedding model: {DEFAULT_EMBEDDING_MODEL}")
except ImportError:
    # Fall back to mock embeddings for development
    logger.warning("sentence-transformers not available, using mock embeddings")
    USING_MOCK = True


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for the given text.
    
    Args:
        text: Text to generate embedding for
    
    Returns:
        List of float values representing the embedding vector
    """
    if not text.strip():
        # Return zero vector for empty text
        return [0.0] * EMBEDDING_DIMENSION
        
    if USING_MOCK:
        # Generate deterministic mock embedding based on text hash
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Use the hash to seed numpy random for deterministic but unique vectors
        np.random.seed(hash_int)
        mock_embedding = np.random.uniform(-1, 1, EMBEDDING_DIMENSION)
        
        # Normalize to unit length
        norm = np.linalg.norm(mock_embedding)
        if norm > 0:
            mock_embedding = mock_embedding / norm
            
        return mock_embedding.tolist()
    else:
        # Use the actual model
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()


def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score (0-1)
    """
    if not embedding1 or not embedding2:
        return 0.0
        
    # Convert to numpy arrays
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Compute cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return dot_product / (norm1 * norm2)


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to split
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return []
        
    if len(text) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # Adjust end to avoid cutting words
        if end < len(text):
            # Try to find a natural break point
            for break_char in ['. ', '! ', '? ', '\n\n', '\n', ' ']:
                last_break = text.rfind(break_char, start, end)
                if last_break != -1:
                    end = last_break + len(break_char)
                    break
        
        # Add the chunk
        chunks.append(text[start:end].strip())
        
        # Calculate next start position with overlap
        start = end - chunk_overlap
        
        # Ensure we're making progress
        if start >= end:
            start = end
    
    return chunks
