"""
Test content-aware outreach generation with YouTube content analysis.
Demonstrates the full pipeline: fetch → normalize → summarize → personalize outreach
"""

from agents.content_fetchers import fetch_youtube_content
from agents.content_normalizer import normalize_content_list
from agents.content_summarizer import summarize_content
from agents.outreach import generate_outreach_for_influencer

# Test with a real YouTube channel
# Example: Using a tech/lifestyle channel (replace with actual channel)
test_channel_url = "https://www.youtube.com/@mkbhd"  # Example: MKBHD

print("=" * 80)
print("CONTENT-AWARE OUTREACH GENERATION TEST")
print("=" * 80)

print("\n1. FETCHING YOUTUBE CONTENT...")
print("-" * 80)
try:
    raw_content = fetch_youtube_content(
        channel_url=test_channel_url,
        max_videos=5
    )
    print(f"✓ Fetched {len(raw_content)} videos")
    
    for i, video in enumerate(raw_content[:3], 1):
        print(f"\n  Video {i}: {video.get('title', 'N/A')}")
        has_transcript = "✓" if video.get('transcript') else "✗"
        print(f"  Transcript: {has_transcript}")
        print(f"  Published: {video.get('published_date', 'N/A')}")

except Exception as e:
    print(f"✗ Error fetching content: {str(e)}")
    print("\nNote: Update test_channel_url to a valid YouTube channel URL")
    exit(1)

print("\n\n2. NORMALIZING CONTENT...")
print("-" * 80)
normalized_content = normalize_content_list(raw_content, "YouTube")
print(f"✓ Normalized {len(normalized_content)} items")
print(f"  Fields: title, description, transcript, full_text, tags, published_date")

print("\n\n3. SUMMARIZING CREATOR THEMES...")
print("-" * 80)
content_summary = summarize_content(normalized_content)
print("✓ Content analysis complete\n")
print(f"Main Topics: {', '.join(content_summary.get('main_topics', []))}")
print(f"Content Style: {content_summary.get('content_style', 'N/A')}")
print(f"Tone: {content_summary.get('tone', 'N/A')}")
print(f"Recent Themes: {', '.join(content_summary.get('recent_themes', [])[:3])}")
if content_summary.get('hook_examples'):
    print(f"Hook Example: {content_summary['hook_examples'][0]}")

print("\n\n4. GENERATING CONTENT-AWARE OUTREACH...")
print("-" * 80)

# Create mock influencer data
influencer_data = {
    "name": "Tech Reviewer",  # Adjust based on actual channel
    "platform": "YouTube",
    "url": test_channel_url,
    "niche": "technology reviews and insights"
}

# Generate outreach WITH content summary
outreach_with_content = generate_outreach_for_influencer(
    influencer=influencer_data,
    brand_name="TechGear Pro",
    product_domain="tech accessories",
    target_audience="tech enthusiasts",
    message_type="casual_dm",
    content_summary=content_summary  # This makes it content-aware!
)

print("\n📧 CONTENT-AWARE MESSAGE:")
print(outreach_with_content['message'])

print("\n\n5. COMPARISON: WITHOUT CONTENT ANALYSIS")
print("-" * 80)

# Generate outreach WITHOUT content summary (basic)
outreach_without_content = generate_outreach_for_influencer(
    influencer=influencer_data,
    brand_name="TechGear Pro",
    product_domain="tech accessories",
    target_audience="tech enthusiasts",
    message_type="casual_dm"
    # No content_summary provided
)

print("\n📧 BASIC MESSAGE (without content analysis):")
print(outreach_without_content['message'])

print("\n\n6. FORMAL EMAIL WITH CONTENT AWARENESS")
print("-" * 80)

email = generate_outreach_for_influencer(
    influencer=influencer_data,
    brand_name="TechGear Pro",
    product_domain="tech accessories",
    target_audience="tech enthusiasts",
    message_type="formal_email",
    collaboration_idea="Product review series featuring our new wireless charging line",
    content_summary=content_summary
)

print(f"\nSubject: {email['subject']}\n")
print(f"Body:\n{email['message']}")

print("\n" + "=" * 80)
print("✓ CONTENT-AWARE OUTREACH TEST COMPLETE!")
print("=" * 80)
print("\nKey Difference:")
print("- WITH content analysis: References actual videos, topics, style")
print("- WITHOUT content analysis: Generic niche-based outreach")
print("\nThis is what makes outreach feel authentic and researched!")
