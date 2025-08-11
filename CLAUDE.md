# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the `solver-verifier` project - an RFP business requirements extraction system using a 6-stage Analyzer-Verifier pipeline. Built with Python, FastAPI, and uv package management. Inspired by Gemini 2.5 Pro's IMO 2025 approach, it uses dual-agent architecture to extract accurate business requirements from RFP documents, interviews, and related materials.

## Development Commands

### Package Management (uv)
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package>

# Add development dependency  
uv add --dev <package>

# Run Python with project dependencies
uv run python <script.py>

# Activate virtual environment
source .venv/bin/activate  # or use: uv shell
```

### Running the Application
```bash
# Development server (with auto-reload)
uv run uvicorn main:app --reload

# Production server
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Direct Python execution
uv run python main.py
```

### Testing
```bash
# Add pytest as dev dependency first
uv add --dev pytest pytest-cov pytest-asyncio httpx

# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/test_specific.py

# Run with coverage
uv run pytest --cov=solver_verifier

# Run tests with verbose output
uv run pytest -v
```

## Project Architecture

### Directory Structure
```
solver-verifier/
├── solver_verifier/        # Main application package
│   ├── api/                # FastAPI routes and endpoints
│   ├── models/             # Pydantic models and data structures
│   └── services/           # Business logic and solver implementations
├── tests/                  # Test files
├── main.py                 # FastAPI application entry point
└── pyproject.toml         # uv/Python project configuration
```

### 6-Stage Pipeline Architecture

The system implements a sophisticated dual-agent pipeline:

1. **Stage 1: Initial BR Draft** - Analyzer extracts requirements with citations
2. **Stage 2: Self-improvement** - Analyzer refines and enhances the draft  
3. **Stage 3: Verification** - Verifier validates requirements and generates bug reports
4. **Stage 4: Review (Optional)** - Human/AI review of verification results
5. **Stage 5: Bug Fixes** - Analyzer addresses verification issues
6. **Stage 6: Accept/Reject** - Final decision based on quality metrics

### Core Components

- **PipelineService**: Orchestrates the complete 6-stage process
- **AnalyzerService**: Extracts and refines business requirements (equivalent to Solver)
- **VerifierService**: Validates requirements against source documents (equivalent to Verifier)
- **Business Requirement Models**: Comprehensive data models with traceability and metrics

### Key API Endpoints

- `POST /pipeline/process`: Upload RFP documents for processing
- `GET /pipeline/status/{set_id}`: Check processing status
- `POST /pipeline/configure/analyzer`: Set Analyzer system prompt
- `POST /pipeline/configure/verifier`: Set Verifier system prompt  
- `GET /pipeline/stages`: Get pipeline stage information

### Data Models

- **BusinessRequirement**: Core requirement with citations, stakeholders, acceptance criteria
- **RequirementSet**: Complete set with verification issues and metrics
- **VerificationIssue**: Issues found during verification with severity levels
- **CoverageMetrics**: Quality metrics (recall, precision, traceability, etc.)

### Agent Configuration

System prompts are automatically loaded from files at startup:
- **Auto-loading**: `prompts/analyzer_prompt.txt` and `prompts/verifier_prompt.txt` are loaded automatically
- **Manual override**: Use API endpoints to update prompts at runtime
- **Environment override**: Set `ANALYZER_SYSTEM_PROMPT` and `VERIFIER_SYSTEM_PROMPT` env vars

### Technology Stack
- **Python 3.10+**: Core language
- **FastAPI**: Async web framework for building APIs
- **Uvicorn**: ASGI server for serving FastAPI applications
- **uv**: Fast Python package manager and virtual environment manager
- **Pydantic**: Data validation and serialization using Python type annotations
- **Pydantic Settings**: Configuration management

### Frontend Development

The project includes a React-based web interface:

```bash
# Build and serve frontend
./scripts/build-frontend.sh
uv run uvicorn main:app --reload

# Visit http://localhost:8000
```

**Frontend Features**:
- File upload with drag-and-drop (PDF, MD, TXT, DOCX, PPTX, XLSX)
- Real-time processing status
- Interactive results display with expandable requirements
- Quality metrics visualization
- Responsive design with Tailwind CSS

### Document Processing

**Supported Formats**:
- **PDF**: Parsed using markitdown library for text extraction
- **Markdown (.md)**: Direct text parsing with UTF-8/CP949 encoding support
- **Text (.txt)**: Direct text parsing
- **Office**: DOCX, PPTX, XLSX via markitdown

**Processing Pipeline**:
1. File validation and format checking
2. Document parsing with appropriate parser
3. Text extraction and content preparation
4. 6-stage Analyzer-Verifier pipeline execution

### Development Notes
- Virtual environment is automatically managed by uv in `.venv/`
- Dependencies are locked in `uv.lock` for reproducible builds
- System prompts auto-load from `prompts/` directory at startup
- Pipeline supports iterative refinement with configurable acceptance thresholds
- React frontend proxies API requests to backend during development
- Production build serves static files directly from FastAPI