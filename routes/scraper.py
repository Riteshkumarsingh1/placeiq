import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_shiksha(college_name: str) -> list:
    reviews = []
    try:
        # Search page use karo
        search_url = f"https://www.shiksha.com/search?q={college_name.replace(' ', '+')}&searchType=college"
        res = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # College link dhundo
        college_link = soup.find('a', href=re.compile(r'/college/.*reviews'))
        if not college_link:
            college_link = soup.find('a', href=re.compile(r'/college/'))
        
        if college_link:
            review_url = 'https://www.shiksha.com' + college_link['href']
            if 'reviews' not in review_url:
                review_url = review_url.rstrip('/') + '/reviews'
            
            rev_res = requests.get(review_url, headers=HEADERS, timeout=10)
            rev_soup = BeautifulSoup(rev_res.text, 'html.parser')
            
            # Multiple selectors try karo
            selectors = [
                {'class': re.compile(r'review-text|reviewText|review_text', re.I)},
                {'class': re.compile(r'review-content|reviewContent', re.I)},
                {'itemprop': 'reviewBody'},
            ]
            
            for sel in selectors:
                divs = rev_soup.find_all(['div', 'p', 'span'], sel)
                for d in divs[:8]:
                    text = d.get_text(strip=True)
                    if len(text) > 40:
                        reviews.append(text[:300])
                if reviews:
                    break
                    
    except Exception as e:
        print(f"Shiksha error: {e}")
    
    print(f"Shiksha reviews: {len(reviews)}")
    return reviews


def scrape_collegedunia(college_name: str) -> list:
    reviews = []
    try:
        search_url = f"https://collegedunia.com/search?s={college_name.replace(' ', '+')}"
        res = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        college_link = soup.find('a', href=re.compile(r'/college/.*review'))
        if not college_link:
            college_link = soup.find('a', href=re.compile(r'/college/\d+'))
        
        if college_link:
            review_url = 'https://collegedunia.com' + college_link['href']
            if 'review' not in review_url:
                review_url = review_url.rstrip('/') + '/reviews'
            
            rev_res = requests.get(review_url, headers=HEADERS, timeout=10)
            rev_soup = BeautifulSoup(rev_res.text, 'html.parser')
            
            selectors = [
                {'class': re.compile(r'review|Review', re.I)},
                {'class': re.compile(r'comment|Comment', re.I)},
                {'itemprop': 'reviewBody'},
            ]
            
            for sel in selectors:
                divs = rev_soup.find_all(['div', 'p'], sel)
                for d in divs[:8]:
                    text = d.get_text(strip=True)
                    if len(text) > 40:
                        reviews.append(text[:300])
                if reviews:
                    break
                    
    except Exception as e:
        print(f"Collegedunia error: {e}")
    
    print(f"Collegedunia reviews: {len(reviews)}")
    return reviews


def get_all_reviews(college_name: str) -> list:
    """Groq se college-specific realistic reviews generate karo"""
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()
    import os, json
    
    print(f"Generating reviews for: {college_name}")
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = f"""Generate 10 realistic student reviews for {college_name} in India.
These should be based on the college's actual reputation and characteristics.
Return ONLY a JSON array of strings, no extra text:
["review1", "review2", ...]
Each review should be 1-2 sentences, mix of positive and negative."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    
    raw = response.choices[0].message.content.strip()
    start = raw.find('[')
    end = raw.rfind(']') + 1
    reviews = json.loads(raw[start:end])
    print(f"Generated {len(reviews)} reviews")
    return reviews