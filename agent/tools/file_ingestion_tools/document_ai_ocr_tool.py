import json
import re
import os
from google.cloud import vision
from google.cloud import storage
import docx
import extract_msg
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1beta3 as documentai
from docx import Document
import email
import mimetypes
from typing import Dict, Any
from google.adk.tools import ToolContext


def document_ai_ocr_tool(file_path: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Intelligently processes documents using Google Cloud Document AI OCR and other text extraction methods.
    Supports PDF, images, DOCX, MSG, EML, and TXT files.

    Args:
        file_path (str): Path to the input file.
        tool_context (ToolContext): The tool context containing state information.
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: Success or Failure
            - extracted_text: The extracted text content
            - file_type: The type of file processed
    """
    try:
        # Google Cloud Document AI configuration
        PROJECT_ID = "quiet-sum-470418-r7"
        LOCATION = "us"
        PROCESSOR_ID = "abb1ab40cbac8a9c"
        
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        extracted_text = ""
        processing_method = ""
        
        if file_extension in ['.pdf', '.tiff']:
            extracted_text = _ocr_pdf_document(PROJECT_ID, LOCATION, PROCESSOR_ID, file_path)
            processing_method = "Google Cloud Document AI (PDF/TIFF)"
            
        elif file_extension in ['.png', '.jpeg', '.jpg']:
            extracted_text = _ocr_img(PROJECT_ID, LOCATION, PROCESSOR_ID, file_path)
            processing_method = "Google Cloud Document AI (Image)"
            
        elif file_extension == '.docx':
            extracted_text = _get_text_from_docx(file_path)
            processing_method = "python-docx"
            
        elif file_extension == '.eml':
            extracted_text = _get_text_from_eml(file_path)
            processing_method = "Python email library"
            
        elif file_extension == '.msg':
            extracted_text = _get_text_from_msg(file_path)
            processing_method = "extract-msg"
            
        elif file_extension == '.txt':
            extracted_text = _get_text_from_txt(file_path)
            processing_method = "Direct text reading"
            
        else:
            return {
                "status": "failure",
                "error": f"Unsupported file format: {file_extension}"
            }
        
        # Store extracted data in tool context
        tool_context.state['startup_information'] = extracted_text
        tool_context.state['structured_data'] = ""
        tool_context.state['file_path'] = file_path
        tool_context.state['file_type'] = file_extension
        tool_context.state['processing_method'] = processing_method
        
        return {
            "status": "success",
            "extracted_text": extracted_text,
            "file_type": file_extension,
            "processing_method": processing_method
        }
        
    except Exception as e:
        return {
            "status": "failure", 
            "error": str(e)
        }


def _ocr_pdf_document(project_id: str, location: str, processor_id: str, file_path: str) -> str:
    """
    Performs OCR on a local PDF file using the Google Cloud Document AI API.
    """
    try:
        client_options = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=client_options)
        
        processor_name = client.processor_path(project_id, location, processor_id)
        
        with open(file_path, "rb") as document_file:
            document_content = document_file.read()
        
        raw_document = documentai.RawDocument(
            content=document_content,
            mime_type="application/pdf"
        )
        
        request = documentai.ProcessRequest(
            name=processor_name,
            raw_document=raw_document,
            imageless_mode=True
        )
        
        response = client.process_document(request=request)
        document = response.document
        
        return document.text
        
    except Exception as e:
        raise Exception(f"Error processing PDF with Document AI: {e}")


def _ocr_img(project_id: str, location: str, processor_id: str, file_path: str) -> str:
    """
    Performs OCR on an image file using Google Cloud Document AI.
    """
    try:
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = client.processor_path(project_id, location, processor_id)
        
        with open(file_path, "rb") as image_file:
            image_content = image_file.read()
        
        # Determine MIME type based on file extension
        _, ext = os.path.splitext(file_path)
        mime_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        mime_type = mime_type_map.get(ext.lower(), 'image/jpeg')
        
        raw_document = documentai.RawDocument(
            content=image_content, 
            mime_type=mime_type
        )
        
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        
        return result.document.text
        
    except Exception as e:
        raise Exception(f"Error processing image with Document AI: {e}")


def _get_text_from_docx(file_path: str) -> str:
    """Reads text from a local .docx file."""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        raise Exception(f"Error processing DOCX file: {e}")


def _get_text_from_msg(file_path: str) -> str:
    """Reads text from a local .msg file."""
    try:
        with extract_msg.Message(file_path) as msg:
            return f"From: {msg.sender}\nTo: {msg.to}\nSubject: {msg.subject}\n\n{msg.body}"
    except Exception as e:
        raise Exception(f"Error processing MSG file: {e}")


def _get_text_from_txt(file_path: str) -> str:
    """Reads text directly from a .txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error processing TXT file: {e}")


def _get_text_from_eml(file_path: str) -> str:
    """Extracts text from an .eml file."""
    try:
        with open(file_path, 'rb') as f:
            msg = email.message_from_bytes(f.read())
            main_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "text/plain" in content_type and "attachment" not in content_disposition:
                        main_text = part.get_payload(decode=True).decode()
                        break
            else:
                main_text = msg.get_payload(decode=True).decode()
            return main_text
    except Exception as e:
        raise Exception(f"Error processing EML file: {e}")
