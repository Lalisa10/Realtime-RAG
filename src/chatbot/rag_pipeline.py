from retrieval.embedding import EmbeddingGenerator
from retrieval.vector_store import VectorStore
from chatbot.gemini_client import GeminiClient
from cache.QuestionCache import QuestionCache

class RAGPipeline:
    def __init__(self, config):
        self.config = config
        self.embedding_generator = EmbeddingGenerator(config['embedding']['model'])
        self.vector_store = VectorStore(
            index_name=config['elasticsearch']['index_name'],
            dimension=config['embedding']['dimension']
        )
        self.gemini_client = GeminiClient(
            config['gemini']['api_key'],
            config['gemini']['model']
        )
        if config['elasticsearch']['initialize']:
            print('Initialize vector store')
            self.initialize_vector_store()

        self.cache = QuestionCache(config)
    
    def initialize_vector_store(self):
        # Load sample data and create embeddings
        with open('data/raw/sample_data.txt', 'r') as file:
            documents = file.read().split('\n\n')
        embeddings = [self.embedding_generator.generate(doc) for doc in documents]
        self.vector_store.upsert_vectors(documents, embeddings)
    
    def query(self, user_input):
        cache_result = self.cache.process_question(user_input, similarity_threshold=self.config["cache"]["similarity_threshold"])
        if cache_result:
            print("Found existing result!")
            return cache_result
        # Generate embedding for user query
        query_embedding = self.embedding_generator.generate(user_input)
        
        # Retrieve relevant documents
        retrieved_docs = self.vector_store.query(query_embedding, top_k=3)
        context = "\n".join(retrieved_docs)
        
        # Generate response using Gemini
        response = self.gemini_client.generate_response(user_input, context)
        self.cache.store_question(user_input, response, self.config['cache']['ttl'])
        return response