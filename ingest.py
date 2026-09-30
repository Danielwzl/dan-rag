from pathlib import Path

import chromadb
import ollama
from pypdf import PdfReader
from chucking.general import fixed_size_chunks


DOCUMENTS_DIR = Path("documents")
DB_DIR = "chroma_db"
FILE_NAMES = "Daniel_Wang_Cover_Letter_QA_Automation.pdf" or "*.pdf" 

EMBEDDING_MODEL = "nomic-embed-text"


def load_pdf(file_path):
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    return pages


client = chromadb.PersistentClient(
    path=DB_DIR
)

collection = client.get_or_create_collection(
    name="documents"
)


for pdf_file in DOCUMENTS_DIR.glob(FILE_NAMES):

    print(f"Processing: {pdf_file.name}")

    pages = load_pdf(pdf_file)

    for page in pages:

        chunks = fixed_size_chunks(page["text"], chunk_size=1000, overlap=150)

        for index, chunk in enumerate(chunks):

            response = ollama.embed(
                model=EMBEDDING_MODEL,
                input=chunk
            )

            embedding = response["embeddings"][0]

            document_id = (
                f"{pdf_file.stem}"
                f"-page-{page['page']}"
                f"-chunk-{index}"
            )

            collection.upsert(
                ids=[document_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": pdf_file.name,
                    "page": page["page"],
                    "chunk": index
                }]
            )

            print(
                f"  Added page {page['page']} "
                f"chunk {index}"
            )


print("\nIngestion complete.")