from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
from dotenv import load_dotenv
import json

load_dotenv('./.env')
api_key=os.environ.get('GEM_API_KEY')
client = genai.Client(api_key=api_key)

def generateImage(prompt, filename):
    contents=prompt
    # print(contents)

    print(filename)

    if not os.path.exists(filename):
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
            )
        )

        try:
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save(filename)
        except Exception as e:
            print('Error in generating the Image')
        return filename
    else:
        print(f"Image {filename} already exists, skipping generation.")
        return filename
        
# for file in os.listdir('./images/'):
#     if '.jpg' in file:
#         print("./images/"+file)
#         im = Image.open("./images/"+file)
#         newName="./images/"+os.path.splitext(file)[0]+'.png'
#         print(newName)
#         im.save(newName)
    