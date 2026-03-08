# ManuscriptMagic.AI API Documentation

A RESTful API service to automate manuscript analysis and IEEE formatting.

## Architecture

The system follows a 4-stage pipeline orchestrated via a Flask backend:
1. **Parser**: Extracts structured elements from DOCX.
2. **Classifier**: Refines content roles using AI heuristics.
3. **Mapper**: Structures content into a clean schema.
4. **Formatter**: Applies IEEE styles and generates a new DOCX.

## API Endpoints

### 1. Upload Document
- **Endpoint**: `POST /api/documents/upload`
- **Request**: Multipart/form-data with `file` field (.docx).
- **Response**: `{"job_id": "...", "filename": "..."}`
- **Status Codes**: 201 Created.

### 2. Analyze Document
- **Endpoint**: `POST /api/documents/analyze/<job_id>`
- **Request**: Parameterized by the `job_id` from the upload step.
- **Goal**: Runs Stage 1-3 of the pipeline.
- **Response**: JSON report with metadata, sections, tables, and mapping issues.
- **Status Codes**: 200 OK.

### 3. Format Document
- **Endpoint**: `POST /api/documents/format/<job_id>`
- **Goal**: Runs Stage 4 (formatting) and generates the final output.
- **Response**: Octet-stream (.docx file download).
- **Status Codes**: 200 OK.

## Setup

1. **Requirements**: 
    - `pip install -r backend/requirements.txt`
2. **Execution**:
    - `python backend/main.py`
3. **Testing**:
    - Use `backend/tests/test_api_flow.py` (requires a running server).
