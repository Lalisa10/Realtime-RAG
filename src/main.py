import yaml
from dotenv import load_dotenv
from chatbot.rag_pipeline import RAGPipeline
from interfaces.web import launch_gradio
from utils.util import resolve_env_vars

def load_config(config_path):
    with open(config_path, 'r') as file:
        raw_config = yaml.safe_load(file)
    config = resolve_env_vars(raw_config)
    return config

def main():
    # Load environment variables
    load_dotenv()

    # Load configuration
    config = load_config('config/config.yaml')

    # Initialize RAG pipeline
    rag_pipeline = RAGPipeline(config)
    
    # Launch Gradio interface
    launch_gradio(rag_pipeline)

if __name__ == "__main__":
    main()