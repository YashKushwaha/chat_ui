# loaders/base_loader.py
from typing import List
from langchain.schema import Document

class BaseDocumentLoader:
    def load(self) -> List[Document]:
        raise NotImplementedError()
