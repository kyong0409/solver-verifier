# RFP Business Requirements Extractor

A 6-stage Analyzer-Verifier pipeline for extracting business requirements from RFP documents, interviews, and related materials. Inspired by Gemini 2.5 Pro's IMO 2025 approach.

## Features

🎯 **Dual-Agent Architecture**: Analyzer extracts requirements, Verifier validates accuracy  
📄 **Multi-Format Support**: PDF, Markdown, Text, DOCX, PPTX, XLSX via markitdown  
🔍 **6-Stage Pipeline**: Complete extraction to acceptance workflow  
🎨 **React Frontend**: Intuitive web interface for document upload and results  
📊 **Quality Metrics**: Coverage, precision, traceability scoring  
🔧 **Configurable Prompts**: Customize agent behavior via API or files  

## Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies with uv
uv sync

# Install Node.js dependencies for frontend
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
cd ..
```

### 2. Build Frontend
```bash
# Build React frontend
./scripts/build-frontend.sh
```

### 3. Configure System Prompts (Optional)
Edit the prompts in `prompts/` directory:
- `prompts/analyzer_prompt.txt` - Analyzer agent configuration
- `prompts/verifier_prompt.txt` - Verifier agent configuration

### 4. Start Server
```bash
# Start FastAPI server with React frontend
uv run uvicorn main:app --reload

# Visit http://localhost:8000
```

## Usage

### Web Interface
1. Open http://localhost:8000
2. Upload RFP documents (PDF, MD, TXT, DOCX, PPTX, XLSX)
3. Enter project name and description
4. Click "Analyze Requirements"
5. Review extracted requirements, issues, and metrics

### API Usage
```bash
# Process documents via API
curl -X POST "http://localhost:8000/pipeline/process" \
  -F "files=@rfp_document.pdf" \
  -F "files=@requirements.md" \
  -F "set_name=Project Alpha" \
  -F "set_description=E-commerce platform RFP"

# Check pipeline stages
curl http://localhost:8000/pipeline/stages

# Configure prompts
curl -X POST "http://localhost:8000/pipeline/configure/analyzer" \
  -F "system_prompt=Your custom analyzer prompt"
```

## 6-Stage Pipeline

1. **Initial BR Draft** - Extract requirements with citations
2. **Self-improvement** - Refine and enhance draft
3. **Verification** - Validate against source documents
4. **Review (Optional)** - Human/AI review of results
5. **Bug Fixes** - Address verification issues
6. **Accept/Reject** - Final quality decision

## Architecture

```
├── solver_verifier/           # Main Python package
│   ├── api/                  # FastAPI routes
│   ├── models/               # Pydantic models
│   └── services/             # Core business logic
├── frontend/                 # React web interface
├── prompts/                  # System prompt templates
└── scripts/                  # Build and utility scripts
```

## Configuration

### Environment Variables
```bash
# .env file
ANALYZER_SYSTEM_PROMPT="Custom analyzer prompt"
VERIFIER_SYSTEM_PROMPT="Custom verifier prompt"
PIPELINE_CONFIG__MAX_ITERATIONS=5
PIPELINE_CONFIG__ACCEPTANCE_THRESHOLD=3
```

### Prompt Management
- **File-based**: Edit `prompts/*.txt` files
- **API-based**: POST to `/pipeline/configure/analyzer` or `/verifier`
- **Auto-loading**: Prompts load automatically at startup

## Development

### Backend Development
```bash
# Install development dependencies
uv add --dev pytest pytest-cov pytest-asyncio httpx

# Run tests
uv run pytest

# Run with hot reload
uv run uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend

# Development server (with backend proxy)
npm start

# Build production version
npm run build
```

## Supported File Formats

- **PDF**: Parsed with markitdown
- **Markdown**: Direct text parsing
- **Text**: Direct text parsing  
- **Office**: DOCX, PPTX, XLSX via markitdown

## Documentation

📚 **Complete Documentation**: See [`docs/`](docs/) directory for comprehensive guides:

- **[User Guide](docs/USER_GUIDE.md)**: Complete user manual for end users
- **[API Reference](docs/API_REFERENCE.md)**: REST API documentation for developers  
- **[Development Guide](docs/DEVELOPMENT.md)**: Setup and development workflows
- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design and technical architecture

## License

MIT License - see LICENSE file for details.