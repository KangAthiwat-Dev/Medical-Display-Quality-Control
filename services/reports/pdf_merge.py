import fitz


def merge_pdf_bytes(pdf_documents: list[bytes]) -> bytes:
    output = fitz.open()
    try:
        for pdf_bytes in pdf_documents:
            if not pdf_bytes:
                continue
            with fitz.open(stream=pdf_bytes, filetype="pdf") as src:
                output.insert_pdf(src)
        return output.tobytes()
    finally:
        output.close()
