"""
RAG (Retrieval-Augmented Generation) API endpoints.
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import os
import hashlib
import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from api.auth import get_current_active_user, get_current_admin_user
from database.connection import get_db_session
from database.models.user import User
from database.models.document import Document
from database.models.document_chunk import DocumentChunk
from database.models.vector_embedding import VectorEmbedding

router = APIRouter(prefix="/rag", tags=["rag"])

# Make sure data directory exists
DATA_DIR = Path("./data/rag_documents")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Import embedding utilities
from api.system_engine.utils.embedding import generate_embedding, chunk_text, calculate_similarity

# Model definitions
class DocumentMetadata(BaseModel):
    """Metadata for a document"""
    title: str = Field(..., description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    source: Optional[str] = Field(None, description="Document source")
    content_type: Optional[str] = Field(None, description="Document content type")
    date: Optional[str] = Field(None, description="Document date")
    tags: List[str] = Field(default_factory=list, description="Document tags")

class DocumentCreate(BaseModel):
    """Request to create a document"""
    content: str = Field(..., description="Document content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")

class DocumentSearch(BaseModel):
    """Request to search documents"""
    query: str = Field(..., description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    limit: int = Field(10, description="Maximum number of results")

class DocumentResponse(BaseModel):
    """Response with document details"""
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    content_type: str = Field(..., description="Content type")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    tags: List[str] = Field(..., description="Document tags")

class DocumentChunkResponse(BaseModel):
    """Response with document chunk details"""
    id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    chunk_index: int = Field(..., description="Chunk index")
    content: str = Field(..., description="Chunk content")
    created_at: datetime = Field(..., description="Creation timestamp")
    token_count: Optional[int] = Field(None, description="Token count")

class SearchResult(BaseModel):
    """Search result with document and relevance score"""
    document: DocumentResponse = Field(..., description="Document details")
    score: float = Field(..., description="Relevance score")
    content_preview: str = Field(..., description="Content preview")
    
class PaginatedDocuments(BaseModel):
    """Paginated list of documents"""
    items: List[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")

class QueryRequest(BaseModel):
    """Request to query the RAG system"""
    query: str = Field(..., description="Query text")
    collection_id: str = Field("default", description="Collection ID to query")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results")
    
class QueryResponse(BaseModel):
    """Response from a RAG query"""
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    query: str = Field(..., description="Original query")
    collection_id: str = Field(..., description="Collection ID that was queried")
    timestamp: datetime = Field(default_factory=datetime.now)

class CollectionCreate(BaseModel):
    """Request to create a collection"""
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")

class CollectionResponse(BaseModel):
    """Response with collection details"""
    id: str = Field(..., description="Collection ID")
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    document_count: int = Field(..., description="Number of documents in collection")
    created_at: datetime = Field(..., description="Creation timestamp")

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_active_user)
) -> DocumentResponse:
    """Create a new document in the RAG system"""
    # Check if collection exists
    if document.collection_id not in _collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    document_id = str(uuid4())
    created_at = datetime.now()
    
    # Store document
    _documents[document_id] = {
        "id": document_id,
        "content": document.content,
        "metadata": document.metadata.dict(),
        "collection_id": document.collection_id,
        "created_at": created_at,
        "updated_at": created_at,
        "embedding_status": "processing",
        "creator_id": current_user.id
    }
    
    # Update collection document count
    _collections[document.collection_id]["document_count"] += 1
    
    # In a real implementation, this would trigger an async task to embed the document
    # For now, just fake it
    _documents[document_id]["embedding_status"] = "completed"
    
    return DocumentResponse(
        id=document_id,
        metadata=document.metadata,
        collection_id=document.collection_id,
        created_at=created_at,
        updated_at=created_at,
        embedding_status="completed"
    )

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    collection_id: str = Form("default"),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Upload a document file to the RAG system"""
    # Check if collection exists
    if collection_id not in _collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Read file content
    content = await file.read()
    
    # Process tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    document_id = str(uuid4())
    created_at = datetime.now()
    
    # Store document
    _documents[document_id] = {
        "id": document_id,
        "content": content.decode("utf-8"),  # In a real impl, handle different file types
        "metadata": {
            "title": title,
            "author": None,
            "source": file.filename,
            "date": None,
            "tags": tag_list
        },
        "collection_id": collection_id,
        "created_at": created_at,
        "updated_at": created_at,
        "embedding_status": "processing",
        "creator_id": current_user.id
    }
    
    # Update collection document count
    _collections[collection_id]["document_count"] += 1
    
    # In a real implementation, this would trigger an async task to embed the document
    # For now, just fake it
    _documents[document_id]["embedding_status"] = "completed"
    
    return {
        "status": "success",
        "message": f"Document uploaded successfully",
        "document_id": document_id
    }

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str = Path(..., description="Document ID"),
    current_user: User = Depends(get_current_active_user)
) -> DocumentResponse:
    """Get details for a specific document"""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
        
    document = _documents[document_id]
    
    return DocumentResponse(
        id=document_id,
        metadata=DocumentMetadata(**document["metadata"]),
        collection_id=document["collection_id"],
        created_at=document["created_at"],
        updated_at=document["updated_at"],
        embedding_status=document["embedding_status"]
    )

@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
) -> QueryResponse:
    """Query the RAG system"""
    # Check if collection exists
    if request.collection_id not in _collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # In a real implementation, this would query the vector store
    # For now, just return mock results based on the documents we have
    results = []
    for doc_id, document in _documents.items():
        if document["collection_id"] == request.collection_id:
            # Simple substring search for demo purposes
            if request.query.lower() in document["content"].lower():
                results.append({
                    "document_id": doc_id,
                    "metadata": document["metadata"],
                    "content_snippet": document["content"][:200] + "...",
                    "relevance_score": 0.95  # Mock score
                })
                
                # Limit results
                if len(results) >= request.max_results:
                    break
    
    return QueryResponse(
        results=results,
        query=request.query,
        collection_id=request.collection_id
    )

@router.post("/collections", response_model=CollectionResponse)
async def create_collection(
    collection: CollectionCreate,
    current_user: User = Depends(get_current_admin_user)
) -> CollectionResponse:
    """Create a new document collection (admin only)"""
    collection_id = str(uuid4())
    created_at = datetime.now()
    
    _collections[collection_id] = {
        "id": collection_id,
        "name": collection.name,
        "description": collection.description,
        "document_count": 0,
        "created_at": created_at,
        "creator_id": current_user.id
    }
    
    return CollectionResponse(
        id=collection_id,
        name=collection.name,
        description=collection.description,
        document_count=0,
        created_at=created_at
    )

@router.get("/collections", response_model=List[CollectionResponse])
async def list_collections(
    current_user: User = Depends(get_current_active_user)
) -> List[CollectionResponse]:
    """List all document collections"""
    return [
        CollectionResponse(
            id=cid,
            name=coll["name"],
            description=coll["description"],
            document_count=coll["document_count"],
            created_at=coll["created_at"]
        )
        for cid, coll in _collections.items()
    ]

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str = Path(..., description="Document ID"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Delete a document (admin only)"""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = _documents[document_id]
    collection_id = document["collection_id"]
    
    # Delete document
    del _documents[document_id]
    
    # Update collection document count
    _collections[collection_id]["document_count"] -= 1
    
    return {
        "status": "success",
        "message": f"Document {document_id} deleted successfully"
    }
