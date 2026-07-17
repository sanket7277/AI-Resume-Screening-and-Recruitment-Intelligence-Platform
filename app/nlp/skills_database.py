import os
import json

class SkillsDatabase:
    """Helper class to load, structure, and query the skills taxonomy database."""
    def __init__(self, taxonomy_path=None):
        if not taxonomy_path:
            # Default location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            taxonomy_path = os.path.join(current_dir, '..', '..', 'data', 'skills_taxonomy.json')
            
        self.taxonomy_path = os.path.normpath(taxonomy_path)
        self.taxonomy = self._load_taxonomy()
        
        # Build index mapping (lowercased skill name -> original spelling & category)
        self.flat_skills = {}
        self.category_map = {}
        for category, skills in self.taxonomy.items():
            for skill in skills:
                lowered = skill.lower()
                self.flat_skills[lowered] = skill
                self.category_map[lowered] = category
                
        # Register standard abbreviations / aliases
        self.aliases = self.get_skill_aliases()
        # Merge aliases into lookup indexes
        for alias, standard_name in self.aliases.items():
            lowered_alias = alias.lower()
            if standard_name.lower() in self.flat_skills:
                self.flat_skills[lowered_alias] = standard_name
                self.category_map[lowered_alias] = self.category_map[standard_name.lower()]

    def _load_taxonomy(self):
        """Load skills from JSON file, fallback to minimal hardcoded dict if missing."""
        if os.path.exists(self.taxonomy_path):
            try:
                with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fallback dictionary if JSON loading fails
        return {
            "programming_languages": ["Python", "Java", "C++", "JavaScript", "SQL", "HTML", "CSS"],
            "databases": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"],
            "data_science": ["Pandas", "NumPy", "Scikit-learn"],
            "soft_skills": ["Leadership", "Communication"]
        }

    def get_all_skills(self):
        """Retrieve set of all standardized lowercased skill strings."""
        return set(self.flat_skills.keys())

    def get_category(self, skill_name):
        """Find category of a skill. Returns None if unknown."""
        return self.category_map.get(skill_name.lower())

    def is_valid_skill(self, name):
        """Check if skill string exists in database or aliases."""
        return name.lower() in self.flat_skills

    def get_standard_spelling(self, name):
        """Get canonical capitalization spelling (e.g. 'python' -> 'Python')."""
        return self.flat_skills.get(name.lower(), name)

    def search_skills(self, query):
        """Basic match search for autocomplete or querying."""
        if not query:
            return []
        query_lowered = query.lower()
        results = []
        for lowered, original in self.flat_skills.items():
            if query_lowered in lowered:
                results.append(original)
        return list(set(results))

    def get_skills_by_category(self, category):
        """List all skills in a given category."""
        return self.taxonomy.get(category, [])

    def get_skill_aliases(self):
        """Returns map of common tech skill abbreviations to canonical forms."""
        return {
            "js": "JavaScript",
            "ts": "TypeScript",
            "py": "Python",
            "ml": "Machine Learning",
            "dl": "Deep Learning",
            "nlp": "Natural Language Processing",
            "cv": "Computer Vision",
            "k8s": "Kubernetes",
            "tf": "TensorFlow",
            "aws": "AWS",
            "gcp": "Google Cloud",
            "postgres": "PostgreSQL",
            "mongo": "MongoDB",
            "dockerize": "Docker",
            "dotnet": "ASP.NET",
            "html5": "HTML",
            "css3": "CSS",
            "git": "Git",
            "scrummaster": "Scrum Master",
            "powerbi": "Power BI"
        }
