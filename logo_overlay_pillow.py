#!/usr/bin/env python3
"""
Logo Overlay with Pillow
A comprehensive program to add logos to the top white space of generated posters
"""

from PIL import Image, ImageDraw, ImageFont
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogoOverlayProcessor:
    """Professional logo overlay processor for posters"""
    
    def __init__(self, logo_path=None, output_dir="output"):
        self.logo_path = logo_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def add_logo_to_poster(self, poster_path, logo_path=None, position='top-right', 
                          max_logo_height=100, margin=20, background_color=(255, 255, 255, 180)):
        """
        Add logo to poster with professional positioning and styling
        
        Args:
            poster_path (str): Path to the poster image
            logo_path (str): Path to the logo image (optional if set in constructor)
            position (str): 'top-right', 'top-left', 'top-center', 'bottom-right', 'bottom-left', 'bottom-center'
            max_logo_height (int): Maximum height of the logo in pixels
            margin (int): Margin from edges in pixels
            background_color (tuple): RGBA color for logo background (optional)
            
        Returns:
            str: Path to the output image, or None if failed
        """
        try:
            # Use constructor logo_path if not provided
            if logo_path is None:
                logo_path = self.logo_path
                
            if not logo_path or not os.path.exists(logo_path):
                logger.error(f"Logo file not found: {logo_path}")
                return None
                
            if not os.path.exists(poster_path):
                logger.error(f"Poster file not found: {poster_path}")
                return None
            
            # Open poster image
            with Image.open(poster_path) as poster_img:
                poster_width, poster_height = poster_img.size
                logger.info(f"Poster dimensions: {poster_width}x{poster_height}")
                
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
                    scale_factor = min(max_logo_height / logo_height, 1.0)
                    new_logo_width = int(logo_width * scale_factor)
                    new_logo_height = int(logo_height * scale_factor)
                    
                    # Resize logo
                    logo_img = logo_img.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
                    logger.info(f"Logo resized to: {new_logo_width}x{new_logo_height}")
                    
                    # Calculate logo position based on specified position
                    logo_x, logo_y = self._calculate_logo_position(
                        poster_width, poster_height, new_logo_width, new_logo_height, 
                        position, margin
                    )
                    
                    # Create a copy of the poster for modification
                    result_img = poster_img.copy()
                    
                    # Add background behind logo if specified
                    if background_color:
                        # Create background rectangle
                        bg_width = new_logo_width + 20  # Extra padding
                        bg_height = new_logo_height + 20
                        bg_x = logo_x - 10
                        bg_y = logo_y - 10
                        
                        # Create background overlay
                        bg_overlay = Image.new('RGBA', result_img.size, (0, 0, 0, 0))
                        bg_draw = ImageDraw.Draw(bg_overlay)
                        bg_draw.rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], 
                                        fill=background_color)
                        
                        # Composite background
                        result_img = Image.alpha_composite(result_img, bg_overlay)
                    
                    # Create logo overlay
                    logo_overlay = Image.new('RGBA', result_img.size, (0, 0, 0, 0))
                    logo_overlay.paste(logo_img, (logo_x, logo_y), logo_img)
                    
                    # Composite logo onto poster
                    result_img = Image.alpha_composite(result_img, logo_overlay)
                    
                    # Save result
                    output_path = os.path.join(self.output_dir, f"poster_with_logo_{os.path.basename(poster_path)}")
                    result_img.save(output_path, 'PNG', quality=95)
                    
                    logger.info(f"Logo added successfully to: {output_path}")
                    return output_path
                    
        except Exception as e:
            logger.error(f"Error adding logo to poster: {e}")
            return None
    
    def _calculate_logo_position(self, poster_width, poster_height, logo_width, logo_height, 
                               position, margin):
        """Calculate logo position based on specified position"""
        
        if position == 'top-right':
            x = poster_width - logo_width - margin
            y = margin
        elif position == 'top-left':
            x = margin
            y = margin
        elif position == 'top-center':
            x = (poster_width - logo_width) // 2
            y = margin
        elif position == 'bottom-right':
            x = poster_width - logo_width - margin
            y = poster_height - logo_height - margin
        elif position == 'bottom-left':
            x = margin
            y = poster_height - logo_height - margin
        elif position == 'bottom-center':
            x = (poster_width - logo_width) // 2
            y = poster_height - logo_height - margin
        else:
            # Default to top-right
            x = poster_width - logo_width - margin
            y = margin
            
        return x, y
    
    def add_logo_with_text_overlay(self, poster_path, logo_path=None, company_name=None, 
                                  contact_info=None, position='top-right'):
        """
        Add logo with company text overlay for professional business posters
        
        Args:
            poster_path (str): Path to the poster image
            logo_path (str): Path to the logo image
            company_name (str): Company name to display
            contact_info (dict): Contact information (phone, email, website, etc.)
            position (str): Logo position
            
        Returns:
            str: Path to the output image, or None if failed
        """
        try:
            # First add the logo
            temp_output = self.add_logo_to_poster(poster_path, logo_path, position)
            if not temp_output:
                return None
            
            # If we have company information, add text overlay
            if company_name or contact_info:
                with Image.open(temp_output) as img:
                    # Create text overlay
                    draw = ImageDraw.Draw(img)
                    
                    # Try to load a professional font
                    try:
                        font_size = 24
                        font = ImageFont.truetype("arial.ttf", font_size)
                        bold_font = ImageFont.truetype("arialbd.ttf", font_size + 4)
                    except:
                        # Fallback to default font
                        font = ImageFont.load_default()
                        bold_font = ImageFont.load_default()
                    
                    # Calculate text position (below logo)
                    logo_x, logo_y = self._calculate_logo_position(
                        img.width, img.height, 100, 100, position, 20
                    )
                    
                    text_y = logo_y + 120  # Below logo
                    text_color = (0, 0, 0, 255)  # Black text
                    
                    # Add company name
                    if company_name:
                        bbox = draw.textbbox((0, 0), company_name, font=bold_font)
                        text_width = bbox[2] - bbox[0]
                        text_x = logo_x + (100 - text_width) // 2  # Center under logo
                        
                        # Add text background for readability
                        bg_padding = 10
                        draw.rectangle([
                            text_x - bg_padding, text_y - bg_padding,
                            text_x + text_width + bg_padding, text_y + font_size + bg_padding
                        ], fill=(255, 255, 255, 200))
                        
                        draw.text((text_x, text_y), company_name, font=bold_font, fill=text_color)
                        text_y += font_size + 10
                    
                    # Add contact information
                    if contact_info:
                        for key, value in contact_info.items():
                            if value:
                                text = f"{key.title()}: {value}"
                                bbox = draw.textbbox((0, 0), text, font=font)
                                text_width = bbox[2] - bbox[0]
                                text_x = logo_x + (100 - text_width) // 2
                                
                                # Add text background
                                bg_padding = 5
                                draw.rectangle([
                                    text_x - bg_padding, text_y - bg_padding,
                                    text_x + text_width + bg_padding, text_y + font_size + bg_padding
                                ], fill=(255, 255, 255, 180))
                                
                                draw.text((text_x, text_y), text, font=font, fill=text_color)
                                text_y += font_size + 5
                    
                    # Save final result
                    final_output = os.path.join(self.output_dir, f"poster_with_logo_text_{os.path.basename(poster_path)}")
                    img.save(final_output, 'PNG', quality=95)
                    
                    # Clean up temp file
                    os.remove(temp_output)
                    
                    logger.info(f"Logo with text overlay added successfully to: {final_output}")
                    return final_output
            else:
                return temp_output
                
        except Exception as e:
            logger.error(f"Error adding logo with text overlay: {e}")
            return None
    
    def create_sample_poster(self, width=800, height=600, text="Sample Business Poster"):
        """Create a sample poster for testing"""
        try:
            # Create a sample poster
            img = Image.new('RGB', (width, height), (240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Add some sample content
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # Center the text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Add text background
            draw.rectangle([x-20, y-20, x+text_width+20, y+text_height+20], 
                         fill=(255, 255, 255, 200))
            draw.text((x, y), text, font=font, fill=(50, 50, 50))
            
            # Save sample poster
            sample_path = os.path.join(self.output_dir, "sample_poster.png")
            img.save(sample_path, 'PNG')
            logger.info(f"Sample poster created: {sample_path}")
            return sample_path
            
        except Exception as e:
            logger.error(f"Error creating sample poster: {e}")
            return None

def main():
    """Main function to demonstrate logo overlay functionality"""
    print("🎨 Logo Overlay with Pillow - Professional Poster Enhancement")
    print("=" * 60)
    
    # Initialize processor
    processor = LogoOverlayProcessor()
    
    # Create sample poster
    print("\n📝 Creating sample poster...")
    sample_poster = processor.create_sample_poster()
    if not sample_poster:
        print("❌ Failed to create sample poster")
        return
    
    # Check for logo files
    logo_dir = "static/uploads/logos"
    if os.path.exists(logo_dir):
        logo_files = [f for f in os.listdir(logo_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if logo_files:
            logo_path = os.path.join(logo_dir, logo_files[0])
            print(f"✅ Using logo: {logo_files[0]}")
            
            # Test different logo positions
            positions = ['top-right', 'top-left', 'top-center']
            
            for position in positions:
                print(f"\n🎯 Testing {position} position...")
                output_path = processor.add_logo_to_poster(
                    sample_poster, logo_path, position=position
                )
                if output_path:
                    print(f"✅ Logo added successfully: {os.path.basename(output_path)}")
                else:
                    print(f"❌ Failed to add logo in {position} position")
            
            # Test with company information
            print(f"\n🏢 Testing with company information...")
            contact_info = {
                'phone': '+1 (555) 123-4567',
                'email': 'info@company.com',
                'website': 'www.company.com'
            }
            
            output_path = processor.add_logo_with_text_overlay(
                sample_poster, logo_path, 
                company_name="Sample Company Inc.",
                contact_info=contact_info
            )
            
            if output_path:
                print(f"✅ Logo with text overlay added: {os.path.basename(output_path)}")
            else:
                print("❌ Failed to add logo with text overlay")
                
        else:
            print("❌ No logo files found in static/uploads/logos")
    else:
        print("❌ Logo directory not found: static/uploads/logos")
    
    print(f"\n📁 Check the '{processor.output_dir}' directory for results")
    print("🎉 Logo overlay demonstration complete!")

if __name__ == "__main__":
    main() 