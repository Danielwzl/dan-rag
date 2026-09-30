from typing import List


# ============================================================
# 1. Fixed-size chunking
# ============================================================

def fixed_size_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> List[str]:
    """
    Split text into chunks based on character count.

    Example:
        chunk_size = 1000
        overlap = 150

    Chunk 1: characters 0 - 999
    Chunk 2: characters 850 - 1849
    Chunk 3: characters 1700 - 2699
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


# ============================================================
# 2. Sentence-based chunking
# ============================================================

def sentence_chunks(
    text: str,
    sentences_per_chunk: int = 5,
    overlap_sentences: int = 1
) -> List[str]:
    """
    Split text based on sentences.

    Example:
        sentences_per_chunk = 5
        overlap_sentences = 1

    Chunk 1:
        Sentence 1
        Sentence 2
        Sentence 3
        Sentence 4
        Sentence 5

    Chunk 2:
        Sentence 5
        Sentence 6
        Sentence 7
        Sentence 8
        Sentence 9
    """

    if sentences_per_chunk <= 0:
        raise ValueError(
            "sentences_per_chunk must be greater than 0"
        )

    if overlap_sentences < 0:
        raise ValueError(
            "overlap_sentences cannot be negative"
        )

    if overlap_sentences >= sentences_per_chunk:
        raise ValueError(
            "overlap_sentences must be smaller than "
            "sentences_per_chunk"
        )

    # Simple sentence splitting.
    # This is intentionally lightweight for our first version.
    sentences = []

    for sentence in text.replace("!", ".").replace("?", ".").split("."):
        sentence = sentence.strip()

        if sentence:
            sentences.append(sentence + ".")

    chunks = []

    step = sentences_per_chunk - overlap_sentences

    for start in range(0, len(sentences), step):
        chunk_sentences = sentences[
            start:start + sentences_per_chunk
        ]

        if not chunk_sentences:
            break

        chunks.append(" ".join(chunk_sentences))

        if start + sentences_per_chunk >= len(sentences):
            break

    return chunks


# ============================================================
# 3. Paragraph-based chunking
# ============================================================

def paragraph_chunks(
    text: str,
    paragraphs_per_chunk: int = 2,
    overlap_paragraphs: int = 0
) -> List[str]:
    """
    Split text based on paragraphs.

    Paragraphs are expected to be separated by blank lines.
    """

    if paragraphs_per_chunk <= 0:
        raise ValueError(
            "paragraphs_per_chunk must be greater than 0"
        )

    if overlap_paragraphs < 0:
        raise ValueError(
            "overlap_paragraphs cannot be negative"
        )

    if overlap_paragraphs >= paragraphs_per_chunk:
        raise ValueError(
            "overlap_paragraphs must be smaller than "
            "paragraphs_per_chunk"
        )

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []

    step = paragraphs_per_chunk - overlap_paragraphs

    for start in range(0, len(paragraphs), step):
        chunk_paragraphs = paragraphs[
            start:start + paragraphs_per_chunk
        ]

        if not chunk_paragraphs:
            break

        chunks.append("\n\n".join(chunk_paragraphs))

        if start + paragraphs_per_chunk >= len(paragraphs):
            break

    return chunks


# ============================================================
# 4. Recursive chunking
# ============================================================

def recursive_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> List[str]:
    """
    Recursively split text using increasingly smaller separators.

    Priority:

        Paragraph
           ↓
        Line
           ↓
        Sentence
           ↓
        Space
           ↓
        Character

    This tries to preserve semantic structure before falling
    back to smaller pieces.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    separators = [
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]

    chunks = _recursive_split(
        text,
        separators,
        chunk_size
    )

    # Add overlap after the initial recursive split.
    if overlap == 0:
        return chunks

    result = []

    for index, chunk in enumerate(chunks):
        if index == 0:
            result.append(chunk)
            continue

        previous_chunk = chunks[index - 1]

        overlap_text = previous_chunk[-overlap:]

        combined = overlap_text + " " + chunk

        result.append(combined[:chunk_size])

    return result


def _recursive_split(
    text: str,
    separators: List[str],
    chunk_size: int
) -> List[str]:
    """
    Internal helper for recursive_chunks().
    """

    text = text.strip()

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    if not separators:
        return fixed_size_chunks(
            text,
            chunk_size=chunk_size,
            overlap=0
        )

    separator = separators[0]

    if separator == "":
        return fixed_size_chunks(
            text,
            chunk_size=chunk_size,
            overlap=0
        )

    parts = text.split(separator)

    chunks = []
    current = ""

    for part in parts:
        part = part.strip()

        if not part:
            continue

        candidate = (
            part
            if not current
            else current + separator + part
        )

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)

            # If this individual part is still too large,
            # recursively split it using the next separator.
            if len(part) > chunk_size:
                smaller_chunks = _recursive_split(
                    part,
                    separators[1:],
                    chunk_size
                )

                chunks.extend(smaller_chunks)
                current = ""
            else:
                current = part

    if current:
        chunks.append(current)

    return chunks


# ============================================================
# 5. Page-based chunking
# ============================================================

def page_chunks(pages: List[dict]) -> List[dict]:
    """
    Keep each PDF page as one chunk.

    Expected input:

        [
            {
                "page": 1,
                "text": "..."
            },
            {
                "page": 2,
                "text": "..."
            }
        ]

    Returns:

        [
            {
                "page": 1,
                "text": "..."
            },
            ...
        ]
    """

    chunks = []

    for page in pages:
        text = page["text"].strip()

        if not text:
            continue

        chunks.append({
            "page": page["page"],
            "text": text
        })

    return chunks


# ============================================================
# 6. Utility
# ============================================================

def print_chunks(chunks: List[str]) -> None:
    """
    Print chunks for debugging.
    """

    print(f"\nTotal chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks):
        print("\n" + "=" * 60)
        print(f"Chunk {index}")
        print("=" * 60)
        print(chunk)