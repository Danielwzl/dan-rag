import chromadb
import ollama


LLM_MODEL = "deepseek-r1:8b"
EMBEDDING_MODEL = "nomic-embed-text"


client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    name="documents"
)


def search_documents(question, top_k=3):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question
    )

    query_embedding = response["embeddings"][0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


def build_context(results):

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    context_parts = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        context_parts.append(
            f"""
Source: {metadata['source']}
Page: {metadata['page']}

{document}
"""
        )

    return "\n\n".join(context_parts)


def ask_deepseek(question, context):

    prompt = f"""
You are a helpful assistant.

Answer the user's question using ONLY
the information provided in the context.

If the answer cannot be found in the context,
say that you could not find the answer
in the provided documents.

Do not make up information.

Context:

{context}

Question:

{question}
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def rag(question):

    results = search_documents(question)

    context = build_context(results)

    answer = ask_deepseek(
        question,
        context
    )

    return answer, results


while True:

    question = input("\nQuestion: ")

    if question.lower() in ["exit", "quit"]:
        break

    answer, results = rag(question)

    print("\nAnswer:")
    print(answer)

    print("\nSources:")

    for metadata in results["metadatas"][0]:

        print(
            f"- {metadata['source']}, "
            f"page {metadata['page']}"
        )