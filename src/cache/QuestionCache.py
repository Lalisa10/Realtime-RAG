from sentence_transformers import SentenceTransformer
import redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from retrieval.embedding import EmbeddingGenerator
import numpy as np
import json
from utils.util import load_config

class QuestionCache:
    def __init__(self, config):
        self.config = config
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        self.embedding_generator = EmbeddingGenerator(config['embedding']['model'])

        self.schema = (
        TextField("question"),
        VectorField("embedding", "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": config['embedding']['dimension'],
            "DISTANCE_METRIC": config['cache']['distance_metric'],
            "INITIAL_CAP": config['cache']['initial_cap']
            })
        )

        # Xóa index nếu tồn tại
        try:
            self.redis_client.ft("questions_idx").dropindex(delete_documents=True)
            print("Existing index dropped")
        except redis.exceptions.ResponseError as e:
            print("No index to drop, proceeding to create")

        self.redis_client.ft("questions_idx").create_index(
            fields=self.schema,
            definition=IndexDefinition(prefix=["question:"], index_type=IndexType.HASH)
        )
    
    def embed_question(self, question):
        return np.array(self.embedding_generator.generate(question)).astype(np.float32).tobytes()
    
    def store_question(self, question, response, ttl=3600):
        embedding = self.embed_question(question)
        key = f"question:{question}"
        self.redis_client.hset(key, mapping={
            "question": question,
            "embedding": embedding,
            "response": response  # Lưu phản hồi từ Gemini API
        })
        if ttl:  # Chỉ đặt TTL nếu được cung cấp
            self.redis_client.expire(key, ttl)
    
    def search_similar_question(self, question, k=5):
        query_embedding = self.embed_question(question)
        query = f"* => [KNN {k} @embedding $vec AS score]"
        
        results = self.redis_client.ft("questions_idx").search(
            query=query,
            query_params={"vec": query_embedding}
        )
        
        return [
            {
                "question": doc["question"],
                "response": doc["response"],
                "score": doc["score"]
            } for doc in results.docs
        ]
    
    def process_question(self, question, similarity_threshold=0.9):
        query_embedding = self.embed_question(question)
        query = f"* => [KNN 5 @embedding $vec AS score]"
        results = self.redis_client.ft("questions_idx").search(
            query=query,
            query_params={"vec": query_embedding}
        )
        if not results.docs:
            return None
        score = float(results.docs[0]["score"])
        if results.docs and score < (1 - similarity_threshold):
            print(f"Trả về từ cache (câu hỏi tương tự) distance = {score}")
            return results.docs[0]["response"]

        return None

if __name__ == "__main__":
    config = load_config('config/config.yaml')
    cache = QuestionCache(config)
    response = "Có, rất đẹp trai!"
    cache.store_question('Trúc đẹp trai không?', response)
    print(cache.process_question('Trúc đẹp chứ?', 0.8))