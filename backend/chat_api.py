import google.generativeai as genai

# Đặt API key ở đây
genai.configure(api_key="AIzaSyDUrDYvzw4wisZEoAGB6jC2a1IIFs2JAKY")  # 🔁 Thay bằng API key của bạn

model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

def chat_with_gemini(message):
    response = model.generate_content(message)
    return response.text
