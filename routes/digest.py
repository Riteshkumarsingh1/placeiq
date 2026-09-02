import feedparser
from flask import Blueprint, jsonify

digest_bp = Blueprint('digest', __name__)

@digest_bp.route('/news', methods=['GET'])
def get_placement_news():
    feeds = [
        'https://timesofindia.indiatimes.com/rssfeeds/5880659.cms',  # Education
        'https://economictimes.indiatimes.com/tech/technology/rssfeeds/5878127.cms'  # Tech news
    ]
    articles = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.summary[:200],
                    'published': entry.published
                })
        except:
            pass
    return jsonify(articles[:10])