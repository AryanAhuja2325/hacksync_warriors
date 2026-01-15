import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json
import re
import time

load_dotenv()

SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")


class InfluencerScraper:
    """Scrape influencer data from public directory sites using ScrapingBee API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or SCRAPINGBEE_API_KEY
        if not self.api_key:
            raise ValueError("ScrapingBee API key not found. Set SCRAPINGBEE_API_KEY in .env")
        
        self.base_url = "https://app.scrapingbee.com/api/v1/"
    
    def _scrape_with_bee(self, url: str, render_js: bool = True, wait: int = 5000) -> str:
        """Make request using ScrapingBee API"""
        params = {
            'api_key': self.api_key,
            'url': url,
            'render_js': 'true' if render_js else 'false',
            'premium_proxy': 'true',
            'country_code': 'us',
            'wait': str(wait)  # Wait for JS to render
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"ScrapingBee error: {response.status_code} - {response.text}")
    
    def scrape_social_blade(self, platform: str = "instagram", limit: int = 50) -> List[Dict]:
        """
        Scrape top influencers from Social Blade
        
        Social Blade has simpler HTML structure, easier to parse
        """
        url = f"https://socialblade.com/instagram/top/50/followers"
        
        try:
            print(f"Scraping Social Blade ({platform})...")
            html = self._scrape_with_bee(url, render_js=False)  # Social Blade doesn't need JS rendering
            soup = BeautifulSoup(html, 'html.parser')
            
            influencers = []
            
            # Social Blade uses a table with id="socialblade-user-content"
            table = soup.find('div', {'id': 'socialblade-user-content'})
            
            if table:
                # Find all ranking divs
                rank_divs = table.find_all('div', style=re.compile('padding'))
                
                for div in rank_divs[:limit]:
                    try:
                        # Extract username
                        link = div.find('a')
                        if link:
                            username = link.get_text(strip=True)
                            
                            influencer = {
                                'name': username,
                                'platform': platform,
                                'followers': None,
                                'engagement': None,
                                'category': 'general',
                                'source': 'socialblade',
                                'url': f"https://socialblade.com{link['href']}" if link.get('href') else None
                            }
                            influencers.append(influencer)
                    except Exception as e:
                        print(f"Error parsing Social Blade entry: {e}")
                        continue
            else:
                print("⚠️  Could not find Social Blade table")
            
            print(f"   Found {len(influencers)} from Social Blade")
            return influencers
            
        except Exception as e:
            print(f"❌ Error scraping Social Blade: {e}")
            return []
    
    def scrape_influencer_marketing_hub(self, platform: str = "instagram", limit: int = 50) -> List[Dict]:
        """
        Scrape Influencer Marketing Hub - they have public top lists
        This site has simpler HTML structure
        """
        platform_map = {
            'instagram': 'instagram',
            'youtube': 'youtube',
            'tiktok': 'tiktok'
        }
        
        platform_slug = platform_map.get(platform.lower(), 'instagram')
        url = f"https://influencermarketinghub.com/top-{platform_slug}-influencers/"
        
        try:
            print(f"Scraping Influencer Marketing Hub ({platform})...")
            html = self._scrape_with_bee(url, render_js=True, wait=5000)
            soup = BeautifulSoup(html, 'html.parser')
            
            influencers = []
            
            # Look for article or list items
            items = soup.find_all(['article', 'div', 'li'], class_=re.compile(r'influencer|creator|profile', re.I))
            
            for item in items[:limit]:
                try:
                    name_elem = item.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'name|title|heading', re.I))
                    
                    if name_elem:
                        influencer = {
                            'name': name_elem.get_text(strip=True),
                            'platform': platform,
                            'followers': None,
                            'engagement': None,
                            'category': 'general',
                            'source': 'influencermarketinghub'
                        }
                        influencers.append(influencer)
                except:
                    continue
            
            print(f"   Found {len(influencers)} from Influencer Marketing Hub")
            return influencers
            
        except Exception as e:
            print(f"❌ Error scraping Influencer Marketing Hub: {e}")
            return []
    
    def scrape_all_sources(self, platform: str = "instagram", category: str = "all", limit: int = 20) -> List[Dict]:
        """
        Scrape from all available sources and combine results
        
        Focus on simpler sites that don't require complex JS parsing
        """
        all_influencers = []
        
        # Try Social Blade (simplest, most reliable)
        try:
            print("\n📊 Source 1/2: Social Blade")
            social_blade_data = self.scrape_social_blade(platform, limit)
            all_influencers.extend(social_blade_data)
            time.sleep(2)
        except Exception as e:
            print(f"❌ Social Blade failed: {e}")
        
        # Try Influencer Marketing Hub
        try:
            print("\n📊 Source 2/2: Influencer Marketing Hub")
            imh_data = self.scrape_influencer_marketing_hub(platform, limit)
            all_influencers.extend(imh_data)
            time.sleep(2)
        except Exception as e:
            print(f"❌ Influencer Marketing Hub failed: {e}")
        
        # Remove duplicates based on name
        unique_influencers = []
        seen_names = set()
        
        for inf in all_influencers:
            name_lower = inf['name'].lower()
            if name_lower not in seen_names:
                unique_influencers.append(inf)
                seen_names.add(name_lower)
        
        print(f"\n✅ Total unique influencers: {len(unique_influencers)}")
        return unique_influencers
    
    def _parse_number(self, text: str) -> Optional[int]:
        """Parse follower count from text (handles K, M, B suffixes)"""
        try:
            text = text.strip().upper().replace(',', '')
            
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            elif 'B' in text:
                return int(float(text.replace('B', '')) * 1000000000)
            else:
                # Extract just the digits
                return int(''.join(filter(str.isdigit, text)))
        except:
            return None


def scrape_influencers(platform: str = "instagram", category: str = "all", limit: int = 20) -> List[Dict]:
    """
    Main function to scrape influencer data
    
    Args:
        platform: Platform to scrape (instagram, youtube, tiktok)
        category: Category/niche (fashion, beauty, fitness, tech, etc.)
        limit: Number of influencers per source
    
    Returns:
        List of influencer dictionaries with name, followers, engagement, category
    """
    scraper = InfluencerScraper()
    return scraper.scrape_all_sources(platform, category, limit)
