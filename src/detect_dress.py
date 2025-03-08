import sys
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

def encode_image(image_path):
    """Convert image to Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def load_img_model():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=2000,
        timeout=4000
    )

def image_label(prompt, img_base64, model_img):
    message_content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
    ]

    # Invoke the model
    msg = model_img.invoke([HumanMessage(content=message_content)])
    
    return msg.content.strip()

def get_dress_type(image_path):
    img_64 = encode_image(image_path)
    model = load_img_model()
    
    prompt = "You are an assistant to label the image in one of the options: 1. Pant, 2. Shirt. If it does not match either, return 'Invalid image'."
    return image_label(prompt, img_64, model)

if __name__ == "__main__":
    image_path = sys.argv[1]  # Get image path from command-line argument
    print(get_dress_type(image_path))  # Print output so Node.js can read it
