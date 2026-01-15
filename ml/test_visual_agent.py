"""
Visual Agent Test with HTML Mood Board Preview
"""

import os
from agents.visualAgent import generate_mood_board
from datetime import datetime

def create_mood_board_preview(mood_board: dict, output_dir: str = "mood_board_output"):
    """
    Create mood board with images and HTML preview.
    
    Args:
        mood_board: Mood board dict from visual agent
        output_dir: Directory to save outputs
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'=' * 80}")
    print("SAVING MOOD BOARD")
    print(f"{'=' * 80}")
    
    # Save images with descriptive names
    image_files = []
    for i, tile in enumerate(mood_board.get('tiles', []), 1):
        if tile.get('image_data'):
            # Create descriptive filename
            mood = tile['mood'].replace(' ', '_')
            style = tile['style'].replace(' ', '_')
            filename = f"tile_{i}_{mood}_{style}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(tile['image_data'])
            
            size_kb = tile['image_size'] / 1024
            print(f"✓ Saved: {filename} ({size_kb:.1f} KB)")
            print(f"  Mood: {tile['mood']} | Style: {tile['style']}")
            print(f"  Prompt: {tile['prompt'][:80]}...")
            
            image_files.append({
                'filename': filename,
                'mood': tile['mood'],
                'style': tile['style'],
                'prompt': tile['prompt'],
                'size': size_kb
            })
        else:
            print(f"✗ Tile {i} has no image data")
    
    # Create HTML preview
    html_file = os.path.join(output_dir, "mood_board_preview.html")
    create_html_preview(mood_board, image_files, html_file)
    
    print(f"\n✓ HTML Preview: {html_file}")
    print(f"  Open this file in your browser to view the mood board")
    
    return output_dir


def create_html_preview(mood_board: dict, image_files: list, output_file: str):
    """Generate HTML preview of mood board."""
    
    product = mood_board.get('product', 'Unknown Product')
    audience = mood_board.get('audience', 'Unknown Audience')
    tone = mood_board.get('tone', 'Unknown Tone')
    theme = mood_board.get('visual_theme', 'N/A')
    colors = ', '.join(mood_board.get('color_palette', []))
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mood Board - {product}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .strategy-info {{
            background: #f8f9fa;
            padding: 30px 40px;
            border-bottom: 3px solid #e9ecef;
        }}
        
        .strategy-info h2 {{
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .info-item strong {{
            display: block;
            color: #667eea;
            margin-bottom: 5px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .info-item span {{
            color: #495057;
            font-size: 1.1em;
        }}
        
        .mood-board {{
            padding: 40px;
        }}
        
        .mood-board h2 {{
            color: #495057;
            margin-bottom: 30px;
            font-size: 1.8em;
            text-align: center;
        }}
        
        .tiles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }}
        
        .tile {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .tile:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }}
        
        .tile img {{
            width: 100%;
            height: 400px;
            object-fit: cover;
            display: block;
        }}
        
        .tile-info {{
            padding: 20px;
            background: #f8f9fa;
        }}
        
        .tile-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 12px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-mood {{
            background: #e7f3ff;
            color: #0066cc;
        }}
        
        .badge-style {{
            background: #fff3e7;
            color: #cc6600;
        }}
        
        .tile-prompt {{
            color: #6c757d;
            font-size: 0.9em;
            line-height: 1.5;
            font-style: italic;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            border-top: 3px solid #e9ecef;
        }}
        
        .timestamp {{
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Mood Board</h1>
            <p>AI-Generated Visual Campaign</p>
        </div>
        
        <div class="strategy-info">
            <h2>Campaign Strategy</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Product</strong>
                    <span>{product}</span>
                </div>
                <div class="info-item">
                    <strong>Target Audience</strong>
                    <span>{audience}</span>
                </div>
                <div class="info-item">
                    <strong>Tone</strong>
                    <span>{tone}</span>
                </div>
                <div class="info-item">
                    <strong>Visual Theme</strong>
                    <span>{theme}</span>
                </div>
                <div class="info-item">
                    <strong>Color Palette</strong>
                    <span>{colors}</span>
                </div>
                <div class="info-item">
                    <strong>Tiles Generated</strong>
                    <span>{len(image_files)} images</span>
                </div>
            </div>
        </div>
        
        <div class="mood-board">
            <h2>Visual Mood Board</h2>
            <div class="tiles-grid">
"""
    
    # Add each tile
    for i, img_data in enumerate(image_files, 1):
        html += f"""
                <div class="tile">
                    <img src="{img_data['filename']}" alt="Mood Board Tile {i}">
                    <div class="tile-info">
                        <div class="tile-meta">
                            <span class="badge badge-mood">{img_data['mood']}</span>
                            <span class="badge badge-style">{img_data['style']}</span>
                        </div>
                        <div class="tile-prompt">
                            "{img_data['prompt']}"
                        </div>
                    </div>
                </div>
"""
    
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html += f"""
            </div>
        </div>
        
        <div class="footer">
            <p class="timestamp">Generated on {timestamp}</p>
            <p>Powered by Pollinations AI + Mistral AI</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)


# Main test
if __name__ == "__main__":
    print("=" * 80)
    print("VISUAL AGENT TEST - MOOD BOARD GENERATOR")
    print("=" * 80)
    
    # Test campaign 1: EcoBottle
    print("\n🧪 Test 1: Eco-Friendly Product")
    print("-" * 80)
    
    mood_board = generate_mood_board(
        product="EcoBottle - Sustainable Water Bottle",
        audience="environmentally conscious college students in India",
        tone="friendly and inspiring",
        domain="sustainability and eco-friendly lifestyle",
        num_images=4
    )
    
    if mood_board.get('status') == 'success':
        output_dir = create_mood_board_preview(mood_board, "mood_board_output")
        
        print(f"\n{'=' * 80}")
        print("✓ MOOD BOARD GENERATED SUCCESSFULLY!")
        print(f"{'=' * 80}")
        print(f"\nOutput Directory: {output_dir}")
        print(f"  - {mood_board['total_generated']} images saved")
        print(f"  - HTML preview created")
        print(f"\nNext Steps:")
        print(f"  1. Check the images in '{output_dir}' folder")
        print(f"  2. Open '{output_dir}/mood_board_preview.html' in your browser")
        print(f"  3. Review the visual consistency and theme alignment")
    else:
        print("\n✗ Mood board generation failed")
        print(f"Status: {mood_board.get('status')}")
    
    print("\n" + "=" * 80)
