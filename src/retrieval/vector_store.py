import pinecone
from pinecone import Pinecone, ServerlessSpec

class VectorStore:
    def __init__(self, api_key, environment, index_name, dimension):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        
        # Create index if it doesn't exist
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=environment)
            )
        self.index = self.pc.Index(index_name)
    
    def upsert_vectors(self, documents, embeddings):
        vectors = [(str(i), emb, {"text": doc}) for i, (doc, emb) in enumerate(zip(documents, embeddings))]
        self.index.upsert(vectors)
    
    def query(self, embedding, top_k=3):
        results = self.index.query(vector=embedding, top_k=top_k, include_metadata=True)
        return [match['metadata']['text'] for match in results['matches']]