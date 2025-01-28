from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import base64
load_dotenv()
from langchain_core.messages import HumanMessage

def encode_image(image_path):
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def load_img_model():
    img_model=ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",temperature=0,max_tokens=2000,
    timeout=4000)
    return img_model

def image_label(prompt,img_base64,model_img):
    message_content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
    ]

    # Invoke the model
    msg = model_img.invoke([HumanMessage(content=message_content)])

    # Process the response
    response = msg.content
    return response

def get_dress_type():
    img_path=r'D:\Dress Up\OIP.jpg'
    img_64=encode_image(img_path)
    model=load_img_model()
    prompt1="You are a assistant to label the image in two of the option 1.Pant , 2.Shirt if does not come under any category return image is invalid"
    #prompt1=prompt1.format(prom)
    output=image_label(prompt1,img_64,model)
    return output
dress_type = get_dress_type()
