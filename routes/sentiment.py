from dotenv import load_dotenv
load_dotenv()
from flask import Blueprint, jsonify
from groq import Groq
import os
import json

sentiment_bp = Blueprint('sentiment', __name__)

def get_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_sentiment(reviews, college_name):
    client = get_client()
    reviews_text = "\n".join([f"- {r}" for r in reviews[:15]])
    prompt = f"""Analyze these student reviews for {college_name} and return ONLY JSON.

Reviews:
{reviews_text}

Return exactly this JSON (no extra text):
{{
    "sentiment_score": 75,
    "vibe": "Good",
    "positive_points": ["point1", "point2"],
    "negative_points": ["point1"],
    "summary": "2 line summary",
    "placement_sentiment": "Positive",
    "recommend_pct": 78
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    raw = response.choices[0].message.content.strip()
    start = raw.find('{')
    end = raw.rfind('}') + 1
    return json.loads(raw[start:end])


@sentiment_bp.route('/<college_name>', methods=['GET'])
def get_sentiment(college_name):
    try:
        from routes.scraper import get_all_reviews
        reviews = get_all_reviews(college_name)
        
        if not reviews:
            print(f"No reviews found for {college_name}, using dummy")
            reviews = [
                "Placement is decent but could be better",
                "Faculty is very supportive and helpful",
                "Campus life is amazing with lots of activities",
                "Infrastructure needs improvement",
                "Good opportunities for internships",
                "Placements are average for CSE branch",
                "Overall a good college for engineering"
            ]
        
        result = analyze_sentiment(reviews, college_name)
        result['college'] = college_name
        result['reviews_analyzed'] = len(reviews)
        result['source'] = 'real' if reviews else 'dummy'
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500