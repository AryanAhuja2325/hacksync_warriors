"""
Strategy Parser - Unified Input Processing for Campaign Briefs
Handles both text and PDF inputs, extracts structured strategy with intelligent fallbacks.
"""

import os
import requests
from io import BytesIO
from pypdf import PdfReader
from mistralai import Mistral
from dotenv import load_dotenv
import json
import logging
from typing import Dict, Any, Optional, Union

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

EXTRACTION_PROMPT = """You are a marketing strategy extraction expert. Extract structured campaign information from the given text.

Extract these fields with STRICT CONCISENESS:
- product: ONLY product/brand name (max 3-5 words). Example: "EcoBottle" not "EcoBottle - A sustainable water bottle"
- audience: ONLY primary demographic label (max 3-5 words). Example: "Gen Z" not "Gen Z (18-24) hypebeasts who value exclusivity"
- goal: ONLY primary action verb + outcome (max 5-7 words). Example: "increase brand awareness" not full sentences
- tone: ONLY 1-2 tone adjectives. Example: "energetic, fun" not detailed descriptions
- platforms: ONLY platform names in list. Example: ["Instagram", "TikTok"] not descriptions
- domain: ONLY industry category (1-2 words). Example: "fashion" not "sustainable fashion retail"

CRITICAL RULES:
1. Keep ALL fields extremely concise - remove all explanations, parentheses, and extra details
2. Extract the CORE label/term only
3. If not mentioned, return null
4. NO verbose descriptions - only essential keywords

Examples:
✓ GOOD: "audience": "college students"
✗ BAD: "audience": "college students aged 18-24 who are interested in sustainability and eco-friendly products"

✓ GOOD: "product": "Swasya Jeans"
✗ BAD: "product": "Swasya - A sustainable jeans brand using recycled fabrics"

Return VALID JSON only:
{
  "product": "string or null",
  "audience": "string or null",
  "goal": "string or null",
  "tone": "string or null",
  "platforms": ["list"] or null,
  "domain": "string or null"
}"""

FALLBACK_PROMPT = """You are a marketing strategy advisor. Given partial campaign information, infer missing fields using marketing best practices.

Partial Strategy:
{partial_strategy}

Fill in ONLY the missing (null) fields with intelligent inferences based on:
- What's already known about the campaign
- Common marketing patterns for this type of product/audience
- Industry standards

For each inferred field, use high-probability assumptions.

Return VALID JSON with the COMPLETE strategy (keep existing fields, fill missing ones):
{
  "product": "string",
  "audience": "string",
  "goal": "string",
  "tone": "string",
  "platforms": ["list"],
  "domain": "string",
  "stylistics": "string"
}"""


class StrategyParser:
    """Parses campaign briefs from text or PDF into structured strategy JSON"""
    
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY not found in .env")
        
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model = "mistral-large-latest"
    
    def parse_strategy(
        self,
        input_data: Union[str, Dict[str, Any]],
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Main entry point - parse strategy from text or PDF.
        
        Args:
            input_data: Raw text string or {"pdf_url": "..."} dict
            input_type: "text" or "pdf"
        
        Returns:
            Structured strategy dict with confidence scores
        """
        logger.info(f"Parsing strategy from {input_type} input")
        
        # Step 1: Get text content
        if input_type == "pdf":
            if isinstance(input_data, dict):
                pdf_url = input_data.get("pdf_url")
            else:
                pdf_url = input_data
            text = self._extract_pdf_text(pdf_url)
        else:
            text = input_data if isinstance(input_data, str) else str(input_data)
        
        logger.info(f"Extracted text length: {len(text)} chars")
        
        # Step 2: Extract fields with LLM
        partial_strategy = self._extract_with_llm(text)
        
        # Step 2.5: Clean up verbose outputs
        partial_strategy = self._cleanup_verbose_fields(partial_strategy)
        
        # Step 3: Fill missing fields
        complete_strategy = self._fill_missing_fields(partial_strategy)
        
        # Step 4: Add metadata and confidence
        result = self._validate_and_score(complete_strategy, partial_strategy)
        
        logger.info(f"Strategy parsed successfully: {result['metadata']['fields_extracted']}/{result['metadata']['total_fields']} fields")
        
        return result
    
    def _extract_pdf_text(self, pdf_url: str) -> str:
        """Extract text from PDF URL"""
        try:
            logger.info(f"Downloading PDF from: {pdf_url[:50]}...")
            
            response = requests.get(pdf_url, timeout=30)
            if response.status_code != 200:
                raise ValueError(f"Failed to download PDF: HTTP {response.status_code}")
            
            reader = PdfReader(BytesIO(response.content))
            text_chunks = []
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
                logger.info(f"Extracted page {i+1}/{len(reader.pages)}")
            
            final_text = "\n".join(text_chunks).strip()
            
            if not final_text:
                raise ValueError("No extractable text found in PDF")
            
            logger.info(f"✓ PDF text extracted: {len(final_text)} characters")
            return final_text
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"PDF download failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"PDF parsing failed: {str(e)}")
    
    def _extract_with_llm(self, text: str) -> Dict[str, Any]:
        """Extract structured fields using LLM"""
        try:
            logger.info("Extracting fields with LLM...")
            
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Text to analyze:\n\n{text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            extracted = json.loads(content)
            
            logger.info(f"✓ LLM extraction complete: {extracted}")
            return extracted
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Raw content: {content}")
            # Return empty structure on parse failure
            return {
                "product": None,
                "audience": None,
                "goal": None,
                "tone": None,
                "platforms": None,
                "domain": None
            }
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return {}
    
    def _cleanup_verbose_fields(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up verbose LLM outputs to concise labels"""
        import re
        
        cleaned = {}
        
        for field, value in strategy.items():
            if value is None or isinstance(value, list):
                cleaned[field] = value
                continue
            
            if not isinstance(value, str):
                cleaned[field] = value
                continue
            
            # Remove content in parentheses
            value = re.sub(r'\([^)]*\)', '', value)
            
            # Remove explanatory phrases
            value = re.sub(r'\b(who|that|which|with)\b.*$', '', value, flags=re.IGNORECASE)
            value = re.sub(r'\b(including|such as|like)\b.*$', '', value, flags=re.IGNORECASE)
            
            # For audience: extract first demographic term only
            if field == "audience":
                # Look for age groups or demographic labels at start
                match = re.match(r'^([A-Za-z\s]+?)(?:\(|\,|and|who|\d)', value)
                if match:
                    value = match.group(1).strip()
                else:
                    # Take first 3-5 words max
                    words = value.split()[:4]
                    value = ' '.join(words)
            
            # For product: extract brand/product name only
            elif field == "product":
                # Remove common suffixes
                value = re.sub(r'\s*[-:]\s*.*$', '', value)
                words = value.split()[:3]
                value = ' '.join(words)
            
            # For goal: keep first clause only
            elif field == "goal":
                value = value.split(',')[0].split(';')[0]
                words = value.split()[:7]
                value = ' '.join(words)
            
            # Clean up whitespace
            value = ' '.join(value.split()).strip()
            
            cleaned[field] = value if value else None
        
        logger.info(f"Cleaned strategy: {cleaned}")
        return cleaned
    
    def _fill_missing_fields(self, partial_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing fields using LLM-based inference"""
        # Check if any fields are missing
        missing_fields = [k for k, v in partial_strategy.items() if v is None]
        
        if not missing_fields:
            logger.info("All fields extracted, no fallback needed")
            # Add stylistics based on tone and domain if available
            stylistics = self._generate_stylistics(partial_strategy)
            return {**partial_strategy, "stylistics": stylistics}
        
        logger.info(f"Missing fields: {missing_fields}. Using LLM fallback...")
        
        try:
            prompt = FALLBACK_PROMPT.format(
                partial_strategy=json.dumps(partial_strategy, indent=2)
            )
            
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a marketing strategy expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            complete_strategy = json.loads(content)
            
            logger.info(f"✓ Fallback complete: {complete_strategy}")
            return complete_strategy
            
        except Exception as e:
            logger.error(f"Fallback failed: {str(e)}")
            # Use basic defaults
            return self._apply_basic_defaults(partial_strategy)
    
    def _apply_basic_defaults(self, partial_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rule-based defaults for missing fields"""
        defaults = {
            "product": partial_strategy.get("product") or "Product",
            "audience": partial_strategy.get("audience") or "general audience",
            "goal": partial_strategy.get("goal") or "increase brand awareness",
            "tone": partial_strategy.get("tone") or "professional",
            "platforms": partial_strategy.get("platforms") or ["Instagram", "Facebook"],
            "domain": partial_strategy.get("domain") or "general",
            "stylistics": partial_strategy.get("stylistics") or "modern and engaging"
        }
        
        logger.info(f"Applied basic defaults: {defaults}")
        return defaults
    
    def _generate_stylistics(self, strategy: Dict[str, Any]) -> str:
        """Generate stylistics field based on tone and domain"""
        tone = strategy.get("tone", "professional")
        domain = strategy.get("domain", "general")
        
        # Simple rule-based stylistics
        if "friendly" in tone.lower() or "casual" in tone.lower():
            return f"approachable and {domain}-focused"
        elif "professional" in tone.lower():
            return f"polished and {domain}-oriented"
        else:
            return f"engaging {domain} content"
    
    def _validate_and_score(
        self,
        complete_strategy: Dict[str, Any],
        partial_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add validation and confidence scoring"""
        
        # Count extracted vs inferred fields
        extracted_fields = sum(1 for v in partial_strategy.values() if v is not None)
        total_fields = len(partial_strategy)
        
        # Calculate confidence
        extraction_ratio = extracted_fields / total_fields if total_fields > 0 else 0
        
        if extraction_ratio >= 0.8:
            confidence = "high"
        elif extraction_ratio >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Build result
        result = {
            "strategy": complete_strategy,
            "metadata": {
                "fields_extracted": extracted_fields,
                "total_fields": total_fields,
                "confidence": confidence,
                "extraction_ratio": round(extraction_ratio, 2),
                "inferred_fields": [
                    k for k, v in partial_strategy.items()
                    if v is None and k in complete_strategy
                ]
            }
        }
        
        return result


# Convenience function
def parse_strategy_from_text(text: str) -> Dict[str, Any]:
    """Quick function to parse strategy from text"""
    parser = StrategyParser()
    return parser.parse_strategy(text, input_type="text")


def parse_strategy_from_pdf(pdf_url: str) -> Dict[str, Any]:
    """Quick function to parse strategy from PDF URL"""
    parser = StrategyParser()
    return parser.parse_strategy(pdf_url, input_type="pdf")
