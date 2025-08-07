import httpx
import logging
from typing import Optional, List, Dict, Any, BinaryIO
from config import settings
from schemas import LightRAGQueryRequest, LightRAGQueryResponse, LightRAGUploadResponse
import json

# Set up logging
logger = logging.getLogger(__name__)


class LightRAGService:
    """
    Service class for interacting with the LightRAG Server.
    
    This class handles all HTTP communication with the LightRAG server,
    including queries, document uploads, and other operations.
    """
    
    def __init__(self):
        self.base_url = settings.lightrag_server_url.rstrip('/')
        self.api_key = settings.lightrag_api_key
        self.timeout = 300.0  # 5 minutes timeout for long operations
        
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for LightRAG API requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers
    
    def _get_upload_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for file upload requests.
        
        Returns:
            Dictionary of HTTP headers for file uploads
        """
        headers = {
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers
    
    async def query(
        self, 
        query: str,
        mode: str = "hybrid",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> LightRAGQueryResponse:
        """
        Send a query to the LightRAG server.
        
        Args:
            query: The query text
            mode: Query mode (local, global, hybrid, naive, mix, bypass)
            conversation_history: Previous conversation messages
            **kwargs: Additional query parameters
            
        Returns:
            LightRAGQueryResponse with the AI response
            
        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If the response is invalid
        """
        url = f"{self.base_url}/query"
        
        # Build the request payload
        payload = {
            "query": query,
            "mode": mode,
            "user_prompt": """
At the end of the response, always include a section titled exactly "References", regardless of the language of the main response. Do not translate or change this heading. It must always appear as "References" in English.

Format each reference in **Markdown link format**, using the following structure:
[KG/DC/KG+DC] [file_name](http://localhost:8000/api/documents/file_name)

Example:
[DC] [Rapor (1)_3816aba6.pdf](http://localhost:8000/api/documents/Rapor%20%281%29_3816aba6.pdf)

"""
        }
        
        if conversation_history:
            payload["conversation_history"] = conversation_history
            
        # Add any additional parameters
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Sending query to LightRAG: {query[:100]}...")
                
                # Add API key as query parameter if available
                params = {}
                if self.api_key:
                    params["api_key_header_value"] = self.api_key
                
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info("Query completed successfully")
                
                return LightRAGQueryResponse(response=result.get("response", ""))
                
        except httpx.HTTPError as e:
            logger.error(f"LightRAG query failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during LightRAG query: {str(e)}")
            raise
    
    async def upload_document(
        self, 
        file_content: bytes, 
        filename: str
    ) -> LightRAGUploadResponse:
        """
        Upload a document to LightRAG server.
        
        Args:
            file_content: The file content as bytes
            filename: Name of the file
            
        Returns:
            LightRAGUploadResponse with upload status
            
        Raises:
            httpx.HTTPError: If the upload fails
        """
        url = f"{self.base_url}/documents/upload"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Uploading document to LightRAG: {filename}")
                
                # Prepare the file for upload
                files = {
                    "file": (filename, file_content, "application/octet-stream")
                }
                
                # Add API key as query parameter if available
                params = {}
                if self.api_key:
                    params["api_key_header_value"] = self.api_key
                
                response = await client.post(
                    url,
                    files=files,
                    headers=self._get_upload_headers(),
                    params=params
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Document upload completed: {filename}")
                
                return LightRAGUploadResponse(
                    status=result.get("status", "success"),
                    message=result.get("message", "Upload completed")
                )
                
        except httpx.HTTPError as e:
            logger.error(f"Document upload failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during document upload: {str(e)}")
            raise
    
    async def insert_text(
        self, 
        text: str, 
        file_source: Optional[str] = None
    ) -> LightRAGUploadResponse:
        """
        Insert text directly into LightRAG system.
        
        Args:
            text: The text content to insert
            file_source: Optional source identifier
            
        Returns:
            LightRAGUploadResponse with insertion status
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/documents/text"
        
        payload = {"text": text}
        if file_source:
            payload["file_source"] = file_source
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Inserting text to LightRAG: {len(text)} characters")
                
                # Add API key as query parameter if available
                params = {}
                if self.api_key:
                    params["api_key_header_value"] = self.api_key
                
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info("Text insertion completed")
                
                return LightRAGUploadResponse(
                    status=result.get("status", "success"),
                    message=result.get("message", "Text inserted successfully")
                )
                
        except httpx.HTTPError as e:
            logger.error(f"Text insertion failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during text insertion: {str(e)}")
            raise
    
    async def scan_documents(self) -> Dict[str, Any]:
        """
        Trigger document scanning on LightRAG server.
        
        Returns:
            Dictionary with scan status
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/documents/scan"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("Triggering document scan on LightRAG")
                
                # Add API key as query parameter if available
                params = {}
                if self.api_key:
                    params["api_key_header_value"] = self.api_key
                
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info("Document scan triggered successfully")
                
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"Document scan failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during document scan: {str(e)}")
            raise
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current pipeline status from LightRAG server.
        
        Returns:
            Dictionary with pipeline status information
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/documents/pipeline_status"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Add API key as query parameter if available
                params = {}
                if self.api_key:
                    params["api_key_header_value"] = self.api_key
                
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Pipeline status request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting pipeline status: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if LightRAG server is healthy.
        
        Returns:
            Dictionary with health status
            
        Raises:
            httpx.HTTPError: If the health check fails
        """
        url = f"{self.base_url}/health"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Add API key as query parameter if available
                params = {}
                if self.api_key:
                    params["api_key_header_value"] = self.api_key
                
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"LightRAG health check failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during health check: {str(e)}")
            raise


# Global service instance
lightrag_service = LightRAGService() 