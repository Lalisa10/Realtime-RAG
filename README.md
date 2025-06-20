# Realtime RAG Chatbot

A chatbot that uses Retrieval-Augmented Generation (RAG) with Gemini Assistant and Pinecone vector database.

## Setup

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd realtime_rag_chatbot
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   - Create a `.env` file in the root directory.

   - Add your Gemini and Confluent API keys:

   ```bash
   GEMINI_API_KEY=
   CONFLUENT_BOOTSTRAP_SERVERS=
   CONFLUENT_API_KEY=
   CONFLUENT_API_SECRET=
   ```

5. **Prepare data**:

   - Run the following command to run crawl data:
   ```bash
   python -m src.crawl.crawl_from_scratch
   ````

6. **Run the chatbot**:

   ```bash
   python src/main.py
   ```
7. **Run ELK cluster and Redis Stack**:

   ```bash
   docker compose up -d
   ```
## Usage

- Open the Gradio interface in your browser (URL provided in the terminal).
- Enter your question in the textbox, and the chatbot will respond using RAG.
