"""Document parsing service for various file formats."""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import tempfile
import os

from markitdown import MarkItDown


class DocumentParserService:
    """Service for parsing documents in various formats."""
    
    def __init__(self):
        self.markitdown = MarkItDown()
        self.supported_extensions = {'.pdf', '.md', '.txt', '.docx', '.pptx', '.xlsx'}
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if the file format is supported."""
        return Path(filename).suffix.lower() in self.supported_extensions
    
    async def parse_documents(self, file_paths: List[str]) -> Dict[str, str]:
        """
        Parse multiple documents and return their text content.
        
        Args:
            file_paths: List of file paths to parse
            
        Returns:
            Dict mapping filename to parsed text content
        """
        documents = {}
        
        print(f"📄 Starting document parsing for {len(file_paths)} files:")
        for file_path in file_paths:
            print(f"   - {Path(file_path).name}")
        
        for file_path in file_paths:
            try:
                filename = Path(file_path).name
                
                if not self.is_supported_file(filename):
                    raise ValueError(f"Unsupported file format: {filename}")
                
                print(f"🔄 Parsing {filename}...")
                content = await self._parse_single_document(file_path)
                documents[filename] = content
                
                # Log content preview
                content_preview = content[:300] + "..." if len(content) > 300 else content
                print(f"✅ {filename} parsed successfully")
                print(f"   📝 Content length: {len(content)} characters")
                print(f"   📖 Preview: {content_preview}")
                print(f"   " + "="*50)
                
            except Exception as e:
                print(f"❌ Error parsing {filename}: {str(e)}")
                raise ValueError(f"Error parsing {filename}: {str(e)}")
        
        print(f"✅ Document parsing completed. Total documents: {len(documents)}")
        return documents
    
    async def _parse_single_document(self, file_path: str) -> str:
        """Parse a single document and return its text content."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.md':
            # Read markdown files directly
            return await self._read_text_file(file_path)
        elif extension == '.txt':
            # Read text files directly
            return await self._read_text_file(file_path)
        elif extension in {'.pdf', '.docx', '.pptx', '.xlsx'}:
            # Use markitdown for PDF and Office documents
            return await self._parse_with_markitdown(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
    
    async def _read_text_file(self, file_path: str) -> str:
        """Read text/markdown files directly."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='cp949') as f:
                return f.read()
    
    async def _parse_with_markitdown(self, file_path: str) -> str:
        """Parse document using markitdown in a thread pool."""
        def _sync_parse():
            try:
                result = self.markitdown.convert(file_path)
                return result.text_content
            except Exception as e:
                raise ValueError(f"markitdown parsing failed: {str(e)}")
        
        # Run markitdown in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_parse)
    
    def get_document_metadata(self, file_path: str) -> Dict[str, str]:
        """Extract basic metadata from document."""
        path = Path(file_path)
        
        metadata = {
            'filename': path.name,
            'extension': path.suffix.lower(),
            'size_bytes': str(path.stat().st_size),
        }
        
        # Add format-specific metadata
        if path.suffix.lower() == '.pdf':
            metadata['parser'] = 'markitdown'
            metadata['type'] = 'PDF Document'
        elif path.suffix.lower() == '.md':
            metadata['parser'] = 'direct'
            metadata['type'] = 'Markdown Document'
        elif path.suffix.lower() == '.txt':
            metadata['parser'] = 'direct'
            metadata['type'] = 'Text Document'
        elif path.suffix.lower() in {'.docx', '.pptx', '.xlsx'}:
            metadata['parser'] = 'markitdown'
            metadata['type'] = 'Office Document'
        
        return metadata