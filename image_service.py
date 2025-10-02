import os
import uuid
from PIL import Image, ImageDraw, ImageFont
from flask import current_app
import logging

def add_watermark(image_path, output_path, is_premium=False):
    """
    PRODUCTION-READY: Add watermark to image with comprehensive error handling
    
    Args:
        image_path (str): Path to the source image
        output_path (str): Path for the output image
        is_premium (bool): Whether user has premium subscription
        
    Returns:
        bool: True if successful, False otherwise
    """
    import shutil
    
    try:
        # Validate inputs
        if not image_path or not output_path:
            logging.error("Invalid input or output path provided")
            return False
            
        if not os.path.exists(image_path):
            logging.error(f"Input file does not exist: {image_path}")
            return False
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Premium users get watermark-free images
        if is_premium:
            try:
                shutil.copy2(image_path, output_path)
                logging.info(f"Premium user - copied without watermark: {output_path}")
                return True
            except Exception as e:
                logging.error(f"Error copying file for premium user: {e}")
                return False
        
        # Apply watermark for free users with robust error handling
        try:
            with Image.open(image_path) as img:
                # Validate image
                if img.size[0] == 0 or img.size[1] == 0:
                    logging.error("Invalid image dimensions")
                    return False
                
                # Convert to RGBA for watermarking
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create watermark overlay
                watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark)
                
                # Watermark text
                watermark_text = "Postasy - Upgrade for Watermark-Free"
                
                # Safe font loading with multiple fallbacks
                font = None
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/TTF/arial.ttf"    # Alternative Linux
                ]
                
                font_size = max(12, min(20, img.width // 40))  # Responsive but bounded
                
                for font_path in font_paths:
                    try:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, font_size)
                            break
                    except Exception:
                        continue
                
                # Fallback to default font
                if font is None:
                    try:
                        font = ImageFont.load_default()
                        font_size = 16  # Default size for fallback font
                    except Exception:
                        font = None
                        font_size = 16  # Ensure font_size is always defined
                
                # Calculate text position with error handling
                if font:
                    try:
                        bbox = draw.textbbox((0, 0), watermark_text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                    except Exception:
                        text_width = len(watermark_text) * font_size // 2
                        text_height = font_size
                else:
                    text_width = len(watermark_text) * 8
                    text_height = 16
                
                # Position at bottom right with safe margins
                margin = max(10, min(20, img.width // 100))
                x = max(0, img.width - text_width - margin)
                y = max(0, img.height - text_height - margin)
                
                # Draw semi-transparent background
                bg_padding = max(5, font_size // 4)
                try:
                    draw.rectangle([
                        max(0, x - bg_padding), max(0, y - bg_padding),
                        min(img.width, x + text_width + bg_padding), 
                        min(img.height, y + text_height + bg_padding)
                    ], fill=(0, 0, 0, 128))
                    
                    # Draw watermark text
                    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
                except Exception as e:
                    logging.warning(f"Error drawing watermark, using simplified version: {e}")
                    # Fallback: simple text without background
                    draw.text((x, y), "POSTASY", font=font, fill=(255, 255, 255, 255))
                
                # Combine with original image
                try:
                    watermarked = Image.alpha_composite(img, watermark).convert('RGB')
                except Exception as e:
                    logging.warning(f"Error compositing, using blend method: {e}")
                    # Fallback blend method
                    watermarked = Image.blend(img.convert('RGB'), watermark.convert('RGB'), 0.1)
                
                # Save with multiple format attempts
                save_successful = False
                
                # Try JPEG first
                try:
                    watermarked.save(output_path, 'JPEG', quality=95, optimize=True)
                    save_successful = True
                    logging.info(f"Successfully saved watermarked image as JPEG: {output_path}")
                except Exception as jpeg_error:
                    logging.warning(f"JPEG save failed: {jpeg_error}")
                    
                    # Try PNG as fallback
                    try:
                        png_path = output_path.rsplit('.', 1)[0] + '.png'
                        watermarked.save(png_path, 'PNG', optimize=True)
                        save_successful = True
                        logging.info(f"Saved as PNG fallback: {png_path}")
                    except Exception as png_error:
                        logging.error(f"PNG fallback also failed: {png_error}")
                
                return save_successful
                
        except Exception as processing_error:
            logging.error(f"Error processing image: {processing_error}")
            
            # Last resort: copy original file
            try:
                shutil.copy2(image_path, output_path)
                logging.warning(f"Processing failed, copied original: {output_path}")
                return True
            except Exception as copy_error:
                logging.error(f"Even file copy failed: {copy_error}")
                return False
                
    except Exception as e:
        logging.error(f"Unexpected error in add_watermark: {e}")
        return False

def add_profile_overlay(image_path, output_path, profile_data, selected_fields):
    """
    Add user profile information overlay to the poster with blank spaces at top and bottom
    
    Args:
        image_path (str): Path to the source image
        output_path (str): Path for the output image
        profile_data (dict): User profile information
        selected_fields (list): List of fields to display
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Create a new image with extra space at top and bottom
            original_width, original_height = img.size
            header_height = original_height // 6  # 1/6 of original height for header
            footer_height = original_height // 6  # 1/6 of original height for footer
            new_height = original_height + header_height + footer_height
            
            # Create new image with white background
            new_img = Image.new('RGB', (original_width, new_height), (255, 255, 255))
            
            # Paste the original image in the center
            new_img.paste(img, (0, header_height))
            
            # Create overlay for text
            overlay = Image.new('RGBA', new_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Prepare text to display
            display_text = []
            logo_path = None
            
            for field in selected_fields:
                if field in profile_data and profile_data[field]:
                    value = profile_data[field]
                    if field == 'full_name':
                        display_text.append(value)
                    elif field == 'business_name':
                        display_text.append(value)
                    elif field == 'phone':
                        display_text.append(f"📞 {value}")
                    elif field == 'address':
                        display_text.append(f"📍 {value}")
                    elif field == 'website':
                        display_text.append(f"🌐 {value}")
                    elif field == 'facebook':
                        display_text.append(f"📘 {value}")
                    elif field == 'instagram':
                        display_text.append(f"📷 {value}")
                    elif field == 'twitter':
                        display_text.append(f"🐦 {value}")
                    elif field == 'linkedin':
                        display_text.append(f"💼 {value}")
                    elif field == 'logo' and profile_data.get('logo_filename'):
                        logo_path = os.path.join('static', 'uploads', 'logos', profile_data['logo_filename'])
            
            if display_text:
                # Font settings
                try:
                    font_size = max(16, original_width // 60)
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                    bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size + 4)
                except:
                    font = ImageFont.load_default()
                    bold_font = ImageFont.load_default()
                
                # Calculate text area
                line_height = font_size + 6
                text_area_height = len(display_text) * line_height + 40
                
                # Create background for footer text
                footer_bg_y = new_height - text_area_height
                draw.rectangle([0, footer_bg_y, original_width, new_height], 
                             fill=(0, 0, 0, 180))
                
                # Draw footer text
                y_offset = footer_bg_y + 20
                for i, text in enumerate(display_text):
                    current_font = bold_font if i < 2 else font  # Name and business name in bold
                    text_color = (255, 255, 255, 255)
                    
                    # Center align text
                    bbox = draw.textbbox((0, 0), text, font=current_font)
                    text_width = bbox[2] - bbox[0]
                    x_offset = (original_width - text_width) // 2
                    
                    draw.text((x_offset, y_offset), text, font=current_font, fill=text_color)
                    y_offset += line_height
                
                # Add header text (business name or full name)
                header_text = []
                if 'business_name' in selected_fields and profile_data.get('business_name'):
                    header_text.append(profile_data['business_name'])
                elif 'full_name' in selected_fields and profile_data.get('full_name'):
                    header_text.append(profile_data['full_name'])
                
                if header_text:
                    # Create background for header text
                    header_bg_height = header_height // 2
                    draw.rectangle([0, 0, original_width, header_bg_height], 
                                 fill=(0, 0, 0, 180))
                    
                    # Draw header text
                    header_y = header_bg_height // 2 - font_size // 2
                    for text in header_text:
                        bbox = draw.textbbox((0, 0), text, font=bold_font)
                        text_width = bbox[2] - bbox[0]
                        x_offset = (original_width - text_width) // 2
                        
                        draw.text((x_offset, header_y), text, font=bold_font, fill=(255, 255, 255, 255))
            
            # Add logo if selected and exists
            if logo_path and os.path.exists(logo_path):
                try:
                    with Image.open(logo_path) as logo_img:
                        # Convert logo to RGBA if needed
                        if logo_img.mode != 'RGBA':
                            logo_img = logo_img.convert('RGBA')
                        
                        # Calculate logo size (max 100px height, maintain aspect ratio)
                        max_logo_height = 100
                        logo_width, logo_height = logo_img.size
                        scale_factor = min(max_logo_height / logo_height, 1.0)
                        new_logo_width = int(logo_width * scale_factor)
                        new_logo_height = int(logo_height * scale_factor)
                        
                        # Resize logo
                        logo_img = logo_img.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
                        
                        # Position logo in top-right corner with margin
                        logo_x = original_width - new_logo_width - 20
                        logo_y = 20
                        
                        # Create logo overlay
                        logo_overlay = Image.new('RGBA', new_img.size, (0, 0, 0, 0))
                        logo_overlay.paste(logo_img, (logo_x, logo_y), logo_img)
                        
                        # Combine logo with text overlay
                        combined_overlay = Image.alpha_composite(overlay, logo_overlay)
                        
                        # Combine with new image
                        final_img = Image.alpha_composite(new_img.convert('RGBA'), combined_overlay).convert('RGB')
                except Exception as logo_error:
                    logging.error(f"Error adding logo overlay: {logo_error}")
                    # Fallback to text-only overlay
                    final_img = Image.alpha_composite(new_img.convert('RGBA'), overlay).convert('RGB')
            else:
                # Combine with new image (text-only)
                final_img = Image.alpha_composite(new_img.convert('RGBA'), overlay).convert('RGB')
            final_img.save(output_path, 'JPEG', quality=95)
            return True
            
    except Exception as e:
        logging.error(f"Error adding profile overlay: {str(e)}")
        return False

def generate_filename(extension='.jpg'):
    """Generate a unique filename"""
    return str(uuid.uuid4()) + extension

def save_uploaded_file(file, upload_folder):
    """
    Save uploaded file with unique filename
    
    Args:
        file: FileStorage object from Flask
        upload_folder (str): Directory to save the file
        
    Returns:
        str: Filename if successful, None otherwise
    """
    try:
        if file and file.filename:
            # Get file extension
            extension = os.path.splitext(file.filename)[1].lower()
            if extension not in ['.jpg', '.jpeg', '.png']:
                return None
            
            # Generate unique filename
            filename = generate_filename(extension)
            filepath = os.path.join(upload_folder, filename)
            
            # Ensure directory exists
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file.save(filepath)
            return filename
    except Exception as e:
        logging.error(f"Error saving uploaded file: {str(e)}")
    
    return None

def add_logo_to_poster_top(poster_path, logo_path, company_info=None):
    """
    Add logo to the top white space of a poster
    
    Args:
        poster_path (str): Path to the poster image
        logo_path (str): Path to the logo image
        company_info (dict): Optional company information
        
    Returns:
        str: Path to the output image, or None if failed
    """
    try:
        # Validate input files
        if not os.path.exists(poster_path):
            logging.error(f"Poster file not found: {poster_path}")
            return None
            
        if not os.path.exists(logo_path):
            logging.error(f"Logo file not found: {logo_path}")
            return None
        
        # Open poster image
        with Image.open(poster_path) as poster_img:
            poster_width, poster_height = poster_img.size
            logging.info(f"Processing poster: {poster_width}x{poster_height}")
            
            # Convert to RGBA for transparency support
            if poster_img.mode != 'RGBA':
                poster_img = poster_img.convert('RGBA')
            
            # Open and process logo
            with Image.open(logo_path) as logo_img:
                # Convert logo to RGBA
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')
                
                # Calculate logo size (maintain aspect ratio)
                logo_width, logo_height = logo_img.size
                max_logo_height = 80
                scale_factor = min(max_logo_height / logo_height, 1.0)
                new_logo_width = int(logo_width * scale_factor)
                new_logo_height = int(logo_height * scale_factor)
                
                # Resize logo
                logo_img = logo_img.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
                logging.info(f"Logo resized to: {new_logo_width}x{new_logo_height}")
                
                # Calculate logo position in top white space
                logo_x = (poster_width - new_logo_width) // 2  # Center horizontally
                logo_y = 30  # Top margin
                
                # Create a copy of the poster for modification
                result_img = poster_img.copy()
                
                # Add background behind logo for better visibility
                bg_width = new_logo_width + 20
                bg_height = new_logo_height + 20
                bg_x = logo_x - 10
                bg_y = logo_y - 10
                
                # Create background overlay
                bg_overlay = Image.new('RGBA', result_img.size, (0, 0, 0, 0))
                bg_draw = ImageDraw.Draw(bg_overlay)
                bg_draw.rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], 
                                fill=(255, 255, 255, 200))
                
                # Composite background
                result_img = Image.alpha_composite(result_img, bg_overlay)
                
                # Create logo overlay
                logo_overlay = Image.new('RGBA', result_img.size, (0, 0, 0, 0))
                logo_overlay.paste(logo_img, (logo_x, logo_y), logo_img)
                
                # Composite logo onto poster
                result_img = Image.alpha_composite(result_img, logo_overlay)
                
                # Add company information if provided
                if company_info:
                    draw = ImageDraw.Draw(result_img)
                    
                    # Try to load a professional font
                    try:
                        font_size = 20
                        font = ImageFont.truetype("arial.ttf", font_size)
                        bold_font = ImageFont.truetype("arialbd.ttf", font_size + 2)
                    except:
                        font = ImageFont.load_default()
                        bold_font = ImageFont.load_default()
                    
                    # Calculate text position (below logo)
                    text_y = logo_y + new_logo_height + 20
                    text_color = (0, 0, 0, 255)
                    
                    # Add company name
                    if company_info.get('company_name'):
                        company_name = company_info['company_name']
                        bbox = draw.textbbox((0, 0), company_name, font=bold_font)
                        text_width = bbox[2] - bbox[0]
                        text_x = (poster_width - text_width) // 2
                        
                        # Add text background
                        bg_padding = 10
                        draw.rectangle([
                            text_x - bg_padding, text_y - bg_padding,
                            text_x + text_width + bg_padding, text_y + font_size + bg_padding
                        ], fill=(255, 255, 255, 200))
                        
                        draw.text((text_x, text_y), company_name, font=bold_font, fill=text_color)
                        text_y += font_size + 10
                    
                    # Add contact information
                    contact_fields = ['phone', 'email', 'website', 'address']
                    for field in contact_fields:
                        if company_info.get(field):
                            text = f"{field.title()}: {company_info[field]}"
                            bbox = draw.textbbox((0, 0), text, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_x = (poster_width - text_width) // 2
                            
                            # Add text background
                            bg_padding = 5
                            draw.rectangle([
                                text_x - bg_padding, text_y - bg_padding,
                                text_x + text_width + bg_padding, text_y + font_size + bg_padding
                            ], fill=(255, 255, 255, 180))
                            
                            draw.text((text_x, text_y), text, font=font, fill=text_color)
                            text_y += font_size + 5
                
                # Save result
                result_img.save(poster_path, 'PNG', quality=95)
                logging.info(f"Logo added successfully to poster: {poster_path}")
                return poster_path
                
    except Exception as e:
        logging.error(f"Error adding logo to poster: {e}")
        return None
