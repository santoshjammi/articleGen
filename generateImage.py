from PIL import Image
from io import BytesIO
import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv('./.env')

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
GEM_API_KEY = os.getenv("GEM_API_KEY")

# Only import Gemini SDK when OpenRouter is not configured
_gemini_client = None
def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        _gemini_client = genai.Client(api_key=GEM_API_KEY)
    return _gemini_client


def _save_pil_image(image, filename):
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(filename, 'WEBP', quality=85, optimize=True, method=6)
    print(f"Saved WebP image: {filename} (optimized for web)")


def _generate_via_pollinations(prompt, filename):
    """
    Generate image via Pollinations.ai — completely free, no API key.
    Retries with exponential backoff on 429 rate-limit responses.
    """
    import urllib.parse, time
    encoded = urllib.parse.quote(prompt[:300])
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        "?width=1024&height=1024&model=flux&nologo=true&enhance=true"
    )
    for attempt in range(2):
        if attempt > 0:
            print(f"  Pollinations rate-limited, retrying in 10s...")
            time.sleep(10)
        img_resp = requests.get(url, timeout=60)
        if img_resp.status_code == 429:
            continue
        img_resp.raise_for_status()
        image = Image.open(BytesIO(img_resp.content))
        _save_pil_image(image, filename)
        return
    raise RuntimeError("Pollinations rate-limit exceeded after 2 retries")


def _generate_via_openrouter(prompt, filename):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/images/generations",
        headers=headers,
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    body = resp.text
    if not body.strip():
        raise ValueError("OpenRouter images endpoint returned empty response")
    data = resp.json()
    item = data["data"][0]

    if item.get("b64_json"):
        image_bytes = base64.b64decode(item["b64_json"])
    elif item.get("url"):
        img_resp = requests.get(item["url"], timeout=60)
        img_resp.raise_for_status()
        image_bytes = img_resp.content
    else:
        raise ValueError("OpenRouter image response has neither url nor b64_json")

    image = Image.open(BytesIO(image_bytes))
    _save_pil_image(image, filename)


def _generate_via_gemini(prompt, filename):
    """Generate image via Gemini Imagen (stable fallback)."""
    from google.genai import types
    client = _get_gemini_client()

    # Try Imagen 4 fast (predict API)
    try:
        response = client.models.generate_images(
            model="imagen-4.0-fast-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1),
        )
        image_bytes = response.generated_images[0].image.image_bytes
        image = Image.open(BytesIO(image_bytes))
        _save_pil_image(image, filename)
        return
    except Exception as e:
        print(f"  Gemini Imagen-4 failed ({e}), trying gemini-2.5-flash-image...")

    # Fallback: gemini-2.5-flash-image (multimodal generateContent)
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            _save_pil_image(image, filename)
            return
    raise RuntimeError("Gemini returned no image data")


def generateImage(prompt, filename):
    """
    Generate an image and save it to filename.
    Tries (in order): Pollinations → OpenRouter → Gemini.
    Returns filename on success, None on total failure
    (so callers can fall back to a placeholder URL).
    """
    print(filename)

    if os.path.exists(filename):
        print(f"Image {filename} already exists, skipping generation.")
        return filename

    # 1. Pollinations (free, no key required)
    try:
        print(f"🎨 Generating image via Pollinations.ai...")
        _generate_via_pollinations(prompt, filename)
        if os.path.exists(filename):
            return filename
    except Exception as e:
        print(f"⚠️  Pollinations failed: {e}")

    # 2. Gemini (Imagen-4 fast → gemini-2.5-flash-image fallback)
    if GEM_API_KEY:
        try:
            print(f"🎨 Trying Gemini image generation...")
            _generate_via_gemini(prompt, filename)
            if os.path.exists(filename):
                return filename
        except Exception as e:
            print(f"⚠️  Gemini image generation failed: {e}")

    print(f"❌ All image generation methods failed for: {filename}")
    return None
def convert_to_webp(input_path, output_path=None, quality=85):
    """
    Convert an existing image to WebP format
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path for the output WebP image (optional)
        quality (int): WebP quality (0-100, default 85)
    
    Returns:
        str: Path to the converted WebP image
    """
    if output_path is None:
        # Generate output path by changing extension to .webp
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.webp"
    
    try:
        if not os.path.exists(input_path):
            print(f"Input image not found: {input_path}")
            return None
            
        if os.path.exists(output_path):
            print(f"WebP image already exists: {output_path}")
            return output_path
            
        # Open and convert the image
        with Image.open(input_path) as image:
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save as WebP
            image.save(output_path, 
                      'WEBP', 
                      quality=quality,
                      optimize=True,
                      method=6)
            
            print(f"Converted to WebP: {input_path} -> {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error converting {input_path} to WebP: {e}")
        return None

def batch_convert_to_webp(images_dir="./images/", quality=85):
    """
    Convert all existing images in the images directory to WebP format
    
    Args:
        images_dir (str): Directory containing images
        quality (int): WebP quality (0-100, default 85)
    
    Returns:
        dict: Summary of conversion results
    """
    converted = []
    skipped = []
    errors = []
    
    if not os.path.exists(images_dir):
        print(f"Images directory not found: {images_dir}")
        return {"converted": 0, "skipped": 0, "errors": 0}
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.webp', '.webp', '.webp')):
                input_path = os.path.join(root, file)
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}.webp"
                
                result = convert_to_webp(input_path, output_path, quality)
                
                if result:
                    converted.append(result)
                    # Optionally remove the original file
                    # os.remove(input_path)  # Uncomment to delete originals
                elif os.path.exists(output_path):
                    skipped.append(output_path)
                else:
                    errors.append(input_path)
    
    summary = {
        "converted": len(converted),
        "skipped": len(skipped), 
        "errors": len(errors),
        "converted_files": converted,
        "skipped_files": skipped,
        "error_files": errors
    }
    
    print(f"\nWebP Conversion Summary:")
    print(f"✅ Converted: {summary['converted']} images")
    print(f"⏭️  Skipped: {summary['skipped']} images (already exist)")
    print(f"❌ Errors: {summary['errors']} images")
    
    return summary
        
# for file in os.listdir('./images/'):
#     if '.webp' in file:
#         print("./images/"+file)
#         im = Image.open("./images/"+file)
#         newName="./images/"+os.path.splitext(file)[0]+'.webp'
#         print(newName)
#         im.save(newName)
if __name__ == "__main__":
    # Create images directory if it doesn't exist
    os.makedirs('./images/', exist_ok=True)
    
    # Sample prompt for testing
    sample_prompt = "A futuristic AI laboratory with scientists working on advanced artificial intelligence research, modern technology, clean and bright environment, high-tech equipment, professional photography style"
    
    # Sample filename
    sample_filename = "./images/01-sample_ai_research_lab.webp"
    
    print("🎨 Generating sample image...")
    print(f"📝 Prompt: {sample_prompt}")
    print(f"💾 Saving to: {sample_filename}")
    
    # Generate the sample image
    result = generateImage(sample_prompt, sample_filename)
    
    if result:
        print(f"✅ Successfully generated image: {result}")
    else:
        print("❌ Failed to generate image")