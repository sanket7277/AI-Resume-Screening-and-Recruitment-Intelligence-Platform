import re
import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# Try loading sentence-transformers for deep semantic parsing
try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Semantic matching will fallback to TF-IDF cosine similarity.")

class MatchingEngine:
    """Computes matching statistics (skills, education, experience, similarity) between candidate resumes and jobs."""
    def __init__(self, sbert_model_name='all-MiniLM-L6-v2'):
        self.sbert_model_name = sbert_model_name
        self._model = None

    @property
    def model(self):
        """Lazy-load the Sentence-Transformers embedding model to optimize startup memory."""
        global SBERT_AVAILABLE
        if not SBERT_AVAILABLE:
            return None
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.sbert_model_name)
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model {self.sbert_model_name}: {e}")
                SBERT_AVAILABLE = False
        return self._model

    def compute_match(self, resume, job):
        """Wrapper to compute match between Resume and JobDescription models."""
        resume_profile = {
            'raw_text': resume.raw_text,
            'skills': resume.candidate_profile.skills_list if resume.candidate_profile else [],
            'education': resume.candidate_profile.education_list if resume.candidate_profile else [],
            'total_experience_years': resume.candidate_profile.total_experience_years if resume.candidate_profile else 0.0
        }
        job_description = {
            'description': job.description,
            'required_skills': job.required_skills if job.required_skills else [],
            'preferred_skills': job.preferred_skills if job.preferred_skills else [],
            'education_level': job.education_level,
            'min_experience': job.min_experience
        }
        return self.calculate_match(resume_profile, job_description)

    def calculate_match(self, resume_profile, job_description):
        """
        Compare resume vs job. Returns dictionary containing detailed matching breakdowns:
        ats_score, skill_match_pct, experience_match, education_match, semantic_similarity, etc.
        """
        if not resume_profile or not job_description:
            return {}

        resume_text = resume_profile.get('raw_text', '') or ''
        job_text = job_description.get('description', '') or ''
        
        # 1. Skill Match Percentage
        required_skills = set(s.lower() for s in job_description.get('required_skills', []))
        preferred_skills = set(s.lower() for s in job_description.get('preferred_skills', []))
        candidate_skills = set(s.lower() for s in resume_profile.get('skills', []))
        
        matched_required = required_skills.intersection(candidate_skills)
        matched_preferred = preferred_skills.intersection(candidate_skills)
        
        missing_skills = list(required_skills - candidate_skills)
        extra_skills = list(candidate_skills - required_skills.union(preferred_skills))
        
        if required_skills:
            skill_match_pct = (len(matched_required) / len(required_skills)) * 100.0
        else:
            skill_match_pct = 100.0 # No requirements means 100% match
            
        # 2. Education Match
        edu_match_score = self._evaluate_education_match(resume_profile.get('education', []), job_description.get('education_level', 'any'))
        
        # 3. Experience Match
        exp_match_score = self._evaluate_experience_match(resume_profile.get('total_experience_years', 0.0), job_description.get('min_experience', 0))
        
        # 4. TF-IDF Cosine Similarity
        tfidf_sim = self._calculate_tfidf_similarity(resume_text, job_text)
        
        # 5. Semantic Similarity (Sentence Transformers)
        semantic_sim = self._calculate_semantic_similarity(resume_text, job_text)
        
        # Overall weighted ATS Score calculation:
        # 35% Skills match
        # 20% Semantic Similarity
        # 15% TF-IDF Cosine Similarity
        # 15% Experience match
        # 10% Education alignment
        # 5% Keyword coverage
        keyword_coverage = self._calculate_keyword_coverage(resume_text, job_text)
        
        ats_score = (
            (skill_match_pct * 0.35) +
            (semantic_sim * 100.0 * 0.20) +
            (tfidf_sim * 100.0 * 0.15) +
            (exp_match_score * 0.15) +
            (edu_match_score * 0.10) +
            (keyword_coverage * 0.05)
        )
        ats_score = min(round(ats_score, 1), 100.0)

        # Generate strengths & weaknesses
        strengths, weaknesses, suggestions = self._generate_bullet_points(
            matched_required, missing_skills, exp_match_score, edu_match_score, semantic_sim
        )

        # Generate a simple recommendation based on score
        if ats_score >= 75.0:
            recommendation = "Highly suitable candidate. Strong match with core technical skills and experience guidelines. Recommend immediate interview."
        elif ats_score >= 50.0:
            recommendation = "Suitable candidate. Good match with most requirements. Consider for screening round."
        else:
            recommendation = "Not suitable candidate. Significant gaps in core skills and experience."

        return {
            'skill_match_pct': round(skill_match_pct, 1),
            'education_match': float(edu_match_score),
            'experience_match': float(exp_match_score),
            'ats_score': ats_score,
            'overall_score': ats_score,
            'keyword_coverage': round(keyword_coverage, 1),
            
            'matched_skills': [s.title() for s in list(matched_required.union(matched_preferred))],
            'missing_skills': [s.title() for s in missing_skills],
            'extra_skills': [s.title() for s in extra_skills[:15]], # Limit noise
            'recommended_skills': [s.title() for s in missing_skills[:5]], # Suggest missing
            
            'semantic_similarity': round(semantic_sim, 3),
            'tfidf_similarity': round(tfidf_sim, 3),
            'cosine_similarity': round(semantic_sim, 3),
            'recommendation': recommendation,
            
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }

    def rank_candidates(self, candidates_list, job_description):
        """Rank a batch of candidate profiles against a job. Returns sorted list by ATS score."""
        ranked = []
        for cand in candidates_list:
            match = self.calculate_match(cand, job_description)
            ranked.append({
                'candidate': cand,
                'match': match
            })
            
        # Sort descending by ATS Score
        ranked.sort(key=lambda x: x['match']['ats_score'], reverse=True)
        
        for idx, item in enumerate(ranked):
            item['match']['overall_rank'] = idx + 1
            
        return ranked

    def _evaluate_education_match(self, candidate_education, required_level):
        """Map degrees to numeric scale and check if requirements are met."""
        if not required_level or required_level.lower() in ['any', 'none']:
            return 100.0
            
        level_map = {'high school': 0, 'associate': 1, 'bachelors': 2, 'masters': 3, 'phd': 4}
        
        req_val = level_map.get(required_level.lower(), 2) # Default bachelors requirement
        
        cand_max_val = 0
        for edu in candidate_education:
            deg = edu.get('degree', '').lower()
            if 'ph' in deg or 'doctor' in deg:
                cand_max_val = max(cand_max_val, 4)
            elif 'master' in deg or 'm.tech' in deg or 'm.s' in deg or 'mba' in deg:
                cand_max_val = max(cand_max_val, 3)
            elif 'bachelor' in deg or 'b.tech' in deg or 'b.e' in deg or 'b.s' in deg:
                cand_max_val = max(cand_max_val, 2)
            elif 'associate' in deg:
                cand_max_val = max(cand_max_val, 1)
                
        if cand_max_val >= req_val:
            return 100.0
        elif cand_max_val == req_val - 1:
            return 70.0 # One level below
        return 40.0

    def _evaluate_experience_match(self, candidate_years, required_years):
        """Compare candidate experience against min requirements."""
        if not required_years or required_years <= 0:
            return 100.0
            
        if candidate_years >= required_years:
            return 100.0
        elif candidate_years > 0:
            # Proportional score
            return round((candidate_years / required_years) * 100.0, 1)
        return 0.0

    def _calculate_tfidf_similarity(self, text1, text2):
        """Compute standard TF-IDF Cosine Similarity."""
        if not text1 or not text2:
            return 0.0
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf = vectorizer.fit_transform([text1, text2])
            pairwise_similarity = (tfidf * tfidf.T).toarray()[0, 1]
            return float(pairwise_similarity)
        except Exception:
            return 0.0

    def _calculate_semantic_similarity(self, text1, text2):
        """Compute Sentence-Transformers semantic alignment."""
        if not text1 or not text2:
            return 0.0
            
        if SBERT_AVAILABLE and self.model:
            try:
                embeddings = self.model.encode([text1, text2])
                emb1 = embeddings[0] / np.linalg.norm(embeddings[0])
                emb2 = embeddings[1] / np.linalg.norm(embeddings[1])
                cosine_sim = np.dot(emb1, emb2)
                # Map from [-1, 1] range to [0, 1]
                return float(max(0.0, cosine_sim))
            except Exception as e:
                logger.error(f"Semantic encoding failed: {e}")
                
        # Fallback to TF-IDF
        return self._calculate_tfidf_similarity(text1, text2)

    def _calculate_keyword_coverage(self, resume_text, job_text):
        """Count unique words shared between both documents."""
        if not resume_text or not job_text:
            return 0.0
            
        # Clean and extract lowercase tokens
        words_resume = set(re.findall(r'\b[a-zA-Z]{3,20}\b', resume_text.lower()))
        words_job = set(re.findall(r'\b[a-zA-Z]{3,20}\b', job_text.lower()))
        
        # Filter stopwords
        stop_words = {'and', 'the', 'for', 'with', 'from', 'this', 'that', 'are', 'your', 'our'}
        keywords_job = words_job - stop_words
        
        if not keywords_job:
            return 100.0
            
        matched = keywords_job.intersection(words_resume)
        return (len(matched) / len(keywords_job)) * 100.0

    def _generate_bullet_points(self, matched_req, missing_skills, exp_score, edu_score, semantic_sim):
        """Formulates resume matching strength, weakness, and suggestions arrays."""
        strengths = []
        weaknesses = []
        suggestions = []

        # Strengths
        if matched_req:
            strengths.append(f"Demonstrates core required skills: {', '.join(list(matched_req)[:4]).title()}")
        if exp_score >= 100.0:
            strengths.append("Meets or exceeds target work experience duration guidelines.")
        if edu_score >= 100.0:
            strengths.append("Possesses required academic degree level qualification.")
        if semantic_sim >= 0.65:
            strengths.append("Resume shows high semantic alignment to responsibilities description.")

        # Weaknesses
        if missing_skills:
            weaknesses.append(f"Missing key required skills: {', '.join(list(missing_skills)[:4]).title()}")
        if exp_score < 70.0:
            weaknesses.append("Has significantly less work experience than requested.")
        if edu_score < 70.0:
            weaknesses.append("Degree credentials fall below listed requirements.")
        if semantic_sim < 0.40:
            weaknesses.append("Language structure and focus deviate from the job description.")

        # Suggestions
        for skill in list(missing_skills)[:3]:
            suggestions.append(f"Add certification or project demonstrating proficiency in {skill.title()}.")
        if exp_score < 100.0:
            suggestions.append("Highlight transferable duties or freelance experience to bridge experience gaps.")
        if semantic_sim < 0.65:
            suggestions.append("Tailor resume summary/keywords to highlight responsibilities keywords listed in the job.")

        # Default fallback values
        if not strengths:
            strengths.append("Candidate possesses general transferable skills.")
        if not weaknesses:
            weaknesses.append("No critical misalignment points discovered.")
        if not suggestions:
            suggestions.append("Structure resume to feature practical project metrics.")

        return strengths, weaknesses, suggestions
