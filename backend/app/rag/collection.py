from pymilvus import FieldSchema, CollectionSchema, DataType, Collection, utility
from .config import COLLECTION_NAME, EMBEDDING_DIM
from .milvus_client import connect_milvus

def get_collection():
    # Ensure Milvus connection exists before any operations
    try:
        connect_milvus()
    except Exception as e:
        # Let downstream operations raise a clear error if connection fails
        print(f"[WARNING] Milvus connection attempt failed: {e}")

    if utility.has_collection(COLLECTION_NAME):
        col = Collection(COLLECTION_NAME)
        try:
            col.load()
        except Exception as e:
            print(f"[WARNING] Failed to load collection {COLLECTION_NAME}: {e}")
        return col

    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("content", DataType.VARCHAR, max_length=2048),
        FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema("source_file", DataType.VARCHAR, max_length=256),
    ]

    schema = CollectionSchema(fields, "RAG collection")
    col = Collection(COLLECTION_NAME, schema)

    col.create_index(
        "embedding",
        {"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 128}}
    )
    col.load()
    return col
