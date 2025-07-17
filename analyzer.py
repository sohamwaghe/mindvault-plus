from textblob import TextBlob

def auto_tag(content):
    # Simple placeholder tagging logic
    keywords = {
        "focus": ["focus", "study", "work"],
        "growth": ["learn", "improve", "skill"],
        "burnout": ["tired", "exhausted", "burnout"]
    }
    matched_tags = []
    for tag, words in keywords.items():
        if any(word in content.lower() for word in words):
            matched_tags.append(tag)
    return ", ".join(matched_tags) if matched_tags else "uncategorized"

def analyze_sentiment(content):
    blob = TextBlob(content)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

