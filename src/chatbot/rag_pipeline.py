from retrieval.embedding import EmbeddingGenerator
from retrieval.vector_store import VectorStore
from chatbot.gemini_client import GeminiClient

class RAGPipeline:
    def __init__(self, config):
        self.config = config
        self.embedding_generator = EmbeddingGenerator(config['embedding']['model'])
        self.vector_store = VectorStore(
            config['pinecone']['api_key'],
            config['pinecone']['environment'],
            config['pinecone']['index_name'],
            config['embedding']['dimension']
        )
        self.gemini_client = GeminiClient(
            config['gemini']['api_key'],
            config['gemini']['model']
        )
        self.initialize_vector_store()
    
    def initialize_vector_store(self):
        # Load sample data and create embeddings
        with open('data/raw/sample_data.txt', 'r') as file:
            documents = file.read().split('\n\n')
        embeddings = [self.embedding_generator.generate(doc) for doc in documents]
        self.vector_store.upsert_vectors(documents, embeddings)
    
    def query(self, user_input):
        # Generate embedding for user query
        query_embedding = self.embedding_generator.generate(user_input)
        
        # Retrieve relevant documents
        retrieved_docs = self.vector_store.query(query_embedding, top_k=3)
        context = "\n".join(retrieved_docs)
        
        # Generate response using Gemini
        response = self.gemini_client.generate_response(user_input, context)
        return response