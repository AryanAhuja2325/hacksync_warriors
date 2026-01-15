"""
Test script for outreach message generation.
Run this from the ml/ directory: python test_outreach.py
"""

from agents.outreach import generate_outreach_for_influencer, generate_bulk_outreach_messages

# Example influencer data (as you'd get from market.py)
sample_influencer = {
    "name": "Priya Sharma",
    "platform": "Instagram",
    "url": "https://instagram.com/priyafashion",
    "niche": "women's fashion and styling",
    "snippet": "Fashion influencer sharing daily outfit inspirations and styling tips for young women"
}

print("=" * 60)
print("TESTING OUTREACH MESSAGE GENERATION")
print("=" * 60)

# Test 1: Casual DM
print("\n1. CASUAL INSTAGRAM DM")
print("-" * 60)
dm = generate_outreach_for_influencer(
    influencer=sample_influencer,
    brand_name="StyleHub",
    product_domain="women's fashion",
    target_audience="young women aged 18-30",
    message_type="casual_dm"
)
print(f"Platform: {dm['platform']}")
print(f"Type: {dm['message_type']}")
print(f"\nMessage:\n{dm['message']}")

# Test 2: Initial Contact
print("\n\n2. INITIAL CONTACT MESSAGE")
print("-" * 60)
initial = generate_outreach_for_influencer(
    influencer=sample_influencer,
    brand_name="StyleHub",
    product_domain="women's fashion",
    target_audience="young women aged 18-30",
    message_type="initial_contact"
)
print(f"Message:\n{initial['message']}")

# Test 3: Formal Email
print("\n\n3. FORMAL EMAIL")
print("-" * 60)
email = generate_outreach_for_influencer(
    influencer=sample_influencer,
    brand_name="StyleHub",
    product_domain="women's fashion",
    target_audience="young women aged 18-30",
    message_type="formal_email",
    collaboration_idea="Instagram Reels series featuring our new collection"
)
print(f"Subject: {email['subject']}\n")
print(f"Body:\n{email['message']}")

# Test 4: Partnership Proposal
print("\n\n4. PARTNERSHIP PROPOSAL")
print("-" * 60)
proposal = generate_outreach_for_influencer(
    influencer=sample_influencer,
    brand_name="StyleHub",
    product_domain="women's fashion",
    target_audience="young women aged 18-30",
    message_type="partnership_proposal",
    collaboration_idea="Long-term brand ambassador program with monthly content creation"
)
print(f"Message:\n{proposal['message']}")

# Test 5: Follow-up
print("\n\n5. FOLLOW-UP MESSAGE")
print("-" * 60)
followup = generate_outreach_for_influencer(
    influencer=sample_influencer,
    brand_name="StyleHub",
    product_domain="women's fashion",
    target_audience="young women aged 18-30",
    message_type="follow_up"
)
print(f"Message:\n{followup['message']}")

# Test 6: Bulk generation with multiple influencers
print("\n\n6. BULK OUTREACH GENERATION (3 influencers)")
print("-" * 60)
influencers = [
    {
        "name": "Ananya Verma",
        "platform": "Instagram",
        "url": "https://instagram.com/ananyastyle",
        "niche": "fashion and lifestyle",
        "snippet": "Fashion blogger and stylist"
    },
    {
        "name": "Riya Kapoor",
        "platform": "YouTube",
        "url": "https://youtube.com/@riyakapoor",
        "niche": "fashion hauls and reviews",
        "snippet": "YouTube creator sharing fashion hauls and honest reviews"
    },
    {
        "name": "Meera Singh",
        "platform": "Instagram",
        "url": "https://instagram.com/meerafashion",
        "niche": "sustainable fashion",
        "snippet": "Promoting eco-friendly and sustainable fashion choices"
    }
]

bulk_results = generate_bulk_outreach_messages(
    influencers=influencers,
    brand_name="StyleHub",
    product_domain="women's fashion",
    target_audience="young women aged 18-30",
    message_type="casual_dm"
)

for i, result in enumerate(bulk_results, 1):
    print(f"\nInfluencer {i}: {result['influencer']['name']} ({result['influencer']['platform']})")
    print(f"Message: {result['outreach']['message']}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
