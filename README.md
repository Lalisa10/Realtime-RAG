# Realtime RAG Chatbot

A chatbot that uses Retrieval-Augmented Generation (RAG) with Gemini Assistant and Pinecone vector database.

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Lalisa10/Realtime-RAG.git
   cd realtime_rag_chatbot
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   - Create a `.env` file in the root directory.

   - Add your Gemini and Pinecone API keys:

     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     PINECONE_API_KEY=your_pinecone_api_key_here
     ```

4. **Prepare data**:

   - Run crawl data from Tiki.vn

5. **Run the chatbot**:

   ```bash
   python src/main.py
   ```

## Usage

- Open the Gradio interface in your browser (URL provided in the terminal).
- Enter your question in the textbox, and the chatbot will respond using RAG.

## Example

- Input: "What is RAG in AI?"
- Output: "RAG stands for Retrieval-Augmented Generation, a technique that combines information retrieval and content generation to improve AI responses."
