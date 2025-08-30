import fitz  # PyMuPDF
import os
import tempfile
from typing import Dict, Any
from google.adk.tools import ToolContext
from PIL import Image
import pytesseract

def pdf_ingestion_tool(pdf_path: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Extracts text from a PDF file by converting each page to an image and using OCR.
    This approach provides better layout preservation and handles complex PDFs.

    Args:
        pdf_path (str): Path to the input pdf.
        tool_context (ToolContext): The tool context containing state information.
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: Success or Failure
    """
    try:
        doc = fitz.open(pdf_path)
        pages_data = []
        page_images = []  # Store image paths for later use in redaction
        
        # Create temporary directory for page images
        temp_dir = tempfile.mkdtemp()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Convert page to image with high DPI for better OCR accuracy
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x scaling for better quality
            
            # Save page as image
            image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
            pix.save(image_path)
            page_images.append(image_path)
            
            # Use OCR to extract text from the image
            image = Image.open(image_path)
            
            # Use detailed OCR to get word-level layout information
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
            
            # Drop rows without text
            ocr_data = ocr_data[ocr_data['text'].notnull()]
            
            # Reconstruct text line by line (helps retain layout better)
            lines = []
            for line_num, line_df in ocr_data.groupby(['block_num', 'par_num', 'line_num']):
                line_text = ' '.join(line_df['text'].tolist())
                if line_text.strip():  # Only add non-empty lines
                    lines.append(line_text)
            
            structured_text = '\n'.join(lines)
            
            # Store page data with OCR layout information
            layout_data = ocr_data.to_dict(orient='records')
            
            pages_data.append({
                "page_number": page_num + 1,
                "content": structured_text,
                "image_path": image_path,
                "layout_data": layout_data
            })
        
        doc.close()

        # Store all extracted data in tool context
        tool_context.state['pdf_data'] = pages_data
        tool_context.state['pdf_path'] = pdf_path
        tool_context.state['page_images'] = page_images
        tool_context.state['temp_dir'] = temp_dir

        return {
            "status": "success",
        }

    except Exception as e:
        return {"status": "failure", "error": str(e)}