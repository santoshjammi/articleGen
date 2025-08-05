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
                    
                    # Convert to RGB if necessary (WebP doesn't support RGBA with certain settings)
                    if image.mode in ('RGBA', 'LA', 'P'):
                        # Create a white background for transparent images
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Save as WebP with high quality and optimization
                    image.save(filename, 
                              'WEBP', 
                              quality=85,  # High quality but still compressed
                              optimize=True,  # Enable optimization
                              method=6)  # Best compression method (0-6, 6 is slowest but best compression)
                    print(f"Saved WebP image: {filename} (optimized for web)")
        except Exception as e:
            print(f'Error in generating the Image: {e}')
        return filename
    else:
        print(f"Image {filename} already exists, skipping generation.")
        return filename

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
    