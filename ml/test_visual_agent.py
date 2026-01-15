"""
Visual Agent Test with Swasya Strategy
Tests mood board generation and saves images only (no HTML)
"""

import os
import base64
from agents.visualAgent import VisualAgent
import json

def save_images_from_mood_board(mood_board, output_dir="mood_board_images"):
    """Save images from mood board as PNG files"""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'=' * 80}")
    print("SAVING IMAGES")
    print(f"{'=' * 80}")
    
    saved_files = []
    
    for i, tile in enumerate(mood_board.get('tiles', []), 1):
        if tile.get('base64'):
            # Decode base64 to binary
            try:
                # Remove data URI prefix if present
                base64_str = tile['base64']
                if ',' in base64_str:
                    base64_str = base64_str.split(',', 1)[1]
                
                image_data = base64.b64decode(base64_str)
                
                # Create filename
                mood = tile['mood'].replace(' ', '_')
                style = tile['style'].replace(' ', '_')
                filename = f"tile_{i}_{mood}_{style}.png"
                filepath = os.path.join(output_dir, filename)
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                size_kb = len(image_data) / 1024
                print(f"\n✓ Saved: {filename} ({size_kb:.1f} KB)")
                print(f"  Mood: {tile['mood']}")
                print(f"  Style: {tile['style']}")
                print(f"  Prompt: {tile['prompt'][:80]}...")
                
                saved_files.append(filepath)
                
            except Exception as e:
                print(f"\n✗ Failed to save tile {i}: {str(e)}")
        else:
            print(f"\n✗ Tile {i} has no image data")
    
    return saved_files

def test_visual_agent_with_strategy():
    """Test visual agent with the Swasya strategy from parser"""
    
    # Strategy from parser output
    strategy = {
        "product": "Swasya",
        "audience": "college students",
        "goal": "promote brand awareness",
        "tone": "energetic, fun",
        "platforms": ["Instagram", "Facebook"],
        "domain": "fashion",
        "stylistics": "modern and engaging"
    }
    
    print("=" * 80)
    print("TESTING VISUAL AGENT WITH SWASYA STRATEGY")
    print("=" * 80)
    print("\nInput Strategy:")
    print(json.dumps(strategy, indent=2))
    print("\n" + "-" * 80)
    
    try:
        # Initialize visual agent
        print("\n[1/4] Initializing Visual Agent...")
        agent = VisualAgent()
        print("✓ Visual Agent initialized")
        
        # Generate mood board
        print("\n[2/4] Generating mood board (4 image variations)...")
        print("⏳ This may take 30-60 seconds (generating images via Gemini API)...")
        print()
        
        mood_board = agent.generate_mood_board(
            strategy=strategy,
            num_variations=4,
            image_size="1024x1024"
        )
        
        # Display results
        print("\n[3/4] GENERATION RESULTS:")
        print("=" * 80)
        print(f"Status: {mood_board['status']}")
        print(f"Product: {mood_board.get('product', strategy.get('product', 'N/A'))}")
        print(f"Images Generated: {len(mood_board['tiles'])}")
        
        if mood_board.get('visual_theme'):
            print(f"Visual Theme: {mood_board['visual_theme']}")
        
        if mood_board.get('color_palette'):
            print(f"Color Palette: {', '.join(mood_board['color_palette'])}")
        
        print("\nGenerated Tiles:")
        print("-" * 80)
        
        for i, tile in enumerate(mood_board['tiles'], 1):
            print(f"\n  [{i}] Tile {tile.get('id', i)}:")
            print(f"      Mood: {tile['mood']}")
            print(f"      Style: {tile['style']}")
            print(f"      Prompt: {tile['prompt'][:100]}...")
            
            if tile.get('base64'):
                print(f"      Image: ✓ Base64 encoded ({len(tile['base64'])} chars)")
            else:
                print(f"      Image: ✗ Not generated")
        
        # Save images
        print(f"\n[4/4] Saving Images...")
        saved_files = save_images_from_mood_board(mood_board)
        
        print(f"\n✓ Saved {len(saved_files)} images to mood_board_images/")
        
        # Show JSON output file
        if mood_board.get('metadata', {}).get('output_file'):
            print(f"✓ Mood board JSON saved to: {mood_board['metadata']['output_file']}")
        
        print("\n" + "=" * 80)
        print("✓ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_visual_agent_with_strategy()
