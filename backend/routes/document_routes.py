import os
import shutil
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from ..services.pipeline import DocumentProcessingPipeline

document_bp = Blueprint('document_bp', __name__)

# Constants for file management
TEMP_DIR = Path(__file__).parent.parent / "tmp"
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_pipeline():
    # Use config or defaults for paths
    base_dir = Path(__file__).parent.parent
    ieee_spec = base_dir / "templates" / "ieee.json"
    ieee_template = base_dir / "templates" / "ieee.docx" # Assuming this exists or will be provided
    
    # Check if template exists, if not, formatter will use default
    template_path = str(ieee_template) if ieee_template.exists() else None
    
    return DocumentProcessingPipeline(
        ieee_spec_path=str(ieee_spec),
        docx_template_path=template_path
    )

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        job_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        
        # Clear TEMP_DIR before saving new upload
        if TEMP_DIR.exists():
            for item in TEMP_DIR.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        
        # Save directly in TEMP_DIR instead of job subfolder
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        input_path = TEMP_DIR / filename
        file.save(input_path)
        
        return jsonify({
            "message": "File uploaded successfully",
            "job_id": job_id,
            "filename": filename
        }), 201
    
    return jsonify({"error": "File type not allowed"}), 400

@document_bp.route('/analyze/<job_id>', methods=['POST'])
def analyze_document(job_id):
    try:
        # Files are now directly in TEMP_DIR
        if not TEMP_DIR.exists():
            return jsonify({"error": "Temp directory not found"}), 404
        
        # Find the docx file in the temp directory
        docx_files = list(TEMP_DIR.glob("*.docx"))
        if not docx_files:
            return jsonify({"error": "No input file found"}), 400
        
        input_path = docx_files[0]
        
        pipeline = get_pipeline()
        result = pipeline.analyze_document(str(input_path), job_id=job_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"error": str(e), "job_id": job_id, "success": False}), 500

@document_bp.route('/format/<job_id>', methods=['POST'])
def format_document(job_id):
    pipeline = get_pipeline()
    result = pipeline.format_mapped_content(job_id=job_id)
    
    if result["success"]:
        output_file = Path(result["output_file"])
        if output_file.exists():
            return send_file(
                output_file,
                as_attachment=True,
                download_name=output_file.name,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        return jsonify({"error": "Formatted file not found"}), 500
    else:
        return jsonify(result), 500