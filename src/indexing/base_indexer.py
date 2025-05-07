from abc import ABC, abstractmethod

class BaseIndexer(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def ingest(self):
        """Load and preprocess documents."""
        pass

    @abstractmethod
    def index(self):
        """Embed and store the documents."""
        pass
