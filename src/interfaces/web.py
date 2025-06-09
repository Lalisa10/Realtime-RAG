import gradio as gr

def launch_gradio(rag_pipeline):
    def chatbot_interface(user_input):
        return rag_pipeline.query(user_input)
    
    iface = gr.Interface(
        fn=chatbot_interface,
        inputs=gr.Textbox(lines=2, placeholder="Nhập câu hỏi của bạn..."),
        outputs="text",
        title="Realtime RAG Chatbot",
        description="Hỏi bất kỳ câu hỏi nào, chatbot sẽ truy xuất thông tin và trả lời bằng Gemini Assistant."
    )
    iface.launch()