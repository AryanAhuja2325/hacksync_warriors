"""
Visual Agent - Mood Board Generator
Generates visual mood boards from campaign strategies using Pollinations API
"""

import os
import requests
import time
import base64
import json
from typing import Dict, List, Any, Optional
from mistralai import Mistral
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualAgent:
    """
    Generates mood board images from campaign strategy.
    
    Flow:
    1. Campaign Strategy → Visual Prompts (LLM)
    2. Visual Prompts → Image Generation (Pollinations API)
    3. Images → Structured Mood Board
    """
    
    def __init__(self):
        self.pollinations_key = os.getenv("POLLINATIONS_API_KEY")
        mistral_key = os.getenv("MISTRAL_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not self.pollinations_key:
            raise ValueError("POLLINATIONS_API_KEY not found in .env")
        if not mistral_key:
            raise ValueError("MISTRAL_API_KEY not found in .env")
        
        self.mistral_client = Mistral(api_key=mistral_key)
        self.mistral_model = "mistral-large-latest"
        
        # Pollinations endpoint
        self.pollinations_endpoint = "https://image.pollinations.ai/prompt"
        
        # Gemini setup (if key available)
        if self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                
                # Initialize standard Gemini client (no Vertex AI needed)
                self.genai_client = genai.Client(api_key=self.gemini_key)
                self.genai_types = types
                logger.info("✓ Gemini client initialized (image generation capable)")
                    
            except Exception as e:
                logger.warning(f"Gemini setup failed: {e}")
                self.genai_client = None
                self.genai_types = None
        else:
            logger.warning("No GEMINI_API_KEY found - fallback disabled")
            self.genai_client = None
            self.genai_types = None
            self.gcp_project_id = None
        
        # Cache for generated images (prevent regeneration)
        self.image_cache = {}
        
        # Output directory for saved images
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_mood_board(
        self,
        strategy: Dict[str, Any],
        num_variations: int = 4,
        image_size: str = "1024x1024",
        reference_image_path: str = None
    ) -> Dict[str, Any]:
        """
        Generate complete mood board from campaign strategy.
        
        Args:
            strategy: Campaign strategy dict with product, audience, tone, etc.
            num_variations: Number of image variations (default: 4)
            image_size: Image dimensions (default: 1024x1024)
            reference_image_path: Optional path to reference image for image-to-image generation
        
        Returns:
            Mood board dict with images, prompts, and metadata
        """
        logger.info(f"Generating mood board for: {strategy.get('product', 'Unknown')}")
        
        # Step 1: Convert strategy to visual language
        visual_descriptors = self._strategy_to_visual_descriptors(strategy)
        
        # Step 2: Create prompt variations
        visual_prompts = self._create_prompt_variations(
            visual_descriptors,
            num_variations=num_variations
        )
        
        # Step 3: Generate images
        width, height = self._parse_size(image_size)
        mood_board_tiles = []
        
        for i, prompt_data in enumerate(visual_prompts, 1):
            logger.info(f"Generating image {i}/{len(visual_prompts)}")
            
            tile = self._generate_tile(
                prompt=prompt_data["prompt"],
                mood=prompt_data["mood"],
                style=prompt_data["style"],
                width=width,
                height=height,
                tile_id=i,
                reference_image_path=reference_image_path
            )
            
            if tile:
                mood_board_tiles.append(tile)
            
            # Rate limit handling: wait between requests
            if i < len(visual_prompts):
                time.sleep(1)  # 1 second between requests
        
        # Step 4: Build mood board structure
        mood_board = {
            "status": "success" if mood_board_tiles else "failed",
            "product": strategy.get("product", ""),
            "audience": strategy.get("audience", ""),
            "tone": strategy.get("tone", ""),
            "visual_theme": visual_descriptors.get("theme", ""),
            "color_palette": visual_descriptors.get("colors", []),
            "tiles": mood_board_tiles,
            "total_generated": len(mood_board_tiles),
            "requested": num_variations
        }
        
        logger.info(f"Mood board complete: {len(mood_board_tiles)}/{num_variations} tiles generated")
        
        # Save JSON output
        json_filename = f"mood_board_{int(time.time())}.json"
        json_filepath = os.path.join(self.output_dir, json_filename)
        
        try:
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(mood_board, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Mood board JSON saved: {json_filepath}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {str(e)}")
        
        return mood_board
    
    def regenerate_tile(
        self,
        tile_id: int,
        new_style: Optional[str] = None,
        new_mood: Optional[str] = None,
        original_prompt: str = "",
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        Regenerate a single mood board tile with new parameters.
        
        Args:
            tile_id: Tile identifier
            new_style: Override style (e.g., "photographic", "illustration")
            new_mood: Override mood (e.g., "energetic", "calm")
            original_prompt: Original prompt to modify
            width: Image width
            height: Image height
        
        Returns:
            New tile dict
        """
        logger.info(f"Regenerating tile {tile_id}")
        
        # Modify prompt based on new parameters
        modified_prompt = original_prompt
        
        if new_style:
            modified_prompt += f", {new_style} style"
        if new_mood:
            modified_prompt += f", {new_mood} mood"
        
        return self._generate_tile(
            prompt=modified_prompt,
            mood=new_mood or "default",
            style=new_style or "default",
            width=width,
            height=height,
            tile_id=tile_id
        )
    
    def _strategy_to_visual_descriptors(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert campaign strategy to visual language using LLM.
        
        Translates abstract concepts (product, audience, tone) into
        visual descriptors (colors, lighting, style, mood).
        """
        product = strategy.get("product", "")
        audience = strategy.get("audience", "")
        tone = strategy.get("tone", "")
        domain = strategy.get("stylistics", strategy.get("domain", ""))
        
        prompt = f"""You are a visual creative director. Convert this campaign strategy into visual design language.

CAMPAIGN STRATEGY:
- Product: {product}
- Target Audience: {audience}
- Tone: {tone}
- Domain/Style: {domain}

EXTRACT VISUAL DESCRIPTORS in JSON format:
{{
  "product": "CONCRETE product description (e.g., 'reusable water bottle' NOT 'EcoBottle', 'smartphone' NOT 'iPhone 15')",
  "audience": "target demographic (e.g., 'college students', 'young professionals')",
  "theme": "one-sentence visual theme",
  "colors": ["color1", "color2", "color3"],
  "lighting": "lighting style (natural/studio/dramatic/soft)",
  "photography_style": "style (candid/editorial/lifestyle/product)",
  "tone": "emotional feel (energetic/calm/luxurious/minimal)",
  "cultural_context": "cultural relevance (if audience is specific region)",
  "composition": "framing preference (close-up/wide/overhead/portrait)"
}}

CRITICAL: The "product" field must be the ACTUAL PHYSICAL OBJECT TYPE (e.g., "water bottle", "laptop", "sneakers"), NOT a brand name or marketing description.

Return ONLY valid JSON, no additional text."""
        
        try:
            response = self.mistral_client.chat.complete(
                model=self.mistral_model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            descriptors = json.loads(json_str)
            logger.info(f"Visual theme: {descriptors.get('theme', 'N/A')}")
            
            return descriptors
        
        except Exception as e:
            logger.error(f"Error generating visual descriptors: {e}")
            # Fallback to basic descriptors
            return {
                "theme": f"{product} for {audience}",
                "colors": ["vibrant", "modern"],
                "lighting": "natural",
                "photography_style": "lifestyle",
                "emotional_tone": tone,
                "cultural_context": "universal",
                "composition": "balanced"
            }
    
    def _create_prompt_variations(
        self,
        descriptors: Dict[str, Any],
        num_variations: int = 4
    ) -> List[Dict[str, str]]:
        """
        Create multiple visual prompt variations from descriptors.
        
        Generates diverse prompts:
        - Image 1: MANDATORY lifestyle shot (person using product)
        - Images 2-4: Product-focused shots with different angles/moods
        """
        # Extract key info
        product = descriptors.get("product", "product")
        audience = descriptors.get("audience", "people")
        theme = descriptors.get("theme", "")
        colors = ", ".join(descriptors.get("colors", ["natural tones"]))
        lighting = descriptors.get("lighting", "natural daylight")
        tone = descriptors.get("tone", "friendly")
        
        variations = []
        
        # IMAGE 1: MANDATORY - Lifestyle shot with target audience USING the product
        # Be very specific about showing the product being used
        audience_descriptor = ""
        if "college" in audience.lower() or "student" in audience.lower():
            audience_descriptor = "young college student, casual outfit, outdoor campus"
        elif "women" in audience.lower() or "girl" in audience.lower():
            audience_descriptor = "young woman, modern casual clothing, natural setting"
        elif "professional" in audience.lower():
            audience_descriptor = "professional person, business casual, office environment"
        else:
            audience_descriptor = "person from target demographic"
        
        lifestyle_prompt = f"Professional lifestyle photograph: {audience_descriptor} actively using a {product}, holding it and drinking/using the product, candid authentic moment, genuine happy expression, {lighting}, {colors}, bokeh background, photorealistic, high quality commercial photography, 8k"
        
        variations.append({
            "prompt": lifestyle_prompt,
            "mood": "authentic",
            "style": "lifestyle",
            "type": "user_depicting"
        })
        
        # IMAGE 2: Product close-up hero shot
        product_hero = f"Professional product photography: {product} close-up hero shot, premium quality visible, clean white background or minimal surface, {lighting}, {colors}, studio photography, commercial advertising quality, sharp focus, 8k detail"
        
        variations.append({
            "prompt": product_hero,
            "mood": "premium",
            "style": "product photography",
            "type": "product_focus"
        })
        
        # IMAGE 3: Product in lifestyle context (without person)
        context_shot = f"Professional commercial photograph: {product} placed in beautiful lifestyle setting related to {audience}, natural environment, aesthetic composition, {colors}, {lighting}, depth of field, editorial style, 8k quality"
        
        variations.append({
            "prompt": context_shot,
            "mood": "aspirational",
            "style": "editorial",
            "type": "product_focus"
        })
        
        # IMAGE 4: Creative product shot
        creative_shot = f"Creative commercial photograph: {product} from unique angle, artistic composition, {tone} mood, {colors}, dramatic {lighting}, high-end advertising style, magazine quality, 8k resolution"
        
        variations.append({
            "prompt": creative_shot,
            "mood": "creative",
            "style": "cinematic",
            "type": "product_focus"
        })
        
        return variations[:num_variations]
    
    def _generate_tile(
        self,
        prompt: str,
        mood: str,
        style: str,
        width: int = 1024,
        height: int = 1024,
        tile_id: Optional[int] = None,
        reference_image_path: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a single mood board tile using Pollinations API or Gemini.
        
        If reference_image_path is provided, tries Gemini img2img first, then falls back to Pollinations.
        Otherwise uses Pollinations directly.
        """
        # If reference image provided, try Gemini image-to-image first
        if reference_image_path:
            gemini_tile = self._gemini_image_to_image(prompt, mood, style, width, height, tile_id, reference_image_path)
            if gemini_tile:
                return gemini_tile
            else:
                logger.warning("Gemini img2img failed, falling back to Pollinations text-to-image")
                # Continue to Pollinations below
        
        # Check cache
        cache_key = f"{prompt}_{width}x{height}"
        if cache_key in self.image_cache:
            logger.info("Using cached image")
            return self.image_cache[cache_key]
        
        # Encode prompt for URL
        encoded_prompt = requests.utils.quote(prompt)
        url = f"{self.pollinations_endpoint}/{encoded_prompt}"
        
        # Query parameters
        params = {
            "width": width,
            "height": height,
            "model": "flux",
            "nologo": "true",
            "enhance": "false"
        }
        
        # Headers with auth
        headers = {
            "Authorization": f"Bearer {self.pollinations_key}"
        }
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Pollinations API (attempt {attempt + 1}/{max_retries})")
                
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    # Save image to file
                    filename = f"tile_{tile_id or int(time.time())}_{mood}_{style.replace(' ', '_')}.jpg"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Create relative URL
                    image_url = f"{self.output_dir}/{filename}"
                    
                    # Convert to base64
                    base64_data = self._image_to_base64(filepath)
                    
                    # Success - return tile data with URL and base64
                    tile = {
                        "id": tile_id,
                        "prompt": prompt,
                        "mood": mood,
                        "style": style,
                        "image_url": image_url,
                        "base64": base64_data,
                        "image_size": len(response.content),
                        "width": width,
                        "height": height,
                        "generated_at": time.time(),
                        "provider": "pollinations"
                    }
                    
                    # Cache it
                    self.image_cache[cache_key] = tile
                    
                    logger.info(f"✓ Tile saved: {filepath} ({len(response.content)} bytes)")
                    return tile
                
                elif response.status_code == 429:
                    # Rate limited
                    logger.warning(f"Rate limited (429), waiting {retry_delay * 2}s...")
                    time.sleep(retry_delay * 2)
                    retry_delay *= 2  # Exponential backoff
                
                else:
                    logger.error(f"API error {response.status_code}: {response.text[:200]}")
                    
                    # Try fallback on last attempt
                    if attempt == max_retries - 1:
                        return self._fallback_gemini_generation(prompt, mood, style, width, height, tile_id)
            
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return self._fallback_gemini_generation(prompt, mood, style, width, height, tile_id)
            
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                if attempt == max_retries - 1:
                    return self._fallback_gemini_generation(prompt, mood, style, width, height, tile_id)
        
        # All retries failed
        logger.error(f"Failed to generate tile after {max_retries} attempts")
        return None
    
    def _fallback_gemini_generation(
        self,
        prompt: str,
        mood: str,
        style: str,
        width: int,
        height: int,
        tile_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback image generation using Google Gemini.
        
        Uses Imagen 3.0 for image generation.
        """
        if not self.genai_client:
            logger.error("Gemini fallback not available - no API key or client failed to load")
            return None
        
        try:
            logger.info("Using Gemini Imagen fallback for image generation...")
            
            # Gemini prompt for image generation
            gemini_prompt = f"Generate a high-quality, professional product photography image: {prompt}. High resolution, studio lighting, commercial quality."
            
            # Generate image using Gemini Imagen
            response = self.genai_client.models.generate_images(
                model='imagen-3.0-generate-001',
                prompt=gemini_prompt,
                config={
                    'number_of_images': 1,
                    'aspect_ratio': '1:1',
                    'safety_filter_level': 'block_only_high',
                    'person_generation': 'allow_adult'
                }
            )
            
            # Extract image from response
            if response.generated_images and len(response.generated_images) > 0:
                import base64
                
                # Get first generated image
                generated_image = response.generated_images[0]
                
                # Decode base64 image
                image_data = base64.b64decode(generated_image.image.image_bytes)
                
                # Save image to file
                filename = f"tile_{tile_id or int(time.time())}_{mood}_{style.replace(' ', '_')}_gemini.jpg"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                image_url = f"{self.output_dir}/{filename}"
                
                # Convert to base64
                base64_data = self._image_to_base64(filepath)
                
                tile = {
                    "id": tile_id,
                    "prompt": prompt,
                    "mood": mood,
                    "style": style,
                    "image_url": image_url,
                    "base64": base64_data,
                    "image_size": len(image_data),
                    "width": width,
                    "height": height,
                    "generated_at": time.time(),
                    "provider": "gemini"
                }
                
                logger.info(f"✓ Gemini fallback success: {filepath}")
                return tile
            
            logger.warning("Gemini response did not contain image data")
            return None
            
        except Exception as e:
            logger.error(f"Gemini fallback failed: {str(e)}")
            return None
    
    def _gemini_image_to_image(
        self,
        prompt: str,
        mood: str,
        style: str,
        width: int,
        height: int,
        tile_id: Optional[int],
        reference_image_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Image-to-image generation using Gemini generate_content with image input.
        
        Uses gemini-3-pro-image-preview model for multimodal generation.
        """
        if not self.genai_client or not self.genai_types:
            logger.error("Gemini client not available for image-to-image generation")
            return None
        
        try:
            from PIL import Image
            
            logger.info(f"Gemini img2img with reference: {reference_image_path}")
            
            # Load reference image using PIL
            with Image.open(reference_image_path) as img:
                # Create transformation prompt
                transform_prompt = f"""Transform this image with the following requirements:
- Mood: {mood}
- Style: {style}
- Content: {prompt}

Maintain the product essence but completely reimagine the setting, lighting, and atmosphere.
Create a professional, commercial-quality image suitable for a marketing mood board.
High resolution, studio-quality result."""
                
                logger.info(f"Generating with prompt: {transform_prompt[:100]}...")
                
                # Generate content with image input
                response = self.genai_client.models.generate_content(
                    model="gemini-3-pro-image-preview",
                    contents=[transform_prompt, img],
                    config=self.genai_types.GenerateContentConfig(
                        image_config=self.genai_types.ImageConfig(
                            aspect_ratio="1:1",
                            image_size="1K"
                        )
                    )
                )
            
            # Extract image from response
            image_parts = [
                part for part in getattr(response, "parts", [])
                if hasattr(part, "inline_data") and 
                   getattr(part.inline_data, "mime_type", "").startswith("image/")
            ]
            
            if not image_parts:
                logger.warning("No image returned by Gemini")
                return None
            
            # Get image bytes
            image_bytes = image_parts[0].inline_data.data
            
            # Save image
            filename = f"tile_{tile_id or int(time.time())}_{mood}_{style.replace(' ', '_')}_gemini.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            image_url = f"{self.output_dir}/{filename}"
            
            # Convert to base64
            base64_data = self._image_to_base64(filepath)
            
            tile = {
                "id": tile_id,
                "prompt": prompt,
                "mood": mood,
                "style": style,
                "image_url": image_url,
                "base64": base64_data,
                "image_size": len(image_bytes),
                "width": width,
                "height": height,
                "generated_at": time.time(),
                "provider": "gemini_img2img",
                "reference_image": reference_image_path
            }
            
            logger.info(f"✓ Gemini img2img success: {filepath} ({len(image_bytes)/1024:.1f} KB)")
            return tile
            
        except Exception as e:
            logger.error(f"Gemini img2img failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _image_to_base64(self, filepath: str) -> str:
        """Convert image file to base64 string with data URI prefix."""
        try:
            with open(filepath, 'rb') as f:
                image_bytes = f.read()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            # Add data URI prefix for direct HTML embedding
            return f"data:image/jpeg;base64,{base64_string}"
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {str(e)}")
            return ""
    
    def _parse_size(self, size_str: str) -> tuple:
        """Parse size string like '1024x1024' into (width, height)."""
        try:
            width, height = size_str.split("x")
            return int(width), int(height)
        except:
            return 1024, 1024


# Convenience functions
def generate_mood_board(
    product: str,
    audience: str,
    tone: str,
    domain: str = "",
    num_images: int = 4
) -> Dict[str, Any]:
    """
    Quick function to generate mood board.
    
    Args:
        product: Product/service name
        audience: Target audience
        tone: Campaign tone
        domain: Industry/domain
        num_images: Number of images to generate
    
    Returns:
        Mood board dict with images
    """
    agent = VisualAgent()
    
    strategy = {
        "product": product,
        "audience": audience,
        "tone": tone,
        "stylistics": domain
    }
    
    return agent.generate_mood_board(strategy, num_variations=num_images)


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("VISUAL AGENT - MOOD BOARD GENERATOR")
    print("=" * 80)
    
    # Test strategy
    test_strategy = {
        "product": "EcoBottle - Sustainable Water Bottle",
        "audience": "environmentally conscious college students",
        "tone": "friendly and inspiring",
        "stylistics": "sustainability and eco-friendly lifestyle"
    }
    
    agent = VisualAgent()
    
    print("\nGenerating mood board...")
    print(f"Product: {test_strategy['product']}")
    print(f"Audience: {test_strategy['audience']}")
    print(f"Tone: {test_strategy['tone']}")
    
    mood_board = agent.generate_mood_board(test_strategy, num_variations=4)
    
    print("\n" + "=" * 80)
    print("MOOD BOARD COMPLETE")
    print("=" * 80)
    print(f"Status: {mood_board['status']}")
    print(f"Theme: {mood_board.get('visual_theme', 'N/A')}")
    print(f"Colors: {', '.join(mood_board.get('color_palette', []))}")
    print(f"Tiles Generated: {mood_board['total_generated']}/{mood_board['requested']}")
    
    print("\nTiles:")
    for i, tile in enumerate(mood_board['tiles'], 1):
        print(f"\n  Tile {i}:")
        print(f"    Mood: {tile['mood']}")
        print(f"    Style: {tile['style']}")
        print(f"    Size: {tile['image_size']} bytes")
        print(f"    Prompt: {tile['prompt'][:80]}...")
    
    # Save images to files
    print("\nSaving images...")
    for i, tile in enumerate(mood_board['tiles'], 1):
        if tile.get('image_data'):
            filename = f"mood_board_tile_{i}.jpg"
            with open(filename, 'wb') as f:
                f.write(tile['image_data'])
            print(f"  ✓ Saved: {filename}")
    
    print("\n" + "=" * 80)