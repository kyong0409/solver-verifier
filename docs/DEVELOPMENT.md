# Development Guide

Complete development guide for the RFP Business Requirements Extractor.

## Prerequisites

### Required Software
- **Python 3.10+**: Core language runtime
- **Node.js 18+**: Frontend development
- **uv**: Fast Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git**: Version control

### Optional Tools
- **Visual Studio Code**: Recommended IDE with extensions:
  - Python
  - TypeScript and JavaScript Language Features
  - Tailwind CSS IntelliSense
  - REST Client (for API testing)

## Project Setup

### 1. Clone and Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd solver-verifier

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
cd ..
```

### 2. Environment Configuration

Create `.env` file in project root:

```bash
# System Prompts (optional - auto-loads from prompts/ directory)
ANALYZER_SYSTEM_PROMPT=""
VERIFIER_SYSTEM_PROMPT=""

# Pipeline Configuration
PIPELINE_CONFIG__MAX_ITERATIONS=5
PIPELINE_CONFIG__ACCEPTANCE_THRESHOLD=3
PIPELINE_CONFIG__ENABLE_STAGE_4_REVIEW=false

# Application Settings
OUTPUT_DIRECTORY=./output
ENABLE_LOGGING=true
LOG_LEVEL=INFO
```

### 3. Configure System Prompts

Edit the Korean-language prompts in the `prompts/` directory:
- `prompts/analyzer_prompt.txt` - Analyzer agent behavior
- `prompts/verifier_prompt.txt` - Verifier agent behavior

Prompts auto-load at startup, or manually load via API:
```bash
curl -X POST http://localhost:8000/pipeline/prompts/load
```

### 4. Build and Run

```bash
# Build frontend
./scripts/build-frontend.sh

# Start development server
uv run uvicorn main:app --reload

# Visit http://localhost:8000
```

## Development Workflow

### Backend Development

#### Project Structure
```
solver_verifier/
├── api/                    # FastAPI routes
│   └── pipeline_router.py  # Main API endpoints
├── models/                 # Pydantic models
│   ├── agent_config.py     # Configuration models
│   └── business_requirement.py  # Data models
└── services/               # Business logic
    ├── analyzer_service.py      # Analyzer (Solver role)
    ├── verifier_service.py      # Verifier role
    ├── pipeline_service.py      # Pipeline orchestration
    ├── document_parser.py       # Multi-format parsing
    └── prompt_loader.py         # Prompt management
```

#### Running in Development Mode
```bash
# Start with auto-reload
uv run uvicorn main:app --reload --log-level debug

# Run specific service tests
uv run python -m pytest tests/test_pipeline_service.py -v

# Test document parsing
uv run python -c "
from solver_verifier.services.document_parser import DocumentParserService
import asyncio
parser = DocumentParserService()
result = asyncio.run(parser.parse_documents(['test.pdf']))
print(result)
"
```

#### Adding New Services
1. Create service file in `solver_verifier/services/`
2. Define service class with dependency injection
3. Add async methods for business logic
4. Register in `pipeline_service.py` if needed
5. Add corresponding API endpoints in `pipeline_router.py`

#### Adding New Models
1. Create Pydantic models in `solver_verifier/models/`
2. Use proper field validation and documentation
3. Export in `__init__.py`
4. Update API endpoints to use new models

### Frontend Development

#### Project Structure
```
frontend/src/
├── components/          # Reusable UI components
│   ├── FileUploader.tsx # Multi-format file upload
│   └── ResultsDisplay.tsx # Requirements visualization
├── pages/              # Page components
│   └── HomePage.tsx    # Main application page
├── services/           # API communication
│   └── api.ts          # Axios-based API client
└── types/              # TypeScript definitions
    └── index.ts        # Business requirement types
```

#### Development Server
```bash
cd frontend

# Start with backend proxy
npm start

# Run in different terminal for backend
cd ..
uv run uvicorn main:app --reload
```

#### Building for Production
```bash
# Automated build script
./scripts/build-frontend.sh

# Manual build
cd frontend
npm run build
cd ..
```

#### Adding New Components
1. Create component in `src/components/`
2. Use TypeScript and proper prop interfaces
3. Apply Tailwind CSS for styling
4. Export from component directory
5. Add to main pages as needed

### API Development

#### Adding New Endpoints

1. **Define endpoint in router**:
```python
# solver_verifier/api/pipeline_router.py
@router.post("/new-endpoint")
async def new_endpoint(param: str = Form(...)):
    try:
        result = await some_service.process(param)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Add service method**:
```python
# solver_verifier/services/some_service.py
async def process(self, param: str) -> Dict[str, Any]:
    # Business logic here
    return {"result": "processed"}
```

3. **Update frontend API client**:
```typescript
// frontend/src/services/api.ts
static async newEndpoint(param: string): Promise<any> {
  const formData = new FormData();
  formData.append('param', param);
  
  const response = await api.post('/pipeline/new-endpoint', formData);
  return response.data;
}
```

#### API Testing

Use REST Client extension or curl:

```bash
# Test document processing
curl -X POST "http://localhost:8000/pipeline/process" \
  -F "files=@test.pdf" \
  -F "set_name=Test"

# Test configuration
curl -X GET "http://localhost:8000/pipeline/configure"

# Test prompt loading
curl -X POST "http://localhost:8000/pipeline/prompts/load"
```

## Testing

### Unit Tests
```bash
# Install test dependencies
uv add --dev pytest pytest-cov pytest-asyncio httpx

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=solver_verifier --cov-report=html

# Run specific test files
uv run pytest tests/test_document_parser.py -v
```

### Integration Tests
```bash
# Test full pipeline
uv run pytest tests/test_integration.py -v

# Test API endpoints
uv run pytest tests/test_api.py -v
```

### Frontend Tests
```bash
cd frontend

# Run React tests
npm test

# Run with coverage
npm test -- --coverage
```

### Manual Testing

#### Test Documents
Create test documents in `test_documents/`:
- `sample_rfp.pdf` - PDF with business requirements
- `requirements.md` - Markdown with structured requirements
- `interview_notes.txt` - Text file with meeting notes

#### Test Scenarios
1. **Single PDF Upload**: Test PDF parsing and requirement extraction
2. **Multiple File Upload**: Mix of PDF, MD, TXT files
3. **Error Scenarios**: Invalid file types, large files, corrupted documents
4. **Configuration Changes**: Modify prompts and pipeline settings
5. **Performance Testing**: Large documents, multiple concurrent requests

## Debugging

### Backend Debugging

#### Enable Debug Logging
```python
# In main.py or service files
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Debug Pipeline Stages
```python
# Add debugging in pipeline_service.py
async def _stage_1_initial_draft(self, ...):
    print(f"Stage 1: Processing {len(documents)} documents")
    # ... existing code
    print(f"Stage 1: Generated {len(requirements)} requirements")
```

#### Debug Document Parsing
```bash
# Test document parsing directly
uv run python -c "
import asyncio
from solver_verifier.services.document_parser import DocumentParserService

async def test():
    parser = DocumentParserService()
    result = await parser.parse_documents(['test.pdf'])
    print(f'Parsed content length: {len(result)}')
    print(f'Content preview: {list(result.values())[0][:200]}...')

asyncio.run(test())
"
```

### Frontend Debugging

#### React Developer Tools
Install React Developer Tools browser extension for component inspection.

#### Network Debugging
```typescript
// Add request/response logging in api.ts
api.interceptors.request.use(request => {
  console.log('API Request:', request);
  return request;
});

api.interceptors.response.use(
  response => {
    console.log('API Response:', response);
    return response;
  },
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

#### Component State Debugging
```typescript
// Add debugging in components
const FileUploader: React.FC<FileUploaderProps> = ({ onFilesChange, ... }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  
  // Debug state changes
  useEffect(() => {
    console.log('Selected files changed:', selectedFiles);
  }, [selectedFiles]);
  
  // ... component logic
};
```

## Performance Optimization

### Backend Performance

#### Document Processing
- Use async/await throughout pipeline
- Process documents in parallel where possible
- Implement result caching for similar content
- Add connection pooling for external services

#### Memory Management
```python
# Clear temporary files promptly
try:
    result = await process_documents(files)
finally:
    for temp_file in temp_files:
        os.unlink(temp_file)
```

#### Response Optimization
```python
# Stream large responses
from fastapi.responses import StreamingResponse

@router.get("/large-results")
async def stream_results():
    def generate():
        for chunk in large_dataset:
            yield json.dumps(chunk) + "\n"
    
    return StreamingResponse(generate(), media_type="application/json")
```

### Frontend Performance

#### Bundle Optimization
```typescript
// Lazy load components
const ResultsDisplay = React.lazy(() => import('../components/ResultsDisplay'));

// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{/* expensive rendering */}</div>;
});
```

#### State Optimization
```typescript
// Debounce API calls
import { useMemo, useCallback } from 'react';
import debounce from 'lodash/debounce';

const debouncedSearch = useCallback(
  debounce((query: string) => {
    // API call here
  }, 300),
  []
);
```

## Deployment

### Development Deployment
```bash
# Start all services
./scripts/build-frontend.sh
uv run uvicorn main:app --reload

# Or use Docker for consistent environment
docker-compose up -d
```

### Production Deployment

#### Environment Setup
```bash
# Production environment variables
NODE_ENV=production
ENABLE_LOGGING=true
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=100MB
```

#### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Copy and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Build frontend
COPY frontend/ ./frontend/
RUN cd frontend && npm install && npm run build

# Copy application
COPY . .

# Start application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Performance Tuning
```bash
# Production server with multiple workers
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Common Issues and Solutions

### Backend Issues

#### Import Errors
```bash
# Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"
uv run python -c "import solver_verifier; print('OK')"
```

#### File Processing Errors
- **PDF parsing fails**: Ensure markitdown dependencies are installed
- **Encoding issues**: Check file encoding, add CP949 fallback
- **Memory issues**: Implement file size limits and streaming

#### Pipeline Errors
- **Stage failures**: Add comprehensive error handling in each stage
- **Timeout issues**: Implement configurable timeouts
- **State corruption**: Add validation between stages

### Frontend Issues

#### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install
```

#### API Connection Issues
- **CORS errors**: Ensure proper proxy configuration in package.json
- **Network errors**: Check backend server is running
- **Type errors**: Update TypeScript definitions

#### Styling Issues
- **Tailwind not working**: Ensure tailwind.config.js is properly configured
- **Component rendering**: Check React DevTools for component state
- **Responsive issues**: Test on different screen sizes

## Best Practices

### Code Style

#### Python
- Use type hints for all functions
- Follow PEP 8 style guidelines
- Use async/await for I/O operations
- Implement proper error handling

```python
async def process_document(
    self, 
    file_path: str, 
    options: Optional[Dict[str, Any]] = None
) -> ProcessingResult:
    """Process a document and return structured results.
    
    Args:
        file_path: Path to the document file
        options: Optional processing parameters
        
    Returns:
        ProcessingResult with extracted requirements
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ProcessingError: If processing fails
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Processing failed for {file_path}: {e}")
        raise ProcessingError(f"Processing failed: {e}") from e
```

#### TypeScript/React
- Use TypeScript interfaces for all props
- Implement proper error boundaries
- Use React hooks appropriately
- Follow React best practices

```typescript
interface ComponentProps {
  data: BusinessRequirement[];
  onSelect: (requirement: BusinessRequirement) => void;
  loading?: boolean;
}

const Component: React.FC<ComponentProps> = ({ 
  data, 
  onSelect, 
  loading = false 
}) => {
  const handleSelect = useCallback((req: BusinessRequirement) => {
    onSelect(req);
  }, [onSelect]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      {data.map(req => (
        <RequirementCard 
          key={req.br_id} 
          requirement={req} 
          onSelect={handleSelect} 
        />
      ))}
    </div>
  );
};
```

### Security

- Validate all user inputs
- Sanitize file uploads
- Implement rate limiting
- Use HTTPS in production
- Log security events

### Performance

- Use async operations for I/O
- Implement caching where appropriate
- Monitor memory usage
- Profile performance bottlenecks
- Optimize database queries (when added)

## Contributing

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Submit pull request with clear description

### Commit Message Format
```
type(scope): description

feat(api): add new endpoint for bulk processing
fix(frontend): resolve file upload validation issue
docs(readme): update installation instructions
```

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive information in code
- [ ] Performance impact considered
- [ ] Security implications reviewed