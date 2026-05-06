from dotenv import load_dotenv; load_dotenv('./.env')
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client(api_key=os.getenv('GEM_API_KEY'))
print('Testing Gemini image generation...')
try:
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp-image-generation',
        contents='A simple blue circle on white background',
        config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
    )
    found_img = False
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            img = Image.open(BytesIO(part.inline_data.data))
            img.save('/tmp/test_gemini.webp', 'WEBP')
            print(f'SUCCESS: {img.size} image saved ({os.path.getsize("/tmp/test_gemini.webp")} bytes)')
            found_img = True
    if not found_img:
        print('No image in response, parts:', [p.text[:50] if p.text else "<img>" for p in response.candidates[0].content.parts])
except Exception as e:
    print(f'Gemini failed: {type(e).__name__}: {e}')
