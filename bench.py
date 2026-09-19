import os
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from src.chunking import SentenceChunker
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.models import Document
from src.embeddings import OpenAIEmbedder

def openai_llm(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content

def main():
    print("=== BẮT ĐẦU CHẠY BENCHMARK THỰC TẾ (OPENAI) ===\n")
    data_dir = Path("data/university-uet")
    files = list(data_dir.glob("*.md"))
    
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    documents = []
    
    for f in files:
        content = f.read_text(encoding="utf-8")
        parts = content.split("---")
        if len(parts) >= 3:
            raw_meta = parts[1]
            body = "---".join(parts[2:]).strip()
            
            meta = {}
            for line in raw_meta.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            
            chunks = chunker.chunk(body)
            for i, c in enumerate(chunks):
                if len(c) > 8000:
                    c = c[:8000]
                documents.append(Document(
                    id=f"{meta.get('doc_id')}_{i}",
                    content=c,
                    metadata=meta
                ))
    
    print(f"Đã cắt ra tổng cộng {len(documents)} chunks từ {len(files)} file.\n")
    
    embedder = OpenAIEmbedder()
    store = EmbeddingStore(collection_name="benchmark_real", embedding_fn=embedder)
    store.add_documents(documents)
    
    agent = KnowledgeBaseAgent(store=store, llm_fn=openai_llm)
    
    queries = [
        "Sinh viên hệ Chuẩn phải đóng học phí theo hình thức nào?",
        "Khi nào sinh viên bị kỷ luật Cảnh cáo thì Điểm rèn luyện tối đa là bao nhiêu?",
        "Sinh viên người dân tộc thiểu số thuộc hộ nghèo được miễn giảm học phí ra sao?",
        "Để đạt điểm rèn luyện loại xuất sắc cần bao nhiêu điểm?",
        "Sinh viên khuyết tật có được ưu tiên điểm rèn luyện không?"
    ]
    
    for i, q in enumerate(queries, 1):
        print(f"Câu hỏi {i}: {q}")
        
        filter_dict = None
        if i == 1:
            filter_dict = {"audience": "student"}
            
        if filter_dict:
            results = store.search_with_filter(q, filter_dict, top_k=3)
        else:
            results = store.search(q, top_k=3)
            
        if results:
            top_chunk = results[0]
            print(f"-> Top 1 Chunk (Score: {top_chunk['score']:.3f}): {top_chunk['content'][:80].replace(chr(10), ' ')}...")
        else:
            print("-> Không tìm thấy chunk nào phù hợp!")
            
        answer = agent.answer(q, top_k=3)
        print(f"-> Agent Answer: {answer.replace(chr(10), ' ')}\n")

if __name__ == "__main__":
    main()
