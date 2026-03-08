"""
pipeline.py — DocumentProcessingPipeline
========================================
Orchestrates the complete manuscript formatting pipeline.

Coordinates Parser → Classifier → Mapper → Formatter to transform
raw DOCX files into publication-ready IEEE formatted documents.
"""

import json
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from .parser import DocumentParser
from .classifier import ContentClassifier
from .mapper import ContentMapper
from .formatter import TemplateFormatter

logger = logging.getLogger(__name__)


class DocumentProcessingPipeline:
    """
    Complete document processing pipeline.
    
    Pipeline Flow:
    1. DocumentParser: Extract structured content from raw DOCX
    2. ContentClassifier: Verify/correct paragraph roles using AI
    3. ContentMapper: Map to clean content schema
    4. TemplateFormatter: Apply IEEE formatting and generate new DOCX
    """

    def __init__(self, ieee_spec_path: str, docx_template_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        Initialize the processing pipeline.
        
        Args:
            ieee_spec_path: Path to IEEE specification JSON file (ieee.json)
            docx_template_path: Path to IEEE Word template (.docx)
            env_path: Path to .env file with API keys
        """
        self.ieee_spec_path = ieee_spec_path
        self.docx_template_path = docx_template_path
        self.env_path = env_path
        
        # Initialize pipeline components
        self.parser = DocumentParser  # Class reference, instantiated per document
        self.classifier = ContentClassifier(env_path=env_path)
        self.mapper = ContentMapper(ieee_spec_path=ieee_spec_path)
        self.formatter = TemplateFormatter(ieee_spec_path=ieee_spec_path, template_path=docx_template_path)
        
        # Processing statistics
        self.stats = {}

    def analyze_document(
        self, 
        input_path: str, 
        job_id: Optional[str] = None,
        save_intermediate: bool = True
    ) -> Dict[str, Any]:
        """
        Step 1-3: Parse, Classify, and Map document.
        Returns the structured mapped output for reporting/UI review.
        """
        if job_id is None:
            job_id = str(uuid.uuid4())[:8]
            
        logger.info(f"[{job_id}] Starting analysis: {input_path}")
        input_file_path = Path(input_path)
        
        # Use the tmp directory directly
        base_dir = Path(__file__).parent.parent
        temp_dir = base_dir / "tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 1: Parse
            parser = self.parser(input_path)
            parsed_output = parser.extract_all()
            
            # Step 2: Classify
            classified_output = self.classifier.classify(parsed_output)
            
            # Step 3: Map
            mapped_output = self.mapper.map_content(classified_output)
            mapping_issues = self.mapper.validate_mapping(mapped_output)
            
            # Add metadata for the API
            mapped_output["job_id"] = job_id
            mapped_output["source_file"] = input_file_path.name
            
            if save_intermediate:
                state_file = temp_dir / "mapped_state.json"
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(mapped_output, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "job_id": job_id,
                "mapping_report": mapped_output,
                "mapping_issues": mapping_issues,
                "stats": self._compile_stats(parsed_output, classified_output, mapped_output, job_id)
            }
        except Exception as e:
            logger.error(f"[{job_id}] Analysis failed: {e}", exc_info=True)
            return {"success": False, "job_id": job_id, "error": str(e)}

    def format_mapped_content(
        self,
        job_id: str,
        mapped_data: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Step 4: Generate the final DOCX from mapped content.
        If mapped_data is None, it attempts to load it from the job's temp folder.
        """
        base_dir = Path(__file__).parent.parent
        temp_dir = base_dir / "tmp"
        
        if mapped_data is None:
            state_file = temp_dir / "mapped_state.json"
            if not state_file.exists():
                return {"success": False, "error": f"No state found for job {job_id}"}
                
            with open(state_file, 'r', encoding='utf-8') as f:
                mapped_data = json.load(f)

        try:
            if output_path is None:
                source_name = mapped_data.get("source_file", "document")
                stem = Path(source_name).stem
                output_path = temp_dir / f"{stem}_formatted.docx"
            
            output_path = Path(output_path)
            
            # Step 4: Format
            logger.info(f"[{job_id}] Generating formatted document...")
            self.formatter.format_document(mapped_data)
            saved_path = self.formatter.save_document(str(output_path))
            
            return {
                "success": True,
                "job_id": job_id,
                "output_file": saved_path
            }
        except Exception as e:
            logger.error(f"[{job_id}] Formatting failed: {e}", exc_info=True)
            return {"success": False, "job_id": job_id, "error": str(e)}

    def process_document(
        self, 
        input_path: str, 
        output_path: Optional[str] = None,
        save_intermediate: bool = True
    ) -> Dict[str, Any]:
        """Legacy helper for full batch/CLI execution."""
        analysis = self.analyze_document(input_path, save_intermediate=save_intermediate)
        if not analysis["success"]:
            return analysis
            
        return self.format_mapped_content(analysis["job_id"], analysis["mapping_report"], output_path)

    def _compile_stats(
        self, 
        parsed_output: Dict[str, Any], 
        classified_output: Dict[str, Any], 
        mapped_output: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:
        """Compile processing statistics from all pipeline stages."""
        
        # Parser statistics
        parser_meta = parsed_output.get("metadata", {})
        
        # Classification statistics
        classification_meta = classified_output.get("classification_meta", {})
        
        # Mapping statistics
        mapped_sections = len(mapped_output.get("sections", []))
        mapped_references = len(mapped_output.get("references", []))
        
        stats = {
            "job_id": job_id,
            "parser": {
                "paragraphs_extracted": parser_meta.get("paragraph_count", 0),
                "sections_found": parser_meta.get("section_count", 0),
                "references_found": parser_meta.get("reference_count", 0),
                "tables_found": parser_meta.get("table_count", 0),
                "images_found": parser_meta.get("image_count", 0),
                "word_count": parser_meta.get("word_count", 0),
            },
            "classifier": {
                "model_used": classification_meta.get("model_used"),
                "high_confidence_kept": classification_meta.get("high_confidence_kept", 0),
                "ambiguous_sent": classification_meta.get("ambiguous_sent", 0),
                "corrections_made": classification_meta.get("corrections_made", 0),
                "fallback_used": classification_meta.get("fallback_used", False),
            },
            "mapper": {
                "sections_mapped": mapped_sections,
                "references_mapped": mapped_references,
                "authors_mapped": len(mapped_output.get("authors", [])),
                "has_title": bool(mapped_output.get("title")),
                "has_abstract": bool(mapped_output.get("abstract")),
                "has_keywords": bool(mapped_output.get("keywords")),
            },
            "pipeline": {
                "total_processing_time": 0,  # Could add timing if needed
                "stages_completed": 4,
                "success": True
            }
        }
        
        return stats

    def batch_process(
        self, 
        input_files: list, 
        output_dir: Optional[str] = None,
        save_intermediate: bool = False
    ) -> Dict[str, Any]:
        """
        Process multiple documents in batch.
        
        Args:
            input_files: List of input DOCX file paths
            output_dir: Directory for output files (defaults to input directory)
            save_intermediate: Whether to save intermediate files
            
        Returns:
            Batch processing results
        """
        logger.info(f"Starting batch processing: {len(input_files)} files")
        
        if output_dir is None:
            output_dir = Path(input_files[0]).parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        batch_results = {
            "total_files": len(input_files),
            "successful": 0,
            "failed": 0,
            "results": [],
            "errors": []
        }
        
        for input_file in input_files:
            input_path = Path(input_file)
            output_file = output_dir / f"{input_path.stem}_formatted.docx"
            
            result = self.process_document(
                str(input_path), 
                str(output_file), 
                save_intermediate=save_intermediate
            )
            
            batch_results["results"].append(result)
            
            if result["success"]:
                batch_results["successful"] += 1
            else:
                batch_results["failed"] += 1
                batch_results["errors"].append({
                    "file": str(input_path),
                    "error": result.get("error"),
                    "error_type": result.get("error_type")
                })
        
        logger.info(f"Batch processing complete: {batch_results['successful']}/{batch_results['total_files']} successful")
        return batch_results

    def cleanup_temp_files(self, temp_dir: str, older_than_hours: int = 24):
        """
        Clean up temporary files older than specified hours.
        
        Args:
            temp_dir: Directory containing temporary files
            older_than_hours: Remove files older than this many hours
        """
        import time
        
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return
        
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        cleaned_count = 0
        for file_path in temp_path.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} temporary files")


if __name__ == "__main__":
    import sys
    
    # Hardcoded paths for local testing
    input_file = r"D:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\template\test.docx"
    spec_path = r"D:\DATA SCIENCE AND ML\Project\ManuscriptMagic.AI\backend\templates\ieee.json"
    template_path = r"backend\templates\ieee.json"
    output_file = None  # Will auto-generate
    save_intermediate = True
    
    # Initialize and run pipeline
    pipeline = DocumentProcessingPipeline(
        ieee_spec_path=spec_path,
        docx_template_path=template_path
    )
    
    print(f"Processing document: {input_file}")
    result = pipeline.process_document(
        input_file, 
        output_file, 
        save_intermediate=save_intermediate
    )
    
    if result["success"]:
        print(f"✅ Processing successful!")
        print(f"   Input: {result['input_file']}")
        print(f"   Output: {result['output_file']}")
        print(f"   Job ID: {result['job_id']}")
        
        stats = result["processing_stats"]
        print(f"\n📊 Processing Statistics:")
        print(f"   Paragraphs extracted: {stats['parser']['paragraphs_extracted']}")
        print(f"   AI corrections made: {stats['classifier']['corrections_made']}")
        print(f"   Sections mapped: {stats['mapper']['sections_mapped']}")
        
        if result["mapping_issues"]:
            print(f"\n⚠️  Mapping Issues:")
            for issue in result["mapping_issues"]:
                print(f"   - {issue}")
    else:
        print(f"❌ Processing failed!")
        print(f"   Error: {result['error']}")
        print(f"   Type: {result['error_type']}")
        sys.exit(1)
