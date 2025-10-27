"""Text processing module for analyzing text content"""
import re
from collections import Counter
import base64
import json

def process_text(text_files):
    """
    Process text files to extract statistics, sentiment analysis, and keyword extraction.
    Returns analysis results for each text file.
    """
    results = []
    for text_file in text_files:
        try:
            # Read text content
            content = text_file.stream.read().decode('utf-8')
            
            # Basic text analysis
            word_count = len(content.split())
            char_count = len(content)
            sentence_count = len(re.split(r'[.!?]+', content))
            
            # Extract most common words
            words = re.findall(r'\b\w+\b', content.lower())
            common_words = Counter(words).most_common(10)
            
            # Simple sentiment analysis (count positive/negative words)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting']
            
            pos_count = sum(1 for word in words if word in positive_words)
            neg_count = sum(1 for word in words if word in negative_words)
            sentiment_score = pos_count - neg_count
            
            analysis = {
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count,
                "common_words": common_words,
                "sentiment_score": sentiment_score,
                "positive_words": pos_count,
                "negative_words": neg_count
            }
            
            # Encode result as base64 JSON
            result_str = base64.b64encode(json.dumps(analysis).encode()).decode('utf-8')
            
            results.append({
                "filename": text_file.filename,
                "analysis_data": result_str
            })
        except Exception as e:
            print(f"Error processing text file {text_file.filename}: {e}")
    
    return results