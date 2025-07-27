#!/usr/bin/env python3
import os
import glob
import json
import logging
import sys
from datetime import datetime
from pdf_extractor import PDFOutlineExtractor

# Configure logging for Docker (stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """Main processing function with comprehensive error handling."""
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure directories exist
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory ready: {output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        return 1
    
    # Initialize extractor
    try:
        extractor = PDFOutlineExtractor()
        logger.info("PDF extractor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PDF extractor: {e}")
        return 1
    
    # Find PDF files
    try:
        pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {input_dir}")
        
        if not pdf_files:
            logger.warning("No PDF files found in input directory")
            return 0
    except Exception as e:
        logger.error(f"Error scanning input directory: {e}")
        return 1
    
    # Process each PDF
    processed_count = 0
    error_count = 0
    
    for pdf_path in pdf_files:
        try:
            filename = os.path.basename(pdf_path)
            logger.info(f"Processing: {filename}")
            
            # Extract outline
            result = extractor.extract_outline(pdf_path)
            
            # Prepare output
            output_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "filename": filename,
                "title": result.get("title", "Document"),
                "outline": result.get("outline", []),
                "total_headings": len(result.get("outline", [])),
                "processing_status": "success"
            }
            
            # Write JSON output
            base_name = os.path.basename(pdf_path)
            output_file = os.path.join(output_dir, base_name.replace('.pdf', '.json'))
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Generated: {os.path.basename(output_file)} ({len(result.get('outline', []))} headings)")
            processed_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing {os.path.basename(pdf_path)}: {str(e)}")
            error_count += 1
            
            # Create error output file
            try:
                error_output = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "filename": os.path.basename(pdf_path),
                    "processing_status": "error",
                    "error_message": str(e)
                }
                error_file = os.path.join(output_dir, f"ERROR_{os.path.basename(pdf_path).replace('.pdf', '.json')}")
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(error_output, f, indent=2, ensure_ascii=False)
            except Exception as write_error:
                logger.error(f"Failed to write error file: {write_error}")
    
    # Summary
    logger.info(f"Processing complete: {processed_count} successful, {error_count} errors")
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
