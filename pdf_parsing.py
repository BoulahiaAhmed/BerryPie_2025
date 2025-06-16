# import pdfplumber
# import pandas as pd
# from langchain.document_loaders import PyPDFLoader, PDFPlumberLoader

# def parse_pdf_path_langchain(path: str) -> str:
#     """
#     Parse a PDF from local filesystem at `path`, extracting both unstructured text and tables,
#     and return a unified, Markdown-friendly string representation.
#     """
#     # 1. Load unstructured text via LangChain's PyPDFLoader
#     text_loader = PyPDFLoader(path)
#     text_docs = text_loader.load()   # List[Document], one per page

#     # 2. Load with PDFPlumberLoader (LangChain wrapper around pdfplumber)
#     table_loader = PDFPlumberLoader(path)
#     _ = table_loader.load()          # We don't use its text—only ensure any internal setup

#     # 3. Directly open with pdfplumber for high-fidelity table extraction
#     tables_md = []
#     with pdfplumber.open(path) as pdf:
#         for page_num, page in enumerate(pdf.pages, start=1):
#             raw_tables = page.extract_tables()
#             for tbl_idx, raw in enumerate(raw_tables, start=1):
#                 # Build DataFrame: first row = columns
#                 df = pd.DataFrame(raw[1:], columns=raw[0])
#                 md = df.to_markdown(index=False)
#                 tables_md.append(f"\n**Table {page_num}.{tbl_idx}:**\n{md}\n")

#     # 4. Combine page texts and tables
#     parts = []
#     for doc in text_docs:
#         parts.append(doc.page_content.strip())

#     parts.extend(tables_md)
#     return "\n\n".join(parts).strip()


# # Example usage
# if __name__ == "__main__":
#     local_pdf_path = "prospectus.pdf"
#     full_content = parse_pdf_path_langchain(local_pdf_path)
#     print(full_content)
