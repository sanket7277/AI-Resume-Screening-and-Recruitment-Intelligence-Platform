import re
import logging
from app.nlp.text_cleaner import TextCleaner
from app.nlp.entity_extractor import EntityExtractor
from app.services.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)

class NLPPipeline:
    """Orchestrator that takes raw text, runs NLTK/spaCy modules, and builds structured candidate profiles."""
    def __init__(self, taxonomy_path=None):
        self.cleaner = TextCleaner()
        self.entity_extractor = EntityExtractor()
        self.skill_extractor = SkillExtractor(taxonomy_path)

    def process_resume(self, raw_text):
        """Processes resume text through extraction pipelines. Returns structured profile dictionary."""
        if not raw_text:
            return {}

        # 1. Clean the text (leaves structure and lines mostly intact for section parsers)
        cleaned_text = self.cleaner.clean_text(raw_text)

        # 2. Extract key contact entities
        entities = self.entity_extractor.extract_all(raw_text)

        # 3. Extract skills
        skills_dict = self.skill_extractor.extract_skills(raw_text)

        # 4. Extract education details
        education = self._extract_education(raw_text)

        # 5. Extract work experience details
        experience, total_years = self._extract_experience(raw_text)

        # 6. Extract certifications
        certifications = self._extract_certifications(raw_text)

        # 7. Extract projects
        projects = self._extract_projects(raw_text)

        # 8. Extract languages
        languages = self._extract_languages(raw_text)

        # Merge results into a structured profile object
        profile = {
            'name': entities.get('name'),
            'email': entities.get('email'),
            'phone': entities.get('phone'),
            'location': entities.get('location'),
            'summary': self._extract_summary(raw_text),
            'skills': skills_dict.get('all', []),
            'skills_by_category': {
                'programming_languages': skills_dict.get('programming_languages', []),
                'web_frameworks': skills_dict.get('web_frameworks', []),
                'databases': skills_dict.get('databases', []),
                'cloud_platforms': skills_dict.get('cloud_platforms', []),
                'devops_tools': skills_dict.get('devops_tools', []),
                'data_science': skills_dict.get('data_science', []),
                'ai_ml': skills_dict.get('ai_ml', []),
                'testing': skills_dict.get('testing', []),
                'frontend_technologies': skills_dict.get('frontend_technologies', []),
                'soft_skills': skills_dict.get('soft_skills', [])
            },
            'education': education,
            'experience': experience,
            'total_experience_years': total_years,
            'certifications': certifications,
            'projects': projects,
            'links': {
                'github': entities.get('github'),
                'linkedin': entities.get('linkedin'),
                'portfolio': self._extract_portfolio_link(entities.get('urls', []), entities.get('github'), entities.get('linkedin'))
            },
            'languages': languages
        }

        return profile

    def _extract_summary(self, text):
        """Extract a professional summary paragraph by scanning header sections."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for headers like 'Summary', 'Professional Summary', 'Objective'
        summary_index = -1
        for i, line in enumerate(lines[:15]):  # limit search to the top of resume
            if re.match(r'^(?:professional\s+)?(?:summary|objective|profile|about\s+me)\b', line, re.IGNORECASE):
                summary_index = i
                break
                
        if summary_index != -1 and summary_index + 1 < len(lines):
            # Take the next 1-3 lines that aren't headers themselves
            summary_lines = []
            for j in range(summary_index + 1, min(summary_index + 4, len(lines))):
                line = lines[j]
                # Stop if we hit another header-like line (e.g. starts with "Skills", "Education")
                if re.match(r'^(?:skills|education|experience|work|projects|certifications)\b', line, re.IGNORECASE):
                    break
                summary_lines.append(line)
            return " ".join(summary_lines)
            
        # Fallback: return the first block of text that looks like a sentence
        for line in lines[1:5]:
            if len(line.split()) > 10:
                return line
        return ""

    def _extract_education(self, text):
        """Regex parser looking for major degree acronyms and universities."""
        education_records = []
        
        # Heuristics for typical degrees
        degree_patterns = [
            (r'\b(?:B\.?S\.?c?|Bachelor(?:s)?(?:\s+of)?)\b(?:\s+[A-Za-z\s]+)?', 'Bachelor\'s'),
            (r'\b(?:B\.?Tech|B\.?E\.?)\b(?:\s+[A-Za-z\s]+)?', 'Bachelor of Technology'),
            (r'\b(?:M\.?S\.?c?|Master(?:s)?(?:\s+of)?)\b(?:\s+[A-Za-z\s]+)?', 'Master\'s'),
            (r'\b(?:M\.?Tech|M\.?E\.?)\b(?:\s+[A-Za-z\s]+)?', 'Master of Technology'),
            (r'\b(?:M\.?B\.?A\.?)\b', 'MBA'),
            (r'\b(?:Ph\.?D\.?|Doctorate|Doctor\s+of\s+Philosophy)\b', 'PhD'),
            (r'\b(?:Associate(?:\s+of|s)?)\b(?:\s+[A-Za-z\s]+)?', 'Associate\'s'),
            (r'\b(?:Diploma)\b(?:\s+[A-Za-z\s]+)?', 'Diploma')
        ]
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find lines mentioning degrees
        for i, line in enumerate(lines):
            matched_degree = None
            for pattern, degree_label in degree_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    matched_degree = degree_label
                    break
                    
            if matched_degree:
                institution = 'Unknown Institution'
                grad_year = None
                
                # Scan surrounding lines (+/- 1) to find institution names or dates
                context_lines = lines[max(0, i-1) : min(len(lines), i+2)]
                context_text = " \n ".join(context_lines)
                
                # Check for university/college keywords
                uni_pattern = r'\b[A-Za-z\s\-\.]*(?:University|College|Institute|Academy|School)[A-Za-z\s\-\.]*\b'
                uni_match = re.search(uni_pattern, context_text, re.IGNORECASE)
                if uni_match:
                    institution = uni_match.group(0).strip()
                    
                # Look for 4 digit graduation years (e.g. 2018 or 2022)
                year_match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', context_text)
                if year_match:
                    grad_year = int(year_match.group(1))
                    
                education_records.append({
                    'degree': matched_degree,
                    'institution': institution,
                    'graduation_year': grad_year,
                    'raw_line': line
                })
                
        return education_records

    def _extract_experience(self, text):
        """Extract jobs, companies, and guess total experience years based on date ranges."""
        experience_records = []
        total_years = 0.0
        
        # Regex to locate date ranges in work history: e.g. "2019 - 2022", "May 2018 - Present", "04/2017 to 08/2021"
        range_pattern = r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})?[\s\-\/]?\d{4}\s*(?:\-|to|until)\s*(Present|current|Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})?[\s\-\/]?(\d{4})\b'
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Try to parse job titles and companies in lines containing dates
        for i, line in enumerate(lines):
            # Check if line contains a year or date range
            year_matches = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', line)
            if year_matches:
                role = "Software Engineer" # Default placeholder
                company = "Enterprise"
                
                # Check line content or preceding lines for titles
                title_keywords = ['engineer', 'developer', 'manager', 'lead', 'analyst', 'consultant', 'intern', 'architect', 'specialist', 'designer']
                
                # Scan current and preceding line for job title
                role_candidate = ""
                for offset in [0, -1]:
                    check_idx = i + offset
                    if 0 <= check_idx < len(lines):
                        line_words = lines[check_idx].lower()
                        if any(kw in line_words for kw in title_keywords):
                            role_candidate = lines[check_idx]
                            break
                if role_candidate:
                    role = role_candidate
                    
                experience_records.append({
                    'role': role,
                    'company': company,
                    'duration_raw': line,
                })
                
        # Estimate total years from year gaps
        year_tokens = [int(y) for y in re.findall(r'\b(19\d{2}|20[0-2]\d)\b', text)]
        if year_tokens:
            min_year = min(year_tokens)
            max_year = max(year_tokens)
            # Cap at reasonable current year if future values leak
            max_year = min(max_year, 2026)
            diff = max_year - min_year
            total_years = float(max(0, diff))
            
        return experience_records, total_years

    def _extract_certifications(self, text):
        """Scans for industry recognized credentials."""
        certs = []
        cert_names = [
            "AWS Certified", "Solutions Architect", "Cloud Practitioner", "Developer Associate",
            "Azure Fundamentals", "Google Cloud Certified", "PMP", "Project Management Professional",
            "Scrum Master", "Certified ScrumMaster", "CSM", "CISSP", "CompTIA Security+", 
            "CCNA", "CKA", "Certified Kubernetes Administrator", "ITIL", "Six Sigma"
        ]
        
        for name in cert_names:
            # Case insensitive search with word boundaries
            escaped = re.escape(name)
            if re.search(rf'\b{escaped}\b', text, re.IGNORECASE):
                certs.append(name)
                
        return certs

    def _extract_projects(self, text):
        """Locates sections mentioning project portfolios."""
        projects = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for headers like 'Projects', 'Key Projects', 'Academic Projects'
        project_index = -1
        for i, line in enumerate(lines):
            if re.match(r'^(?:academic|key|personal\s+)?projects\b', line, re.IGNORECASE):
                project_index = i
                break
                
        if project_index != -1:
            # Parse subsequent lines until hitting next major header
            for j in range(project_index + 1, min(project_index + 10, len(lines))):
                line = lines[j]
                if re.match(r'^(?:skills|education|experience|work|certifications)\b', line, re.IGNORECASE):
                    break
                # Only include lines with descriptive content
                if len(line.split()) > 3:
                    projects.append({
                        'title': line.split(':')[0] if ':' in line else line[:50].strip(),
                        'description': line
                    })
        return projects

    def _extract_languages(self, text):
        """Matches common spoken languages."""
        languages = []
        known_languages = [
            "English", "Spanish", "French", "German", "Chinese", "Mandarin", 
            "Hindi", "Arabic", "Portuguese", "Russian", "Japanese", "Italian"
        ]
        for lang in known_languages:
            if re.search(rf'\b{lang}\b', text, re.IGNORECASE):
                languages.append(lang)
        return languages

    def _extract_portfolio_link(self, urls, github_link, linkedin_link):
        """Extract generic portfolio sites by excluding social media links."""
        ignore_domains = ['github.com', 'linkedin.com', 'google.com', 'facebook.com', 'twitter.com']
        for url in urls:
            if not any(domain in url.lower() for domain in ignore_domains):
                return url
        return github_link or ""
