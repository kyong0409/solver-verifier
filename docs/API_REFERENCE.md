# API Reference

Complete API documentation for the RFP Business Requirements Extractor.

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for this version.

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api` | GET | API information |
| `/health` | GET | Health check |
| `/pipeline/process` | POST | Process RFP documents |
| `/pipeline/status/{set_id}` | GET | Get processing status |
| `/pipeline/stages` | GET | Get pipeline information |
| `/pipeline/configure` | GET | Get current configuration |
| `/pipeline/configure/analyzer` | POST | Configure analyzer prompt |
| `/pipeline/configure/verifier` | POST | Configure verifier prompt |
| `/pipeline/configure/pipeline` | POST | Configure pipeline settings |
| `/pipeline/prompts/load` | POST | Load prompts from files |
| `/pipeline/prompts/save` | POST | Save prompts to files |

---

## Document Processing

### POST `/pipeline/process`

Process RFP documents through the 6-stage Analyzer-Verifier pipeline.

**Request**
- Content-Type: `multipart/form-data`

**Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | File[] | Yes | RFP documents to process |
| `set_name` | string | No | Name for the requirement set |
| `set_description` | string | No | Description for the requirement set |

**Supported File Formats**
- `.pdf` - PDF documents (parsed with markitdown)
- `.md` - Markdown files
- `.txt` - Plain text files
- `.docx` - Microsoft Word documents
- `.pptx` - Microsoft PowerPoint presentations
- `.xlsx` - Microsoft Excel spreadsheets

**Response**
```json
{
  "set_id": "uuid-string",
  "name": "Project Alpha RFP",
  "description": "E-commerce platform requirements",
  "business_requirements": [
    {
      "br_id": "BR_12345678",
      "title": "Mobile Order Conversion 20% Improvement",
      "description": "System must achieve 20% improvement in mobile conversion rates",
      "requirement_type": "functional",
      "priority": "high",
      "citations": [
        {
          "text": "mobile channel conversion improvement is top priority",
          "location": {
            "document": "rfp_document.pdf",
            "section": "3.2",
            "page_number": 12
          }
        }
      ],
      "stakeholders": ["Sales Team", "CX Team"],
      "business_value": "Increase monthly MRR by 10%",
      "acceptance_criteria": [
        {
          "criterion_id": "AC_001",
          "description": "GA4 mobile conversion rate ≥ 20% over 3 months",
          "testable": true
        }
      ],
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "tags": ["mobile", "conversion", "kpi"],
      "dependencies": [],
      "conflicts": [],
      "assumptions": [],
      "constraints": [],
      "notes": null
    }
  ],
  "hypotheses": [],
  "verification_issues": [
    {
      "issue_id": "uuid-string",
      "br_id": "BR_12345678",
      "error_type": "justification_gap",
      "severity": "medium",
      "description": "Citation location needs more precision",
      "suggested_fix": "Add specific paragraph or line number",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "coverage_metrics": {
    "total_requirements": 15,
    "recall": 0.85,
    "precision": 0.92,
    "misinterpretation_rate": 0.03,
    "traceability_score": 0.88,
    "completion_rate": 0.76
  },
  "pipeline_stage": 6,
  "iteration_count": 2,
  "status": "accepted",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z",
  "source_documents": ["rfp_document.pdf", "requirements.md"]
}
```

**Error Responses**
```json
// 400 - Bad Request
{
  "detail": "Unsupported file format: .exe. Supported: .pdf, .md, .txt, .docx, .pptx, .xlsx"
}

// 500 - Processing Error
{
  "detail": "Processing error: Document parsing failed"
}
```

**Example**
```bash
curl -X POST "http://localhost:8000/pipeline/process" \
  -F "files=@rfp_document.pdf" \
  -F "files=@interview_notes.md" \
  -F "set_name=Project Alpha" \
  -F "set_description=E-commerce platform RFP analysis"
```

---

## Status and Information

### GET `/pipeline/status/{set_id}`

Get the current processing status of a requirement set.

**Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `set_id` | string | Yes | Unique identifier for the requirement set |

**Response**
```json
{
  "set_id": "uuid-string",
  "status": "in_progress",
  "current_stage": 3,
  "iteration": 1
}
```

### GET `/pipeline/stages`

Get information about the 6-stage pipeline.

**Response**
```json
{
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
  "supported_formats": [".pdf", ".md", ".txt", ".docx", ".pptx", ".xlsx"]
}
```

---

## Configuration Management

### GET `/pipeline/configure`

Get current system configuration.

**Response**
```json
{
  "analyzer_prompt_configured": true,
  "verifier_prompt_configured": true,
  "analyzer_prompt_length": 4046,
  "verifier_prompt_length": 4093,
  "pipeline_config": {
    "max_iterations": 5,
    "acceptance_threshold": 3,
    "enable_stage_4_review": false
  }
}
```

### POST `/pipeline/configure/analyzer`

Configure the Analyzer agent's system prompt.

**Request**
- Content-Type: `multipart/form-data`

**Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `system_prompt` | string | Yes | System prompt for the Analyzer agent |

**Response**
```json
{
  "message": "Analyzer system prompt updated successfully",
  "prompt_length": 4046
}
```

### POST `/pipeline/configure/verifier`

Configure the Verifier agent's system prompt.

**Request**
- Content-Type: `multipart/form-data`

**Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `system_prompt` | string | Yes | System prompt for the Verifier agent |

**Response**
```json
{
  "message": "Verifier system prompt updated successfully",
  "prompt_length": 4093
}
```

### POST `/pipeline/configure/pipeline`

Configure pipeline processing settings.

**Request**
- Content-Type: `multipart/form-data`

**Parameters**
| Parameter | Type | Required | Description | Range |
|-----------|------|----------|-------------|-------|
| `max_iterations` | integer | No | Maximum iterations for verification loop | 1-10 |
| `acceptance_threshold` | integer | No | Consecutive passes needed for acceptance | 1-5 |
| `enable_stage_4_review` | boolean | No | Enable optional human review in stage 4 | true/false |

**Response**
```json
{
  "message": "Pipeline configuration updated successfully",
  "current_config": {
    "max_iterations": 5,
    "acceptance_threshold": 3,
    "enable_stage_4_review": false
  }
}
```

---

## Prompt Management

### POST `/pipeline/prompts/load`

Load system prompts from files in the `prompts/` directory.

**Response**
```json
{
  "message": "Prompts loaded from files",
  "analyzer_loaded": true,
  "verifier_loaded": true,
  "analyzer_length": 4046,
  "verifier_length": 4093
}
```

### POST `/pipeline/prompts/save`

Save current system prompts to files.

**Response**
```json
{
  "message": "Prompts saved to files",
  "analyzer_saved": true,
  "verifier_saved": true
}
```

---

## Health and Status

### GET `/api`

Get API information and available endpoints.

**Response**
```json
{
  "message": "RFP Business Requirements Extractor API",
  "description": "6-stage Analyzer-Verifier pipeline for requirement extraction",
  "version": "0.1.0",
  "pipeline_stages": 6,
  "endpoints": {
    "process": "/pipeline/process",
    "status": "/pipeline/status/{set_id}",
    "configure": "/pipeline/configure",
    "stages_info": "/pipeline/stages"
  }
}
```

### GET `/health`

Health check endpoint.

**Response**
```json
{
  "status": "healthy",
  "service": "rfp-requirement-extractor"
}
```

---

## Error Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameters, unsupported file format |
| 404 | Not Found | Set ID not found |
| 500 | Internal Server Error | Processing failure, system error |

## Rate Limits

No rate limits currently implemented.

## Examples

### Complete Workflow Example

```bash
# 1. Check pipeline information
curl http://localhost:8000/pipeline/stages

# 2. Process documents
curl -X POST "http://localhost:8000/pipeline/process" \
  -F "files=@rfp.pdf" \
  -F "files=@requirements.md" \
  -F "set_name=Alpha Project" > result.json

# 3. Extract set_id from result
SET_ID=$(jq -r '.set_id' result.json)

# 4. Check processing status
curl "http://localhost:8000/pipeline/status/$SET_ID"

# 5. Configure settings if needed
curl -X POST "http://localhost:8000/pipeline/configure/pipeline" \
  -F "max_iterations=3" \
  -F "acceptance_threshold=2"
```

### JavaScript/Frontend Example

```javascript
// Process documents
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);
formData.append('set_name', 'Project Alpha');
formData.append('set_description', 'E-commerce RFP analysis');

const response = await fetch('/pipeline/process', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Extracted ${result.business_requirements.length} requirements`);
```