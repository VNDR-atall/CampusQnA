import re
from typing import List, Tuple, Dict

class TextChunker:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: dict) -> List[Tuple[str, dict]]:
        chunks = []
        text = text.strip()
        
        if len(text) <= self.chunk_size:
            return [(text, metadata.copy())]
        
        sentences = self._split_into_sentences(text)
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length <= self.chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(("".join(current_chunk), metadata.copy()))
                
                overlap_count = self._calculate_overlap(current_chunk)
                current_chunk = current_chunk[-overlap_count:] + [sentence]
                current_length = sum(len(s) for s in current_chunk)
        
        if current_chunk:
            chunks.append(("".join(current_chunk), metadata.copy()))
        
        for i, (_, chunk_metadata) in enumerate(chunks):
            chunk_metadata["chunk_id"] = f"{metadata.get('title', '')}_{i}"
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        sentence_endings = re.compile(r'([。！？；])')
        parts = sentence_endings.split(text)
        sentences = []
        
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i] + parts[i + 1]
            sentence = sentence.strip()
            if sentence:
                sentences.append(sentence)
        
        if parts and not parts[-1].endswith(tuple('。！？；')):
            last_part = parts[-1].strip()
            if last_part:
                sentences.append(last_part)
        
        return sentences
    
    def _calculate_overlap(self, current_chunk: List[str]) -> int:
        overlap_length = 0
        overlap_count = 0
        
        for i in range(len(current_chunk) - 1, -1, -1):
            if overlap_length + len(current_chunk[i]) <= self.chunk_overlap:
                overlap_length += len(current_chunk[i])
                overlap_count += 1
            else:
                break
        
        return max(overlap_count, 1)
    
    def chunk_documents(self, documents: List[Tuple[str, dict]]) -> List[Tuple[str, dict]]:
        all_chunks = []
        
        for content, metadata in documents:
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks