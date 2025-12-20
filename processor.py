import os
import re
import fitz
from docx import Document

class TextProcessor:
    @staticmethod
    def extract_text(filepath):
        ext = filepath.split('.')[-1].lower()
        text = ""
        if ext == 'pdf':
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text()
        elif ext == 'docx':
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        return text.strip()

    @staticmethod
    def split_into_chunks(text, target_len=2500, first_chunk_len=None):
        # Limpieza básica
        if first_chunk_len is None:
            first_chunk_len = target_len
            
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Dividir por párrafos primero para mantener estructura
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Determinar el target para el chunk actual
            current_target = first_chunk_len if len(chunks) == 0 else target_len
                
            if len(current_chunk) + len(para) < current_target:
                current_chunk += "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Si un solo párrafo es demasiado largo, dividirlo por oraciones
                if len(para) > current_target:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        # Re-evaluar target (podría haber cambiado si acabamos de cerrar un chunk)
                        current_target = first_chunk_len if len(chunks) == 0 else target_len
                        
                        if len(current_chunk) + len(sent) < current_target:
                            current_chunk += " " + sent if current_chunk else sent
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sent
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
