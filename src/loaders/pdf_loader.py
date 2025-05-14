from langchain.document_loaders import PyPDFLoader

def load_pdfs_from_folder(folder_path: str):
    import os
    all_docs = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, file))
            all_docs.extend(loader.load())
    return all_docs
