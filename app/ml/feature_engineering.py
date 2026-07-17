import numpy as np
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Extracts numerical features from CandidateProfile and JobDescription pairs for model predictions."""
    def __init__(self):
        # Master feature list matching synthetic data structure
        self.feature_names = [
            'num_skills',
            'years_experience',
            'education_level',
            'num_certifications',
            'num_projects',
            'has_github',
            'has_linkedin',
            'gpa',
            'skill_match_pct',
            'keyword_coverage',
            'semantic_similarity',
            'tfidf_similarity'
        ]

    def extract_features(self, profile, job, match_result=None):
        """
        Extract feature vector from candidate profile and job description.
        If match_result is provided, pulls computed details directly, 
        otherwise estimates basic alignments.
        """
        if not profile:
            return np.zeros(len(self.feature_names))

        # 1. Number of skills candidate possesses
        skills = profile.get('skills', [])
        num_skills = len(skills)
        
        # 2. Years experience
        years_exp = float(profile.get('total_experience_years', 0.0))
        
        # 3. Education level numeric mapping
        # bachelors or standard university matches
        edu_list = profile.get('education', [])
        edu_level = 0
        for edu in edu_list:
            deg = edu.get('degree', '').lower()
            if 'ph' in deg or 'doctor' in deg:
                edu_level = max(edu_level, 3)
            elif 'master' in deg or 'm.tech' in deg or 'm.s' in deg or 'mba' in deg:
                edu_level = max(edu_level, 2)
            elif 'bachelor' in deg or 'b.tech' in deg or 'b.e' in deg or 'b.s' in deg:
                edu_level = max(edu_level, 1)
                
        # 4. Certifications count
        num_certs = len(profile.get('certifications', []))
        
        # 5. Projects count
        num_projs = len(profile.get('projects', []))
        
        # 6. Has profile links
        links = profile.get('links', {})
        has_git = 1 if links.get('github') else 0
        has_li = 1 if links.get('linkedin') else 0
        
        # 7. GPA extraction (default 3.0 if not listed)
        gpa = 3.0
        
        # 8. Pull matching details if pre-computed
        skill_match = 0.0
        keyword_cov = 0.0
        semantic_sim = 0.0
        tfidf_sim = 0.0
        
        if match_result:
            skill_match = float(match_result.get('skill_match_pct', 0.0))
            keyword_cov = float(match_result.get('keyword_coverage', 0.0))
            semantic_sim = float(match_result.get('semantic_similarity', 0.0))
            tfidf_sim = float(match_result.get('tfidf_similarity', 0.0))
        else:
            # Quick heuristics if running standalone
            job_req_skills = set(s.lower() for s in job.get('required_skills', [])) if job else set()
            cand_skills = set(s.lower() for s in skills)
            if job_req_skills:
                matched_req = job_req_skills.intersection(cand_skills)
                skill_match = (len(matched_req) / len(job_req_skills)) * 100.0
                keyword_cov = skill_match * 0.8
            else:
                skill_match = 50.0
                keyword_cov = 40.0
            
            # Distance approximations
            semantic_sim = 0.5
            tfidf_sim = 0.4
            
        vector = [
            num_skills,
            years_exp,
            edu_level,
            num_certs,
            num_projs,
            has_git,
            has_li,
            gpa,
            skill_match,
            keyword_cov,
            semantic_sim,
            tfidf_sim
        ]
        
        return np.array(vector)

    def get_feature_names(self):
        """Returns names of features compiled in vector."""
        return self.feature_names

    def prepare_training_data(self, df):
        """Splits DataFrame into features X matrix and labels y array."""
        X = df[self.feature_names].values
        y = df['suitability_label'].values
        return X, y
