import re
import string
import logging

logger = logging.getLogger(__name__)

# Try loading NLTK libraries, handle environment errors gracefully.
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Download packages if missing
    def _initialize_nltk():
        resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        for r in resources:
            try:
                nltk.data.find(f'corpora/{r}' if r != 'punkt' else f'tokenizers/{r}')
            except LookupError:
                try:
                    nltk.download(r, quiet=True)
                except Exception as e:
                    logger.warning(f"Could not download NLTK package {r}: {e}")
                    
    _initialize_nltk()
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("NLTK library not available, fallback cleaners will be used.")

class TextCleaner:
    """Helper to clean, normalize, tokenize, and preprocess candidate documents."""
    def __init__(self):
        global NLTK_AVAILABLE
        if NLTK_AVAILABLE:
            try:
                self.lemmatizer = WordNetLemmatizer()
                self.stop_words = set(stopwords.words('english'))
            except Exception:
                NLTK_AVAILABLE = False
                
        if not NLTK_AVAILABLE:
            # Fallback simple stopwords list
            self.stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
                'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it',
                'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
                'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
                'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
                'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
                'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
                "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't"
            }

    def to_lowercase(self, text):
        """Standardize text casing."""
        return text.lower() if text else ""

    def remove_urls(self, text):
        """Remove hyperlinks."""
        if not text:
            return ""
        # Match standard url structures
        pattern = r'https?://\S+|www\.\S+'
        return re.sub(pattern, '', text)

    def remove_email_addresses(self, text):
        """Remove emails from body text."""
        if not text:
            return ""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.sub(pattern, '', text)

    def remove_phone_numbers(self, text):
        """Remove telephone listings."""
        if not text:
            return ""
        # Simple phone layout removal
        pattern = r'[\+]?[\d\s\-\(\)]{10,15}'
        return re.sub(pattern, '', text)

    def remove_special_characters(self, text, keep_periods=True):
        """Remove formatting artifacts and weird punctuation symbols."""
        if not text:
            return ""
        if keep_periods:
            # Keep letters, numbers, spaces, periods, and commas
            pattern = r'[^a-zA-Z0-9\s\.,\+\-\#\/\:]'
        else:
            pattern = r'[^a-zA-Z0-9\s\+\-\#\/\:]'
        return re.sub(pattern, ' ', text)

    def normalize_whitespace(self, text):
        """Convert multiple spaces/tabs/newlines to single spaces."""
        if not text:
            return ""
        return " ".join(text.split())

    def clean_text(self, text):
        """Perform standard structural cleaning (leaves casing and stopwords intact)."""
        if not text:
            return ""
        cleaned = self.remove_urls(text)
        cleaned = self.remove_email_addresses(cleaned)
        cleaned = self.remove_phone_numbers(cleaned)
        cleaned = self.remove_special_characters(cleaned, keep_periods=True)
        cleaned = self.normalize_whitespace(cleaned)
        return cleaned

    def tokenize(self, text):
        """Split text into words."""
        if not text:
            return []
        if NLTK_AVAILABLE:
            try:
                return word_tokenize(text)
            except Exception:
                pass
        # Fallback split
        return re.findall(r'\b\w+\b', text.lower())

    def remove_stopwords(self, text_or_tokens):
        """Remove common noise words."""
        if isinstance(text_or_tokens, str):
            tokens = self.tokenize(text_or_tokens)
        else:
            tokens = text_or_tokens
            
        return [w for w in tokens if w.lower() not in self.stop_words]

    def lemmatize_text(self, tokens):
        """Reduce words to standard dictionary base/lemma representation."""
        if not tokens:
            return []
        if NLTK_AVAILABLE:
            try:
                return [self.lemmatizer.lemmatize(token) for token in tokens]
            except Exception:
                pass
        return tokens  # Fallback: no-op

    def full_clean(self, text):
        """Run text through full lowercase -> clean -> tokenize -> stopwords -> lemma pipeline."""
        if not text:
            return ""
        cleaned = self.clean_text(text)
        lowered = self.to_lowercase(cleaned)
        tokens = self.tokenize(lowered)
        no_stop = self.remove_stopwords(tokens)
        lemmatized = self.lemmatize_text(no_stop)
        return " ".join(lemmatized)

    def extract_sentences(self, text):
        """Split text into distinct sentences."""
        if not text:
            return []
        if NLTK_AVAILABLE:
            try:
                return sent_tokenize(text)
            except Exception:
                pass
        # Fallback regex split
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        return [s.strip() for s in sentences if s.strip()]
