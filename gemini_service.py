import os
import logging
from google import genai
from google.genai import types
from flask import current_app

# Initialize Gemini client with fallback
def get_gemini_client():
    """Get Gemini client with proper error handling"""
    api_key = os.environ.get("GEMINI_API_KEY") or current_app.config.get("GEMINI_API_KEY", "")
    
    if not api_key or api_key == "your-gemini-api-key-here":
        logging.warning("GEMINI_API_KEY not set - image generation will be disabled")
        return None
    
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        logging.error(f"Failed to initialize Gemini client: {e}")
        return None

def generate_poster_image(prompt, output_path):
    """
    PRODUCTION-READY: Generate poster image with comprehensive error handling
    
    Args:
        prompt (str): The text prompt for image generation
        output_path (str): Path where the generated image will be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    import time
    
    try:
        # Validate inputs
        if not prompt or not prompt.strip():
            logging.error("Empty or invalid prompt provided")
            return False
            
        if not output_path:
            logging.error("No output path provided")
            return False
        
        # Get Gemini client
        client = get_gemini_client()
        if not client:
            logging.error("Gemini client not available - check API key configuration")
            return False
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Enhanced prompt for professional poster generation with header/footer space
        enhanced_prompt = f"""Create a professional, eye-catching poster with the following requirements:
        
        Content: {prompt.strip()}
        
        Style guidelines:
        - High-resolution, print-quality design (at least 1024x1024)
        - Professional typography and layout
        - Balanced composition with clear visual hierarchy
        - Vibrant but tasteful color scheme
        - Main content should be centered and leave space at top and bottom for text overlays
        - Clean, modern aesthetic suitable for business use
        - Avoid cluttered designs or excessive text
        - Include visual elements that complement the content theme
        - Suitable for both digital and print media
        - Professional business poster style
        - Design should work well with header and footer text overlays
        - Main visual content should be in the center 2/3 of the image
        """
        
        # Implement retry logic for API resilience
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting to generate image (attempt {attempt + 1}/{max_retries})")
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )
                
                if not response:
                    logging.error("No response received from Gemini API")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                
                if not response.candidates:
                    logging.error("No candidates returned from Gemini API")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                
                content = response.candidates[0].content
                if not content or not content.parts:
                    logging.error("No content parts in response")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                
                # Process response parts
                image_saved = False
                for part in content.parts:
                    if part.text:
                        logging.info(f"Gemini response text: {part.text[:100]}...")
                    elif part.inline_data and part.inline_data.data:
                        try:
                            # Validate image data
                            image_data = part.inline_data.data
                            if len(image_data) < 1000:  # Suspiciously small image
                                logging.warning(f"Image data seems too small: {len(image_data)} bytes")
                                continue
                            
                            # Save image with atomic write (write to temp file first)
                            temp_path = output_path + '.tmp'
                            with open(temp_path, 'wb') as f:
                                f.write(image_data)
                            
                            # Validate saved image
                            try:
                                from PIL import Image
                                with Image.open(temp_path) as test_img:
                                    if test_img.size[0] < 100 or test_img.size[1] < 100:
                                        logging.error(f"Generated image too small: {test_img.size}")
                                        os.remove(temp_path)
                                        continue
                            except Exception as validation_error:
                                logging.error(f"Image validation failed: {validation_error}")
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                continue
                            
                            # Move temp file to final location (atomic operation)
                            import shutil
                            shutil.move(temp_path, output_path)
                            
                            logging.info(f"Image saved successfully to {output_path}")
                            image_saved = True
                            break
                            
                        except Exception as save_error:
                            logging.error(f"Error saving image data: {save_error}")
                            if os.path.exists(temp_path):
                                try:
                                    os.remove(temp_path)
                                except:
                                    pass
                            continue
                
                if image_saved:
                    return True
                else:
                    logging.error("No valid image data found in response")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                    
            except Exception as api_error:
                error_msg = str(api_error)
                logging.error(f"Gemini API error (attempt {attempt + 1}): {error_msg}")
                
                # Check for specific error types
                if "500" in error_msg or "INTERNAL" in error_msg:
                    logging.warning("Gemini API internal server error - will retry")
                elif "429" in error_msg or "quota" in error_msg.lower():
                    logging.error("API quota exceeded or rate limited")
                    return False
                elif "key" in error_msg.lower() and "invalid" in error_msg.lower():
                    logging.error("Invalid API key - check GEMINI_API_KEY configuration")
                    return False
                elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                    logging.warning("Network connectivity issue - will retry")
                else:
                    logging.error(f"Unexpected API error: {error_msg}")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return False
        
        logging.error("All retry attempts failed")
        return False
        
    except Exception as e:
        logging.error(f"Unexpected error in generate_poster_image: {e}")
        return False

def validate_prompt(prompt):
    """
    Validate and sanitize the prompt for appropriate content
    
    Args:
        prompt (str): The user input prompt
        
    Returns:
        tuple: (is_valid, sanitized_prompt or error_message)
    """
    try:
        # Basic content filtering
        inappropriate_keywords = [
            'violence', 'explicit', 'nsfw', 'adult', 'inappropriate',
            'harmful', 'offensive', 'hate', 'discriminatory'
        ]
        
        prompt_lower = prompt.lower()
        for keyword in inappropriate_keywords:
            if keyword in prompt_lower:
                return False, f"Content contains inappropriate material: {keyword}"
        
        # Length validation
        if len(prompt) < 10:
            return False, "Prompt is too short. Please provide more details."
        
        if len(prompt) > 1000:
            return False, "Prompt is too long. Please keep it under 1000 characters."
        
        # Basic sanitization
        sanitized_prompt = prompt.strip()
        
        return True, sanitized_prompt
        
    except Exception as e:
        logging.error(f"Error validating prompt: {str(e)}")
        return False, "Error validating prompt content"
