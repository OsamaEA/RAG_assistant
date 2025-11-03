from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
    
class PgvectorTableSchemaEnums(Enum):
    ID = "id"
    METADATA = "metadata"
    TEXT = "text"
    CHUNK_ID = "chunk_id"
    _PREFIX = "_pgvector"
    VECTOR = "vector"

class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"
    INNER_PRODUCT = "inner_product"

class PgVectorIndexTypeEnums(Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"
