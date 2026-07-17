import re
import logging

logger = logging.getLogger(__name__)

# Try importing spacy, load model lazily to avoid application startup lag
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed. Regex strategies will be used for entity extraction.")

class EntityExtractor:
    """Extracts contact details, names, locations, links, and organizations from raw resume text."""
    def __init__(self, spacy_model_name='en_core_web_sm'):
        self.spacy_model_name = spacy_model_name
        self._nlp = None

    @property
    def nlp(self):
        """Lazy-loading of the spaCy model to save system RAM on startup."""
        global SPACY_AVAILABLE
        if not SPACY_AVAILABLE:
            return None
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self.spacy_model_name)
            except OSError:
                # Attempt to download model if missing
                try:
                    import subprocess
                    import sys
                    logger.info(f"Downloading spaCy model: {self.spacy_model_name}")
                    subprocess.run([sys.executable, "-m", "spacy", "download", self.spacy_model_name], check=True)
                    self._nlp = spacy.load(self.spacy_model_name)
                except Exception as e:
                    logger.error(f"Could not load or download spaCy model {self.spacy_model_name}: {e}")
                    SPACY_AVAILABLE = False
        return self._nlp

    def extract_name(self, text):
        """Extract candidate's name. Prefers spaCy PERSON entities from the top of the resume."""
        if not text:
            return None
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return None

        # Take first 5 lines as name is always near the header
        header_text = " \n ".join(lines[:5])
        
        if SPACY_AVAILABLE and self.nlp:
            try:
                doc = self.nlp(header_text)
                person_entities = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
                if person_entities:
                    # Clean punctuation
                    name = person_entities[0].strip()
                    # Basic filters: names shouldn't have emails, digits or weird characters
                    if not re.search(r'[@\d\.\:\/]', name) and 1 < len(name.split()) < 5:
                        return name
            except Exception as e:
                logger.warning(f"Error during spaCy name extraction: {e}")

        # Fallback regex-based name heuristics: First line often holds name if it matches letters and spacing
        first_line = lines[0]
        if re.match(r'^[A-Z][a-zA-Z\s]{2,40}$', first_line):
            words = first_line.split()
            if 1 < len(words) < 5:
                return first_line
                
        return None

    def extract_email(self, text):
        """Extract candidate email using standard regex matching."""
        if not text:
            return None
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        """Extract phone number using common formats (supports country codes, parenthesis, spaces)."""
        if not text:
            return None
            
        # Pattern to capture international and domestic forms: e.g., +1 (123) 456-7890 or 9876543210
        pattern = r'(?:(?:\+?([1-9]|[0-9]{2,3}))?[\s\-]?)?(?:\(?([0-9]{3})\)?[\s\-]?)?([0-9]{3})[\s\-]?([0-9]{4})\b'
        match = re.search(pattern, text)
        if match:
            # Reconstruct clean version
            parts = match.groups()
            cleaned = "".join(p for p in parts if p)
            # Basic range check for length sanity
            if 9 <= len(cleaned) <= 15:
                return match.group(0).strip()
                
        # Simpler fallback for basic digit clusters
        fallback_pattern = r'\b(?:\d[\s\-]?){9,13}\d\b'
        fallback_match = re.search(fallback_pattern, text)
        return fallback_match.group(0).strip() if fallback_match else None

    def extract_location(self, text):
        """Extract candidate address/city using spaCy NER GPE/LOC."""
        if not text:
            return None
            
        if SPACY_AVAILABLE and self.nlp:
            try:
                # Candidates usually place location details at the beginning or end of resume
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                search_text = " \n ".join(lines[:10] + lines[-10:])
                doc = self.nlp(search_text)
                locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
                if locations:
                    # Clean and return first location found
                    return locations[0].strip()
            except Exception as e:
                logger.warning(f"Error during spaCy location extraction: {e}")

        # Regex fallback: e.g., "City, State" or "City, Country" (e.g. San Francisco, CA or London, UK)
        pattern = r'\b([A-Z][a-zA-Z\s]+),\s([A-Z]{2}|[A-Z][a-zA-Z\s]+)\b'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def extract_urls(self, text):
        """Extract all URLs/hyperlinks."""
        if not text:
            return []
        pattern = r'https?://(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}(?:/\S*)?'
        return list(set(re.findall(pattern, text)))

    def extract_github(self, text):
        """Extract GitHub profile link if listed."""
        if not text:
            return None
        pattern = r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9\-\_]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://github.com/{match.group(1)}" if match else None

    def extract_linkedin(self, text):
        """Extract LinkedIn profile link if listed."""
        if not text:
            return None
        pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub)/([a-zA-Z0-9\-\_]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        return f"https://linkedin.com/in/{match.group(1)}" if match else None

    def extract_dates(self, text):
        """Extract list of chronological calendar dates."""
        if not text:
            return []
        # Patterns like: MM/YYYY, Jan 2021, March 2020 - Present, 2018 - 2022
        pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})?[\s\-\/]?\d{4}\b'
        return re.findall(pattern, text)

    def extract_organizations(self, text):
        """Extract company names / organizations."""
        if not text:
            return []
        if SPACY_AVAILABLE and self.nlp:
            try:
                doc = self.nlp(text)
                orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
                # Deduplicate and filter out short/garbage names
                return list(set(o.strip() for o in orgs if len(o) > 2))
            except Exception:
                pass
        return []

    def extract_all(self, text):
        """Returns structured dictionary of all key contact and profile entities."""
        cleaned_text = text if text else ""
        return {
            'name': self.extract_name(cleaned_text),
            'email': self.extract_email(cleaned_text),
            'phone': self.extract_phone(cleaned_text),
            'location': self.extract_location(cleaned_text),
            'github': self.extract_github(cleaned_text),
            'linkedin': self.extract_linkedin(cleaned_text),
            'urls': self.extract_urls(cleaned_text)
        }
