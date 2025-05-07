#from .indexing import ingest_documents, run_indexing_pipeline

from .simple_text_indexing import SimpleTextIndexer 
from .metadata_aware_indexing import MetadataAwareTextIndexer, TaggedMetadataIndexer

def load_indexer(config):
    if config['indexing_strategy'] == 'simple':
        return SimpleTextIndexer(config)
    elif config['indexing_strategy'] == 'metadata_aware':
        return MetadataAwareTextIndexer(config)
    elif config['indexing_strategy'] == 'metadata_aware_with_tags':
        return TaggedMetadataIndexer(config)
    else:
        raise ValueError(f"Unsupported indexing_strategy: {config['indexing_strategy'] }")
    
    