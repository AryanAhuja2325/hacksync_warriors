"""
Test Visual Agent with Image-to-Image Generation
User provides a reference image, and the agent generates 4 mood board tiles based on it.
"""

import os
import sys
from agents.visualAgent import VisualAgent

def test_image_to_image_moodboard():
    """
    Test mood board generation with a user-provided reference image.
    """
    
    print("=" * 80)
    print("VISUAL AGENT - IMAGE-TO-IMAGE MOOD BOARD TEST")
    print("=" * 80)
    
    # Get reference image from user
    print("\nPlease provide the path to your reference image:")
    print(r"(Example: C:\Users\manis\Downloads\HackSync\hacksync_warriors\ml\ecobottle.webp)")
    
    reference_image = input("\nReference image path: ").strip()
    
    # Remove quotes if user pasted path with quotes
    reference_image = reference_image.strip('"').strip("'")
    
    # Validate file exists
    if not os.path.exists(reference_image):
        print(f"\n❌ Error: File not found: {reference_image}")
        return
    
    print(f"\n✓ Reference image loaded: {reference_image}")
    
    # Get campaign details from user
    print("\n" + "=" * 80)
    print("CAMPAIGN DETAILS")
    print("=" * 80)
    
    product = input("\nProduct/Service name (e.g., EcoBottle): ").strip() or "EcoBottle"
    audience = input("Target audience (e.g., college students): ").strip() or "environmentally conscious college students"
    tone = input("Campaign tone (e.g., friendly): ").strip() or "friendly and inspiring"
    domain = input("Industry/domain (e.g., sustainability): ").strip() or "sustainability and eco-friendly lifestyle"
    
    # Create strategy
    strategy = {
        "product": product,
        "audience": audience,
        "tone": tone,
        "stylistics": domain
    }
    
    print("\n" + "=" * 80)
    print("GENERATING MOOD BOARD WITH IMAGE-TO-IMAGE")
    print("=" * 80)
    print(f"\nProduct: {product}")
    print(f"Audience: {audience}")
    print(f"Tone: {tone}")
    print(f"Domain: {domain}")
    print(f"Reference Image: {reference_image}")
    print(f"\nGenerating 4 mood board tiles (1 will depict target audience)...")
    
    # Initialize agent
    agent = VisualAgent()
    
    # Generate mood board with reference image
    mood_board = agent.generate_mood_board(
        strategy=strategy,
        num_variations=4,
        reference_image_path=reference_image
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("MOOD BOARD GENERATED")
    print("=" * 80)
    
    print(f"\nStatus: {mood_board['status']}")
    print(f"Visual Theme: {mood_board.get('visual_theme', 'N/A')}")
    print(f"Color Palette: {', '.join(mood_board.get('color_palette', []))}")
    print(f"Tiles Generated: {mood_board['total_generated']}/{mood_board['requested']}")
    
    print("\n" + "=" * 80)
    print("GENERATED TILES")
    print("=" * 80)
    
    for i, tile in enumerate(mood_board['tiles'], 1):
        print(f"\nTile {i}:")
        print(f"  Type: {'👤 USER-DEPICTING' if tile.get('prompt', '').find('person') >= 0 or tile.get('prompt', '').find('woman') >= 0 or tile.get('prompt', '').find('man') >= 0 else '📦 PRODUCT'}")
        print(f"  Mood: {tile['mood']}")
        print(f"  Style: {tile['style']}")
        print(f"  Provider: {tile.get('provider', 'unknown')}")
        print(f"  Image: {tile.get('image_url', 'N/A')}")
        print(f"  Size: {tile.get('image_size', 0) / 1024:.1f} KB")
        print(f"  Prompt: {tile['prompt'][:100]}...")
    
    print("\n" + "=" * 80)
    print(f"✓ Images saved in: {agent.output_dir}/")
    print("=" * 80)
    
    # Create simple HTML preview
    create_html_preview(mood_board)


def create_html_preview(mood_board):
    """Create a simple HTML preview of the mood board."""
    
    product = mood_board.get('product', 'N/A')
    audience = mood_board.get('audience', 'N/A')
    tone = mood_board.get('tone', 'N/A')
    theme = mood_board.get('visual_theme', 'N/A')
    colors = ', '.join(mood_board.get('color_palette', []))
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mood Board - Image-to-Image Generation</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .info {{ background: #f9f9f9; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 30px; }}
        .tile {{ background: #fafafa; padding: 15px; border-radius: 8px; border: 2px solid #ddd; }}
        .tile img {{ width: 100%; height: auto; border-radius: 5px; }}
        .tile h3 {{ margin-top: 10px; color: #667eea; }}
        .tile .details {{ font-size: 0.9em; color: #666; margin-top: 10px; }}
        .user-depicting {{ border-color: #10b981; background: #f0fdf4; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
        .badge.user {{ background: #10b981; color: white; }}
        .badge.product {{ background: #667eea; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Mood Board - Image-to-Image Generation</h1>
        
        <div class="info">
            <strong>Product:</strong> {product}<br>
            <strong>Audience:</strong> {audience}<br>
            <strong>Tone:</strong> {tone}<br>
            <strong>Visual Theme:</strong> {theme}<br>
            <strong>Colors:</strong> {colors}
        </div>
        
        <div class="grid">
"""
    
    for i, tile in enumerate(mood_board['tiles'], 1):
        is_user_depicting = any(word in tile.get('prompt', '').lower() for word in ['person', 'woman', 'man', 'girl', 'boy', 'people'])
        tile_class = 'user-depicting' if is_user_depicting else ''
        badge_class = 'user' if is_user_depicting else 'product'
        badge_text = '👤 User Depicting' if is_user_depicting else '📦 Product Focus'
        
        html += f"""
            <div class="tile {tile_class}">
                <span class="badge {badge_class}">{badge_text}</span>
                <img src="../{tile.get('image_url', '')}" alt="Tile {i}">
                <h3>Tile {i}: {tile['mood'].title()}</h3>
                <div class="details">
                    <strong>Style:</strong> {tile['style']}<br>
                    <strong>Provider:</strong> {tile.get('provider', 'unknown')}<br>
                    <strong>Prompt:</strong> {tile['prompt'][:120]}...
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_path = "generated_images/mood_board_img2img_preview.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ HTML Preview: {html_path}")
    print("  Open this file in your browser to view the mood board\n")


if __name__ == "__main__":
    test_image_to_image_moodboard()
