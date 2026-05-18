import os
import re
from typing import List, Tuple
import pdfplumber

class DocumentParser:
    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, dict]:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == ".pdf":
            return DocumentParser._parse_pdf(file_path)
        elif ext == ".txt":
            return DocumentParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def _parse_pdf(file_path: str) -> Tuple[str, dict]:
        content = ""
        metadata = {
            "source": file_path,
            "title": os.path.basename(file_path),
            "doc_type": "pdf"
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n\n"
        except Exception as e:
            raise ValueError(f"Failed to parse PDF file {file_path}: {str(e)}")
        
        content = DocumentParser._clean_text(content)
        return content, metadata
    
    @staticmethod
    def _parse_txt(file_path: str) -> Tuple[str, dict]:
        metadata = {
            "source": file_path,
            "title": os.path.basename(file_path),
            "doc_type": "txt"
        }
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to parse TXT file {file_path}: {str(e)}")
        
        content = DocumentParser._clean_text(content)
        return content, metadata
    
    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\t+", " ", text)
        text = text.strip()
        return text
    
    @staticmethod
    def load_documents(data_dir: str) -> List[Tuple[str, dict]]:
        documents = []
        supported_extensions = (".pdf", ".txt")
        
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.lower().endswith(supported_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        content, metadata = DocumentParser.parse_file(file_path)
                        metadata["department"] = os.path.basename(root)
                        documents.append((content, metadata))
                        print(f"Loaded: {file_path}")
                    except Exception as e:
                        print(f"Failed to load {file_path}: {str(e)}")
        
        return documents