#!/usr/bin/env python3
"""
Logo Integration Script
Adds logo functionality to the existing poster generation system
"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.error(f"Poster file not found: {poster_path}")
            return None
            
        if not os.path.exists(logo_path):
            logger.error(f"Logo file not found: {logo_path}")
            return None
        
        # Open poster image
        with Image.open(poster_path) as poster_img:
            poster_width, poster_height = poster_img.size
            logger.info(f"Processing poster: {poster_width}x{poster_height}")
            
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
                logger.info(f"Logo resized to: {new_logo_width}x{new_logo_height}")
                
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
                logger.info(f"Logo added successfully to poster: {poster_path}")
                return poster_path
                
    except Exception as e:
        logger.error(f"Error adding logo to poster: {e}")
        return None

def test_integration():
    """Test the logo integration functionality"""
    print("🧪 Testing Logo Integration...")
    
    # Check for existing posters
    poster_dir = "static/uploads/posters"
    if os.path.exists(poster_dir):
        poster_files = [f for f in os.listdir(poster_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if poster_files:
            poster_path = os.path.join(poster_dir, poster_files[0])
            print(f"✅ Using existing poster: {poster_files[0]}")
            
            # Check for logo files
            logo_dir = "static/uploads/logos"
            if os.path.exists(logo_dir):
                logo_files = [f for f in os.listdir(logo_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                if logo_files:
                    logo_path = os.path.join(logo_dir, logo_files[0])
                    print(f"✅ Using logo: {logo_files[0]}")
                    
                    # Test logo addition
                    print(f"\n🎯 Adding logo to existing poster...")
                    result = add_logo_to_poster_top(poster_path, logo_path)
                    
                    if result:
                        print(f"✅ Logo added successfully!")
                        print(f"📁 Check the poster: {poster_path}")
                    else:
                        print(f"❌ Failed to add logo")
                else:
                    print("❌ No logo files found")
            else:
                print("❌ Logo directory not found")
        else:
            print("❌ No poster files found")
    else:
        print("❌ Poster directory not found")
    
    print("\n🎉 Integration test complete!")

def show_usage_examples():
    """Show usage examples for the logo integration"""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    
    print("\n1️⃣ Basic Logo Addition:")
    print("""
    # Add logo to poster
    poster_path = "static/uploads/posters/my_poster.jpg"
    logo_path = "static/uploads/logos/company_logo.png"
    result = add_logo_to_poster_top(poster_path, logo_path)
    """)
    
    print("\n2️⃣ Logo with Company Information:")
    print("""
    # Add logo with company info
    company_info = {
        'company_name': 'Acme Corporation',
        'phone': '+1 (555) 123-4567',
        'email': 'info@acme.com',
        'website': 'www.acme.com',
        'address': '123 Business St, City, State'
    }
    
    result = add_logo_to_poster_top(poster_path, logo_path, company_info)
    """)
    
    print("\n3️⃣ Integration in Flask Route:")
    print("""
    # In your Flask route
    if form.show_logo.data and current_user.logo_filename:
        logo_path = os.path.join('static', 'uploads', 'logos', current_user.logo_filename)
        company_info = {
            'company_name': current_user.business_name,
            'phone': current_user.phone,
            'email': current_user.email,
            'website': current_user.website
        }
        add_logo_to_poster_top(poster_path, logo_path, company_info)
    """)

if __name__ == "__main__":
    print("🎨 Logo Integration Script")
    print("=" * 40)
    
    # Test integration
    test_integration()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n🚀 Ready to integrate with your poster generation system!")
    print("📝 Copy the add_logo_to_poster_top function to your image_service.py")
    print("🔧 Update your routes.py to call this function when logo is selected") 