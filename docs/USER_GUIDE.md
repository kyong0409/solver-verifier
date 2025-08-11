# User Guide

Complete guide for using the RFP Business Requirements Extractor.

## Overview

The RFP Business Requirements Extractor is a web-based tool that automatically extracts business requirements from RFP documents, interview transcripts, and related materials using advanced AI analysis. The system employs a 6-stage Analyzer-Verifier pipeline to ensure accurate, traceable, and complete requirement extraction.

## Getting Started

### Accessing the Application

1. **Web Interface**: Open your browser and navigate to the application URL
2. **Upload Documents**: Drag and drop or browse to select RFP documents
3. **Configure Project**: Enter project name and description
4. **Analyze**: Click "Analyze Requirements" to start processing
5. **Review Results**: Examine extracted requirements, issues, and metrics

### Supported Document Types

| Format | Description | Use Case |
|--------|-------------|----------|
| **PDF** | Portable Document Format | RFP documents, proposals, specifications |
| **Markdown** | Markdown text files | Technical documentation, structured notes |
| **TXT** | Plain text files | Meeting notes, interview transcripts |
| **DOCX** | Microsoft Word documents | Formal requirements documents |
| **PPTX** | PowerPoint presentations | Executive briefings, technical presentations |
| **XLSX** | Excel spreadsheets | Requirements matrices, data specifications |

### File Requirements

- **Maximum file size**: 100MB per file
- **Maximum files**: 10 files per upload session
- **File encoding**: UTF-8 (auto-detected for text files)
- **Total processing time**: Typically 1-5 minutes per document set

## Using the Web Interface

### 1. Project Setup

#### Project Information
- **Project Name**: Descriptive name for your analysis (e.g., "E-commerce Platform RFP")
- **Description**: Optional brief description of the project scope
- **Best Practices**:
  - Use clear, descriptive names
  - Include version numbers if applicable
  - Reference RFP numbers or client names

#### Document Upload
1. **Drag and Drop**: Drag files directly onto the upload area
2. **Browse Files**: Click "browse" to select files from your computer
3. **File Validation**: System automatically validates file types and sizes
4. **Preview**: Review selected files before processing

### 2. Processing and Analysis

#### Processing Stages
The system processes your documents through 6 stages:

1. **Initial BR Draft** (30-60 seconds)
   - Extracts requirement candidates from documents
   - Includes direct citations and location references
   - Separates confirmed requirements from hypotheses

2. **Self-Improvement** (30-45 seconds)
   - Reviews initial draft for gaps and issues
   - Decomposes compound requirements
   - Improves citation quality and traceability

3. **Verification** (45-90 seconds)
   - Validates requirements against source documents
   - Checks citation accuracy and semantic consistency
   - Generates quality metrics and issue reports

4. **Review (Optional)** (0 seconds - auto-skip)
   - Optional human review step (disabled by default)
   - Can be enabled via configuration

5. **Bug Fixes** (30-60 seconds)
   - Addresses issues identified by verifier
   - Improves requirement quality and accuracy
   - May repeat with verification step

6. **Accept/Reject Decision** (5-10 seconds)
   - Final quality assessment
   - Accepts high-quality requirement sets
   - Flags sets needing additional work

#### Progress Monitoring
- **Real-time Status**: View current processing stage
- **Estimated Time**: Approximate completion time
- **Stage Description**: Understanding what's happening at each step

### 3. Understanding Results

#### Requirements Overview
- **Total Requirements**: Number of extracted business requirements
- **Pipeline Status**: Final acceptance/rejection status
- **Processing Summary**: Stages completed and iterations performed
- **Source Documents**: List of processed files

#### Individual Requirements

Each extracted requirement includes:

**Basic Information**:
- **ID**: Unique identifier (e.g., BR_12345678)
- **Title**: Concise requirement summary
- **Description**: Detailed requirement explanation
- **Type**: Functional, non-functional, business rule, etc.
- **Priority**: Critical, High, Medium, Low

**Traceability**:
- **Citations**: Direct quotes from source documents
- **Source Location**: Document, page, section references
- **Context**: Surrounding information for clarity

**Stakeholder Information**:
- **Stakeholders**: Identified parties involved
- **Business Value**: Expected benefits or impact
- **Acceptance Criteria**: Testable conditions for completion

**Metadata**:
- **Dependencies**: Related requirements
- **Constraints**: Limitations or restrictions
- **Assumptions**: Underlying assumptions
- **Tags**: Categorization labels

#### Quality Metrics

The system provides comprehensive quality metrics:

**Coverage Metrics**:
- **Recall**: Percentage of source requirements captured
- **Precision**: Percentage of extracted requirements that are valid
- **Traceability Score**: Completeness of source citations

**Quality Indicators**:
- **Completion Rate**: Overall pipeline success rate
- **Misinterpretation Rate**: Percentage of incorrectly interpreted requirements

**Typical Quality Ranges**:
- **Excellent**: Recall >90%, Precision >95%, Traceability >90%
- **Good**: Recall >80%, Precision >90%, Traceability >80%
- **Acceptable**: Recall >70%, Precision >85%, Traceability >70%
- **Needs Review**: Below acceptable thresholds

#### Verification Issues

The system identifies and reports various issues:

**Critical Errors**:
- **Citation Mismatch**: Quoted text doesn't match source
- **Source Missing**: Referenced document not found
- **Meaning Distortion**: Requirement contradicts source intent
- **Missing Evidence**: No supporting citations found

**Justification Gaps**:
- **Incomplete Citations**: Missing location information
- **Weak Evidence**: Insufficient supporting quotes
- **Ambiguous Context**: Unclear relationship to source
- **Missing Metadata**: Incomplete stakeholder or criteria information

## Advanced Features

### Configuration Options

#### System Prompts
- **Analyzer Configuration**: Customize requirement extraction behavior
- **Verifier Configuration**: Adjust validation criteria and strictness
- **Prompt Templates**: Pre-configured prompts for different domains

#### Pipeline Settings
- **Maximum Iterations**: How many verification cycles to attempt (1-10)
- **Acceptance Threshold**: Consecutive successful validations needed (1-5)
- **Stage 4 Review**: Enable optional human review step

### API Access

For programmatic access, the system provides a REST API:

#### Basic Usage
```bash
# Process documents
curl -X POST "http://your-server/pipeline/process" \
  -F "files=@rfp_document.pdf" \
  -F "files=@requirements.md" \
  -F "set_name=Project Alpha" \
  -F "set_description=Analysis description"

# Check status
curl "http://your-server/pipeline/status/{set_id}"

# Get results (included in process response)
```

#### Integration Examples
- **Python**: Use requests library with multipart/form-data
- **JavaScript**: Use fetch() or axios with FormData
- **cURL**: Command-line testing and automation

## Best Practices

### Document Preparation

#### Optimal Document Structure
1. **Clear Sections**: Well-organized with headers and subheaders
2. **Explicit Requirements**: Use "must", "shall", "should" language
3. **Complete Information**: Include stakeholders, acceptance criteria
4. **Consistent Terminology**: Use standard business terms
5. **Version Control**: Include document versions and dates

#### Common Document Issues
- **Scattered Requirements**: Requirements mixed with general text
- **Ambiguous Language**: Vague or interpretable statements
- **Missing Context**: Requirements without business justification
- **Technical Focus**: Implementation details instead of business needs
- **Incomplete Information**: Missing stakeholders or success criteria

#### Document Enhancement Tips
1. **Highlight Key Sections**: Use formatting to emphasize requirements
2. **Add Context**: Include business rationale for each requirement
3. **Specify Stakeholders**: Clearly identify who needs what
4. **Define Success**: Include measurable acceptance criteria
5. **Cross-Reference**: Link related requirements and dependencies

### Upload Strategy

#### Single vs. Multiple Documents
- **Single Large Document**: Best for comprehensive RFPs
- **Multiple Related Documents**: Better for complex projects with various sources
- **Document Combinations**: Mix formats for comprehensive analysis

#### File Organization
- **Primary RFP**: Main requirement document (highest priority)
- **Supporting Materials**: Specifications, technical requirements
- **Meeting Notes**: Interview transcripts, discussion records
- **Reference Documents**: Standards, policies, existing systems

### Result Interpretation

#### Quality Assessment
1. **Review Metrics**: Check coverage and accuracy scores
2. **Examine Issues**: Address critical errors first
3. **Validate Citations**: Spot-check key requirement sources
4. **Assess Completeness**: Compare with known requirements
5. **Check Consistency**: Look for conflicting requirements

#### Common Result Patterns
- **High Recall, Lower Precision**: System captured everything but included some invalid items
- **High Precision, Lower Recall**: System was conservative and missed some requirements
- **Low Traceability**: Poor citation quality, hard to verify sources
- **Many Critical Errors**: Document quality issues or system misconfiguration

#### Improvement Strategies
- **Document Quality**: Improve source document structure and clarity
- **Prompt Tuning**: Adjust system prompts for better domain fit
- **Iterative Processing**: Re-run analysis with refined documents
- **Manual Review**: Combine automated results with human validation

## Troubleshooting

### Common Upload Issues

#### File Format Problems
- **Error**: "Unsupported file format"
- **Solution**: Check supported formats list, convert if necessary
- **Prevention**: Use standard document formats (PDF, DOCX, MD, TXT)

#### File Size Issues
- **Error**: "File too large"
- **Solution**: Compress files or split large documents
- **Prevention**: Keep individual files under 100MB

#### Processing Failures
- **Error**: "Document parsing failed"
- **Causes**: Corrupted files, unsupported encoding, complex layouts
- **Solutions**: 
  - Try different file format
  - Simplify document structure
  - Check file integrity

### Processing Issues

#### Long Processing Times
- **Normal Range**: 1-5 minutes for typical document sets
- **Extended Times**: Large documents, complex requirements, multiple iterations
- **Optimization**: 
  - Reduce document size
  - Improve document structure
  - Lower iteration limits

#### Poor Quality Results
- **Low Recall**: System missing known requirements
  - Check document structure
  - Verify requirements are clearly stated
  - Consider prompt adjustment

- **Low Precision**: System generating invalid requirements
  - Review document quality
  - Check for ambiguous language
  - Validate citations

- **Many Critical Errors**: Fundamental processing issues
  - Examine source documents
  - Check citation accuracy
  - Review system configuration

#### Configuration Problems
- **Prompt Issues**: Custom prompts not working as expected
  - Validate prompt syntax
  - Test with default prompts
  - Check prompt loading status

- **Pipeline Settings**: Processing behavior unexpected
  - Review iteration limits
  - Check acceptance thresholds
  - Validate stage configuration

### Getting Help

#### Self-Service Resources
1. **Check Metrics**: Review quality scores for insights
2. **Examine Issues**: Look at specific error messages
3. **Review Citations**: Verify source document accuracy
4. **Test Settings**: Try different configuration options
5. **Simplify Input**: Start with smaller, clearer documents

#### System Information
- **Health Check**: Visit `/health` endpoint
- **Configuration**: Check `/pipeline/configure` for current settings
- **Pipeline Info**: Review `/pipeline/stages` for system capabilities

#### Support Information
For technical issues or questions:
- Review error messages and system logs
- Document specific steps that led to the issue
- Include example documents (if shareable)
- Note system configuration and settings used