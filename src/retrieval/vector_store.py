from elasticsearch import Elasticsearch
from message_queue.kafka import produce
import json
import numpy as np

class VectorStore:
    def __init__(self, index_name, dimension):
        # Kết nối tới Elasticsearch
        self.es = Elasticsearch("http://localhost:9200")
        self.index_name = index_name
        self.dimension = dimension
        
        # Kiểm tra và tạo index nếu chưa tồn tại
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "embedding": {"type": "dense_vector", "dims": dimension},
                            "text": {"type": "text"}
                        }
                    }
                }
            )
    
    def upsert_vectors(self, documents, embeddings):
        # Gửi embeddings và documents tới Kafka
        for doc, emb in zip(documents, embeddings):
            record = {
                "text": doc,
                "embedding": emb,
            }
            #print(type(json.dumps(record).encode('utf-8')))
            produce('rag_embeddings', json.dumps(record).encode('utf-8'))
    
    def query(self, embedding, top_k=3):
        # Tìm kiếm k-nearest neighbors trong Elasticsearch
        query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": embedding}
                    }
                }
            },
            "size": top_k
        }
        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"]["text"] for hit in response["hits"]["hits"]]