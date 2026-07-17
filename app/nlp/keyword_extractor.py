import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

class KeywordExtractor:
    """Extracts relevant terms, frequencies, and ngrams from document texts."""
    def __init__(self):
        pass

    def extract_keywords_tfidf(self, text, top_n=20):
        """Use Scikit-learn's TF-IDF Vectorizer to score and return top terms in document."""
        if not text or len(text.strip()) < 10:
            return []
            
        try:
            # We vectorize a single document, which evaluates word importance based on local density
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Pair names with their scores
            paired = list(zip(feature_names, scores))
            # Sort descending by weight
            paired.sort(key=lambda x: x[1], reverse=True)
            
            return [(word, float(score)) for word, score in paired[:top_n]]
        except Exception:
            # Fallback to frequency if tfidf fails due to single-token vocabularies or exceptions
            return self.extract_keywords_frequency(text, top_n)

    def extract_keywords_frequency(self, text, top_n=20):
        """Count literal word occurrences (excluding common stopwords)."""
        if not text:
            return []
            
        # Clean standard symbols and lowercase
        words = re.findall(r'\b[a-zA-Z]{3,20}\b', text.lower())
        
        # Simple stopword exclusion list
        stopwords = {
            'and', 'the', 'for', 'with', 'from', 'this', 'that', 'our', 'your', 'are', 'was',
            'were', 'been', 'have', 'has', 'had', 'will', 'shall', 'should', 'would', 'could',
            'can', 'may', 'might', 'must', 'about', 'above', 'after', 'again', 'against',
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'than', 'too', 'very', 'but', 'nor', 'not', 'only', 'own', 'same', 'she', 'him',
            'her', 'its', 'their', 'them', 'who', 'whom', 'why', 'how', 'when', 'where'
        }
        
        filtered_words = [w for w in words if w not in stopwords]
        counts = Counter(filtered_words)
        
        return [(word, count) for word, count in counts.most_common(top_n)]

    def extract_ngrams(self, text, n=2, top_k=15):
        """Extract multi-word phrase combinations (n-grams) to reveal full title structures (e.g. 'Project Manager')."""
        if not text:
            return []
            
        # Clean and split into words
        words = re.findall(r'\b[a-zA-Z]{2,20}\b', text.lower())
        
        # Build list of overlapping tuples
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i+n])
            ngrams.append(ngram)
            
        counts = Counter(ngrams)
        return [(phrase, count) for phrase, count in counts.most_common(top_k)]
