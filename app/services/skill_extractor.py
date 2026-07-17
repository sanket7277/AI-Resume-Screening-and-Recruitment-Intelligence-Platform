import re
from collections import Counter
from app.nlp.skills_database import SkillsDatabase

class SkillExtractor:
    """Extracts technical, tool, soft, and language skills from text documents."""
    def __init__(self, taxonomy_path=None):
        self.db = SkillsDatabase(taxonomy_path)

    def extract_skills(self, text):
        """
        Scan text for matches against standard skills taxonomy.
        Considers multi-word skills, case variants, and aliases.
        """
        if not text:
            return {
                'technical_skills': [],
                'soft_skills': [],
                'tools': [],
                'frameworks': [],
                'databases': [],
                'cloud_platforms': [],
                'devops_tools': [],
                'data_science': [],
                'ai_ml': [],
                'testing': [],
                'frontend_technologies': [],
                'all': []
            }
            
        lowered_text = text.lower()
        
        # Word boundaries cleanup for easy lookup
        # Replace dashes and slashes with spaces to catch compound terms like 'CI/CD' -> 'CI CD'
        normalized_text = re.sub(r'[\/\-\,]', ' ', lowered_text)
        words = re.findall(r'\b\w+\b', normalized_text)
        
        # Build list of 1-word, 2-word, and 3-word phrase sliding windows
        unigrams = words
        bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]
        trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
        
        candidates = set(unigrams + bigrams + trigrams)
        
        # Retrieve all standard names from database
        all_skills = self.db.get_all_skills()
        
        extracted_lowered = []
        for candidate in candidates:
            # Check if this phrase is a valid skill in our master database
            if candidate in all_skills:
                extracted_lowered.append(candidate)
                
        # Resolve abbreviations/aliases to standard spellings (e.g. 'js' -> 'JavaScript')
        standardized_skills = set()
        for s in extracted_lowered:
            standardized_name = self.db.get_standard_spelling(s)
            standardized_skills.add(standardized_name)
            
        # Categorize matches
        categorized = {
            'programming_languages': [],
            'web_frameworks': [],
            'databases': [],
            'cloud_platforms': [],
            'devops_tools': [],
            'data_science': [],
            'ai_ml': [],
            'mobile_development': [],
            'testing': [],
            'version_control': [],
            'operating_systems': [],
            'networking': [],
            'security': [],
            'project_management': [],
            'design_tools': [],
            'soft_skills': [],
            'certifications_keywords': [],
            'frontend_technologies': []
        }
        
        for skill in standardized_skills:
            category = self.db.get_category(skill)
            if category in categorized:
                categorized[category].append(skill)
                
        # Sort each list alphabetically
        for cat in categorized:
            categorized[cat].sort()
            
        # Create a flat set of all found skills
        all_flat = list(standardized_skills)
        all_flat.sort()
        categorized['all'] = all_flat
        
        # Return merged dict
        return categorized

    def get_skill_frequency(self, text):
        """Count raw density counts for each matching skill."""
        if not text:
            return {}
            
        extracted = self.extract_skills(text)
        all_found = extracted['all']
        
        counts = {}
        for skill in all_found:
            # Count exact matches (case-insensitive regex)
            # Escaping in case the skill contains special symbols like C++
            escaped = re.escape(skill)
            pattern = rf'\b{escaped}\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            counts[skill] = len(matches) if matches else 1 # default to 1 if found via alias mapping
            
        return counts
