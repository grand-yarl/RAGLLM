class TextChunker:
    @staticmethod
    def split_text_into_chunks(text, chunk_size=1000, overlap=200):
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end < len(text):
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end),
                    text.rfind('\n', start, end)
                )
                
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def process_documents(self, documents, chunk_size=1000, overlap=200):
        all_chunks = []
        for filename, text in documents:
            chunks = self.split_text_into_chunks(text, chunk_size, overlap)
            all_chunks.extend(chunks)
            print(f"Document {filename} split into {len(chunks)} chunks")
        
        return all_chunks
