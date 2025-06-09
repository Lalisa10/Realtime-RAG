from google import genai

class GeminiClient:
    def __init__(self, api_key, model_name):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_response(self, prompt, context):
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}\nAnswer:"
        response = self.client.models.generate_content(model=self.model_name, contents=full_prompt)
        return response.text