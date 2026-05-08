#!/usr/bin/env python3
"""Extract all PDFs from 软件体系结构参考资料 into RAG-ready chunks."""
import pymupdf, os, json

PDF_DIR = "/mnt/e/项目/大作业/软件体系结构参考资料"
OUT_DIR = "/mnt/e/workspace/UserRegister/arch-assistant/data/rag_chunks"
os.makedirs(OUT_DIR, exist_ok=True)

pdfs = sorted([f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')])
print(f"Found {len(pdfs)} PDFs")

all_chunks = []

for pdf_file in pdfs:
    path = os.path.join(PDF_DIR, pdf_file)
    doc = pymupdf.open(path)
    print(f"  {pdf_file}: {len(doc)} pages")
    
    full_text = ""
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            full_text += f"\n--- Page {i+1} ---\n{text}"
    
    # Chunk by natural boundaries: double newlines, then page breaks
    raw_chunks = full_text.split("\n\n\n")
    
    for ci, chunk in enumerate(raw_chunks):
        chunk = chunk.strip()
        if len(chunk) < 50:  # skip tiny fragments
            continue
        
        # If chunk is too long, split further
        if len(chunk) > 2000:
            # Split by paragraph (single newline)
            paragraphs = [p.strip() for p in chunk.split("\n") if p.strip()]
            current = ""
            for p in paragraphs:
                if len(current) + len(p) > 1500 and current:
                    all_chunks.append({
                        "source": pdf_file,
                        "chunk_id": f"{pdf_file}_{len(all_chunks)}",
                        "text": current
                    })
                    current = p
                else:
                    current = (current + "\n" + p).strip()
            if current:
                all_chunks.append({
                    "source": pdf_file,
                    "chunk_id": f"{pdf_file}_{len(all_chunks)}",
                    "text": current
                })
        else:
            all_chunks.append({
                "source": pdf_file,
                "chunk_id": f"{pdf_file}_{len(all_chunks)}",
                "text": chunk
            })

# Save chunks
with open(os.path.join(OUT_DIR, "chunks.json"), "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

# Also save a raw combined text for reference
with open(os.path.join(OUT_DIR, "full_text.txt"), "w", encoding="utf-8") as f:
    for c in all_chunks:
        f.write(f"\n\n=== {c['source']} ===\n{c['text']}")

total_chars = sum(len(c['text']) for c in all_chunks)
print(f"\nDone: {len(all_chunks)} chunks, {total_chars} chars total")
print(f"Saved to: {OUT_DIR}")
