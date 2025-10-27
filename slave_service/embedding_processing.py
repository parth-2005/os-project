"""Embedding generation module for creating vector representations"""
import base64
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def process_embeddings(text_files):
    """
    Generate TF-IDF embeddings for text files.
    Returns vector embeddings for each text file.
    """
    results = []
    texts = []
    filenames = []
    
    # Read all text files
    for text_file in text_files:
        try:
            content = text_file.stream.read().decode('utf-8')
            texts.append(content)
            filenames.append(text_file.filename)
        except Exception as e:
            print(f"Error reading text file {text_file.filename}: {e}")
            continue
    
    if not texts:
        return results
    
    try:
        # Generate TF-IDF vectors
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        
        for i, filename in enumerate(filenames):
            # Get vector for this document
            doc_vector = tfidf_matrix[i].toarray()[0]
            
            # Create embedding data
            embedding_data = {
                "vector": doc_vector.tolist(),
                "features": feature_names.tolist(),
                "vector_size": len(doc_vector),
                "non_zero_features": int(np.count_nonzero(doc_vector))
            }
            
            # Encode as base64 JSON
            result_str = base64.b64encode(json.dumps(embedding_data).encode()).decode('utf-8')
            
            results.append({
                "filename": filename,
                "embedding_data": result_str
            })
    except Exception as e:
        print(f"Error generating embeddings: {e}")
    
    return results