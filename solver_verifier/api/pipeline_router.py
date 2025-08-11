"""FastAPI router for pipeline operations."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import uuid
from pathlib import Path

from ..models.business_requirement import RequirementSet
from ..models.agent_config import SystemSettings
from ..services.pipeline_service import PipelineService
from ..services.prompt_loader import PromptLoader
from ..services.websocket_manager import websocket_manager


# Router for pipeline endpoints
router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# Global settings instance (would be properly configured in real app)
settings = SystemSettings()
pipeline_service = PipelineService(settings)
prompt_loader = PromptLoader()


@router.post("/process", response_model=RequirementSet)
async def process_rfp_documents(
    files: List[UploadFile] = File(..., description="RFP documents to process"),
    set_name: Optional[str] = Form(None, description="Name for the requirement set"),
    set_description: Optional[str] = Form(None, description="Description for the requirement set")
):
    """
    Process RFP documents through the 6-stage pipeline.
    
    Uploads multiple files and processes them to extract business requirements
    using the Analyzer-Verifier pipeline.
    """
    
    # Validate file uploads
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file formats
    supported_formats = pipeline_service.get_supported_formats()
    for file in files:
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in supported_formats:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(supported_formats)}"
                )
    
    # Save uploaded files to temporary location
    temp_files = []
    try:
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")
            
            # Create temporary file with original extension
            suffix = Path(file.filename).suffix
            with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        # Process documents through pipeline
        result = await pipeline_service.process_rfp_documents(
            document_paths=temp_files,
            set_name=set_name,
            set_description=set_description
        )
        
        return result
        
    except Exception as e:
        import traceback
        error_detail = f"Processing error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(f"❌ Pipeline processing error: {error_detail}")  # Add console logging
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass  # Ignore cleanup errors


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time pipeline progress updates."""
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            # Echo back ping messages to keep connection alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, session_id)


@router.post("/process-realtime")
async def process_rfp_documents_realtime(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="RFP documents to process"),
    set_name: Optional[str] = Form(None, description="Name for the requirement set"),
    set_description: Optional[str] = Form(None, description="Description for the requirement set")
):
    """
    Process RFP documents with real-time progress updates via WebSocket.
    
    Returns a session_id immediately and processes documents in the background.
    Connect to WebSocket at /pipeline/ws/{session_id} to receive real-time updates.
    """
    
    # Validate file uploads
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file formats
    supported_formats = pipeline_service.get_supported_formats()
    for file in files:
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in supported_formats:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(supported_formats)}"
                )
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded files to temporary location
    temp_files = []
    try:
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")
            
            # Create temporary file with original extension
            suffix = Path(file.filename).suffix
            with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        # Start background processing
        background_tasks.add_task(
            _process_documents_background,
            temp_files,
            session_id,
            set_name,
            set_description
        )
        
        return JSONResponse(content={
            "session_id": session_id,
            "message": "Processing started. Connect to WebSocket for real-time updates.",
            "websocket_url": f"/pipeline/ws/{session_id}",
            "files_uploaded": len(temp_files)
        })
        
    except Exception as e:
        # Clean up temporary files on error
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


async def _process_documents_background(
    temp_files: List[str],
    session_id: str,
    set_name: Optional[str],
    set_description: Optional[str]
):
    """Background task to process documents with progress updates."""
    try:
        # Process documents through pipeline
        result = await pipeline_service.process_rfp_documents_with_progress(
            document_paths=temp_files,
            session_id=session_id,
            set_name=set_name,
            set_description=set_description
        )
        
        print(f"✅ Background processing completed for session: {session_id}")
        
    except Exception as e:
        print(f"❌ Background processing failed for session {session_id}: {str(e)}")
        # Send error to WebSocket if still connected
        from ..models.progress import ProgressUpdate
        from datetime import datetime
        error_update = ProgressUpdate(
            type="error",
            session_id=session_id,
            timestamp=datetime.now(),
            data={"error": str(e), "details": "Background processing failed"}
        )
        await websocket_manager.send_update(session_id, error_update)
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass  # Ignore cleanup errors


@router.get("/status/{set_id}")
async def get_pipeline_status(set_id: str):
    """Get the current status of a pipeline processing job."""
    try:
        status = await pipeline_service.get_pipeline_status(set_id)
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Set not found: {str(e)}")


@router.post("/configure/analyzer")
async def configure_analyzer_prompt(
    system_prompt: str = Form(..., description="System prompt for the Analyzer agent")
):
    """
    Configure the system prompt for the Analyzer agent.
    
    This endpoint allows updating the system prompt that guides the Analyzer's
    behavior during requirement extraction.
    """
    try:
        settings.analyzer_system_prompt = system_prompt
        return JSONResponse(content={
            "message": "Analyzer system prompt updated successfully",
            "prompt_length": len(system_prompt)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.post("/configure/verifier")
async def configure_verifier_prompt(
    system_prompt: str = Form(..., description="System prompt for the Verifier agent")
):
    """
    Configure the system prompt for the Verifier agent.
    
    This endpoint allows updating the system prompt that guides the Verifier's
    behavior during requirement verification.
    """
    try:
        settings.verifier_system_prompt = system_prompt
        return JSONResponse(content={
            "message": "Verifier system prompt updated successfully",
            "prompt_length": len(system_prompt)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/configure")
async def get_current_configuration():
    """
    Get the current configuration for both Analyzer and Verifier agents.
    """
    return JSONResponse(content={
        "analyzer_prompt_configured": bool(settings.analyzer_system_prompt),
        "verifier_prompt_configured": bool(settings.verifier_system_prompt),
        "analyzer_prompt_length": len(settings.analyzer_system_prompt),
        "verifier_prompt_length": len(settings.verifier_system_prompt),
        "pipeline_config": {
            "max_iterations": settings.pipeline_config.max_iterations,
            "acceptance_threshold": settings.pipeline_config.acceptance_threshold,
            "enable_stage_4_review": settings.pipeline_config.enable_stage_4_review
        }
    })


@router.post("/configure/pipeline")
async def configure_pipeline_settings(
    max_iterations: Optional[int] = Form(None, description="Maximum iterations for verification loop", ge=1, le=10),
    acceptance_threshold: Optional[int] = Form(None, description="Consecutive passes needed for acceptance", ge=1, le=5),
    enable_stage_4_review: Optional[bool] = Form(None, description="Enable optional human review in stage 4")
):
    """
    Configure pipeline processing settings.
    """
    try:
        if max_iterations is not None:
            settings.pipeline_config.max_iterations = max_iterations
        if acceptance_threshold is not None:
            settings.pipeline_config.acceptance_threshold = acceptance_threshold
        if enable_stage_4_review is not None:
            settings.pipeline_config.enable_stage_4_review = enable_stage_4_review
        
        return JSONResponse(content={
            "message": "Pipeline configuration updated successfully",
            "current_config": {
                "max_iterations": settings.pipeline_config.max_iterations,
                "acceptance_threshold": settings.pipeline_config.acceptance_threshold,
                "enable_stage_4_review": settings.pipeline_config.enable_stage_4_review
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/stages")
async def get_pipeline_stages():
    """
    Get information about the 6 pipeline stages.
    """
    return JSONResponse(content={
        "stages": [
            {
                "stage": 1,
                "name": "Initial BR Draft Generation",
                "description": "Extract BR candidates with direct citations and location info",
                "performer": "Analyzer"
            },
            {
                "stage": 2,
                "name": "Self-improvement Pass",
                "description": "Search for missing, ambiguous, or duplicate requirements",
                "performer": "Analyzer"
            },
            {
                "stage": 3,
                "name": "Verifier Verification & Bug Report",
                "description": "Verify traceability, semantic consistency, atomicity, and schema compliance",
                "performer": "Verifier"
            },
            {
                "stage": 4,
                "name": "Bug Report Review (Optional)",
                "description": "Optional human or AI review of verification results",
                "performer": "Human/AI Reviewer"
            },
            {
                "stage": 5,
                "name": "Bug Report-based Improvement",
                "description": "Fix issues identified by verifier",
                "performer": "Analyzer"
            },
            {
                "stage": 6,
                "name": "Accept/Reject Decision",
                "description": "Final decision based on verification results",
                "performer": "System"
            }
        ],
        "verification_loop": "Stages 3-5 repeat until acceptance criteria met or max iterations reached",
        "supported_formats": pipeline_service.get_supported_formats()
    })


@router.post("/prompts/load")
async def load_prompts_from_files():
    """
    Load system prompts from files in the prompts/ directory.
    """
    try:
        analyzer_prompt = prompt_loader.load_analyzer_prompt()
        verifier_prompt = prompt_loader.load_verifier_prompt()
        
        if analyzer_prompt:
            settings.analyzer_system_prompt = analyzer_prompt
        if verifier_prompt:
            settings.verifier_system_prompt = verifier_prompt
            
        return JSONResponse(content={
            "message": "Prompts loaded from files",
            "analyzer_loaded": bool(analyzer_prompt),
            "verifier_loaded": bool(verifier_prompt),
            "analyzer_length": len(analyzer_prompt) if analyzer_prompt else 0,
            "verifier_length": len(verifier_prompt) if verifier_prompt else 0
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading prompts: {str(e)}")


@router.post("/prompts/save")
async def save_current_prompts():
    """
    Save current system prompts to files.
    """
    try:
        if settings.analyzer_system_prompt:
            prompt_loader.save_analyzer_prompt(settings.analyzer_system_prompt)
        if settings.verifier_system_prompt:
            prompt_loader.save_verifier_prompt(settings.verifier_system_prompt)
            
        return JSONResponse(content={
            "message": "Prompts saved to files",
            "analyzer_saved": bool(settings.analyzer_system_prompt),
            "verifier_saved": bool(settings.verifier_system_prompt)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving prompts: {str(e)}")