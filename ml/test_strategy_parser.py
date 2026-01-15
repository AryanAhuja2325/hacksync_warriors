"""Test Strategy Parser"""
from agents.strategyParser import StrategyParser
import json

# Test 1: Text input
text_input = "We are Swasya, a sustainable jeans brand. We use scrapped and old fabrics to make new jeans. We want to promote our brand to college kids and make them aware of our motto. We want the campaign to be energetic and fun."

print("=" * 80)
print("TEST 1: TEXT INPUT")
print("=" * 80)
print(f"\nInput:\n{text_input}\n")

parser = StrategyParser()
result1 = parser.parse_strategy(text_input, input_type="text")

print("RESULT:")
print(json.dumps(result1, indent=2))

# Test 2: PDF input
pdf_url = "https://drive.google.com/uc?export=download&id=1kKRDNmnfnXaIlj56iwpPV1DEi_bKKbN0"

print("\n" + "=" * 80)
print("TEST 2: PDF INPUT")
print("=" * 80)
print(f"\nPDF URL: {pdf_url}\n")

try:
    result2 = parser.parse_strategy(pdf_url, input_type="pdf")
    print("RESULT:")
    print(json.dumps(result2, indent=2))
except Exception as e:
    print(f"Error: {e}")
