import google.generativeai as genai

# Thay bằng API key của bạn
genai.configure(api_key="AIzaSyCQ0oTVt_lDD7fo0ZVrjBm-sXL6fPhq6tU")

# Thử liệt kê các model
try:
    models = genai.list_models()
    for m in models:
        print("Model name:", m.name)
        print("Supported methods:", m.supported_generation_methods)
        print("--------")
except Exception as e:
    print("Lỗi:", e)