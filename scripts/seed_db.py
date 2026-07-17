"""
scripts/seed_db.py — Database seeder
Creates an admin user, sample recruiters, demo candidates, job postings,
and runs synthetic match results so the platform has realistic demo data on first launch.

Usage:
    python scripts/seed_db.py
"""
import sys
import os

# Add project root to path so we can import from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume, CandidateProfile
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult
import random

# ---- Demo data definitions ----

SAMPLE_JOBS = [
    {
        'title': 'Senior Data Scientist',
        'company': 'TechCorp Inc.',
        'department': 'Data & AI',
        'location': 'San Francisco, CA',
        'employment_type': 'Full-time',
        'description': 'Join our world-class Data & AI team to build production ML models at scale. '
                       'You will lead projects across customer churn prediction, recommendation engines, '
                       'and large language model fine-tuning.',
        'requirements': 'Python, Machine Learning, Deep Learning, PyTorch, Scikit-learn, SQL, '
                        'Docker, MLflow, 5+ years experience, Masters or PhD preferred.',
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'Scikit-learn', 'SQL', 'Docker', 'MLflow'],
        'min_experience': 5,
        'education_required': "Master's Degree",
        'salary_min': 140000,
        'salary_max': 200000,
    },
    {
        'title': 'Frontend Engineer',
        'company': 'StartupXYZ',
        'department': 'Engineering',
        'location': 'Remote',
        'employment_type': 'Full-time',
        'description': 'Build beautiful, performant UIs for our SaaS platform using React and TypeScript.',
        'requirements': 'React, TypeScript, CSS, HTML, REST APIs, Git, 3+ years experience.',
        'required_skills': ['React', 'TypeScript', 'JavaScript', 'HTML', 'CSS', 'Git', 'REST APIs'],
        'min_experience': 3,
        'education_required': "Bachelor's Degree",
        'salary_min': 95000,
        'salary_max': 130000,
    },
    {
        'title': 'DevOps / Site Reliability Engineer',
        'company': 'CloudBase Ltd.',
        'department': 'Infrastructure',
        'location': 'New York, NY',
        'employment_type': 'Full-time',
        'description': 'Manage CI/CD pipelines, Kubernetes clusters, and cloud infrastructure on AWS.',
        'requirements': 'Kubernetes, Docker, AWS, Terraform, CI/CD, Python, Linux, 4+ years.',
        'required_skills': ['Kubernetes', 'Docker', 'AWS', 'Terraform', 'CI/CD', 'Python', 'Linux'],
        'min_experience': 4,
        'education_required': "Bachelor's Degree",
        'salary_min': 110000,
        'salary_max': 160000,
    },
    {
        'title': 'Data Analyst',
        'company': 'FinanceFlow',
        'department': 'Business Intelligence',
        'location': 'Austin, TX',
        'employment_type': 'Full-time',
        'description': 'Analyze large financial datasets to surface business insights for executive leadership.',
        'requirements': 'SQL, Python, Tableau, Excel, Statistics, 2+ years experience.',
        'required_skills': ['SQL', 'Python', 'Tableau', 'Excel', 'Statistics', 'Power BI'],
        'min_experience': 2,
        'education_required': "Bachelor's Degree",
        'salary_min': 70000,
        'salary_max': 95000,
    },
    {
        'title': 'Machine Learning Engineer',
        'company': 'AI Ventures',
        'department': 'ML Platform',
        'location': 'Remote',
        'employment_type': 'Full-time',
        'description': 'Build scalable ML infrastructure, model serving, and feature stores.',
        'requirements': 'Python, TensorFlow, PyTorch, MLOps, Kubernetes, Redis, Kafka.',
        'required_skills': ['Python', 'TensorFlow', 'PyTorch', 'MLOps', 'Kubernetes', 'Kafka', 'Redis'],
        'min_experience': 4,
        'education_required': "Master's Degree",
        'salary_min': 130000,
        'salary_max': 185000,
    },
]

SAMPLE_CANDIDATES = [
    {
        'name': 'Alice Chen',
        'email': 'alice.chen@email.com',
        'skills': ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'Scikit-learn', 'SQL', 'Docker'],
        'experience_years': 7,
        'education': 'Master\'s Degree',
    },
    {
        'name': 'Bob Martinez',
        'email': 'bob.martinez@email.com',
        'skills': ['React', 'TypeScript', 'JavaScript', 'HTML', 'CSS', 'Git', 'Node.js'],
        'experience_years': 4,
        'education': 'Bachelor\'s Degree',
    },
    {
        'name': 'Carol Kim',
        'email': 'carol.kim@email.com',
        'skills': ['Python', 'SQL', 'Tableau', 'Excel', 'Statistics', 'Power BI', 'R'],
        'experience_years': 3,
        'education': 'Bachelor\'s Degree',
    },
    {
        'name': 'David Nguyen',
        'email': 'david.nguyen@email.com',
        'skills': ['Kubernetes', 'Docker', 'AWS', 'Terraform', 'CI/CD', 'Python', 'Linux', 'Ansible'],
        'experience_years': 6,
        'education': 'Bachelor\'s Degree',
    },
    {
        'name': 'Emma Rodriguez',
        'email': 'emma.r@email.com',
        'skills': ['Python', 'TensorFlow', 'MLOps', 'Kubernetes', 'Kafka', 'Feature Stores', 'Spark'],
        'experience_years': 5,
        'education': 'PhD / Doctorate',
    },
    {
        'name': 'Frank Liu',
        'email': 'frank.liu@email.com',
        'skills': ['Java', 'Spring Boot', 'SQL', 'Microservices', 'Docker', 'PostgreSQL'],
        'experience_years': 8,
        'education': 'Bachelor\'s Degree',
    },
    {
        'name': 'Grace Okonkwo',
        'email': 'grace.o@email.com',
        'skills': ['Python', 'NLP', 'Transformers', 'Scikit-learn', 'Machine Learning', 'Pandas', 'NumPy'],
        'experience_years': 4,
        'education': "Master's Degree",
    },
]


def create_users(candidate_user):
    """Create admin and recruiter accounts."""
    users_created = []

    # Admin account
    if not User.query.filter_by(email='admin@recruitiq.dev').first():
        admin = User(
            username='admin',
            email='admin@recruitiq.dev',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123!')
        db.session.add(admin)
        users_created.append(admin)
        print('  Created admin user: admin@recruitiq.dev / admin123!')

    # Recruiter account
    if not User.query.filter_by(email='recruiter@recruitiq.dev').first():
        recruiter = User(
            username='recruiter1',
            email='recruiter@recruitiq.dev',
            first_name='Sarah',
            last_name='Taylor',
            role='recruiter',
            is_active=True
        )
        recruiter.set_password('recruiter123!')
        db.session.add(recruiter)
        users_created.append(recruiter)
        print('  Created recruiter: recruiter@recruitiq.dev / recruiter123!')

    db.session.flush()
    return users_created


def seed():
    with app.app_context():
        print('\n=== Seeding RecruitIQ Database ===\n')
        db.create_all()

        # Users
        print('[1/4] Creating users...')
        create_users(None)
        db.session.commit()

        recruiter = User.query.filter_by(email='recruiter@recruitiq.dev').first()

        # Candidate users
        candidate_accounts = []
        for c in SAMPLE_CANDIDATES:
            uname = c['email'].split('@')[0].replace('.', '_')
            if not User.query.filter_by(email=c['email']).first():
                user = User(username=uname, email=c['email'], first_name=c['name'].split()[0],
                            last_name=c['name'].split()[-1], role='candidate', is_active=True)
                user.set_password('candidate123!')
                db.session.add(user)
                db.session.flush()
                candidate_accounts.append(user)
        db.session.commit()

        # Resumes (synthetic, no actual file)
        print('[2/4] Creating sample resumes...')
        all_candidates = User.query.filter_by(role='candidate').all()
        resume_map = {}
        for i, user in enumerate(all_candidates):
            if Resume.query.filter_by(user_id=user.id).first():
                continue
            c = SAMPLE_CANDIDATES[i % len(SAMPLE_CANDIDATES)]
            resume = Resume(
                user_id=user.id,
                filename=f'{c["name"].replace(" ", "_")}_resume.pdf',
                original_filename=f'{c["name"].replace(" ", "_")}_resume.pdf',
                file_size=102400,
                file_type='pdf',
                status='analyzed',
                raw_text=f'Sample resume for {c["name"]}. Skills: {", ".join(c["skills"])}. Experience: {c["experience_years"]} years.'
            )
            db.session.add(resume)
            db.session.flush()
            
            profile = CandidateProfile(
                resume_id=resume.id,
                name=c['name'],
                email=c['email'],
                phone=f'+1-555-{random.randint(1000,9999)}',
                skills_list=c['skills'],
                total_experience_years=float(c['experience_years']),
                education_list=[{'degree': c['education']}]
            )
            db.session.add(profile)
            db.session.flush()
            resume_map[user.id] = resume

        db.session.commit()

        # Jobs
        print('[3/4] Creating job postings...')
        job_objects = []
        for jd in SAMPLE_JOBS:
            if not JobDescription.query.filter_by(title=jd['title'], company=jd['company']).first():
                job = JobDescription(
                    recruiter_id=recruiter.id if recruiter else 1,
                    is_active=True,
                    title=jd['title'],
                    company=jd['company'],
                    department=jd['department'],
                    location=jd['location'],
                    employment_type=jd['employment_type'],
                    description=jd['description'] + '\n\nRequirements: ' + jd['requirements'],
                    required_skills_list=jd['required_skills'],
                    min_experience=jd['min_experience'],
                    education_level=jd['education_required'],
                    salary_min=jd['salary_min'],
                    salary_max=jd['salary_max']
                )
                db.session.add(job)
                db.session.flush()
                job_objects.append(job)
        db.session.commit()

        # Synthetic match results
        print('[4/4] Generating match results...')
        all_resumes = Resume.query.filter_by(status='analyzed').all()
        all_jobs = JobDescription.query.filter_by(is_active=True).all()

        for job in all_jobs:
            for resume in all_resumes:
                if MatchResult.query.filter_by(resume_id=resume.id, job_id=job.id).first():
                    continue
                if not resume.candidate_profile:
                    continue
                r_skills = set(s.lower() for s in (resume.candidate_profile.skills_list or []))
                j_skills = set(s.lower() for s in (job.required_skills_list or []))
                matched = list(r_skills & j_skills)
                missing = list(j_skills - r_skills)
                extra = list(r_skills - j_skills)
                skill_match = (len(matched) / len(j_skills) * 100) if j_skills else 50
                semantic = round(random.uniform(0.4, 0.95), 4)
                keyword = round(random.uniform(30, 90), 1)
                exp_match = min(100, (resume.candidate_profile.total_experience_years / max(job.min_experience, 1)) * 100) if job.min_experience else 80
                edu_match = 80.0  # simplified
                overall = round(0.35 * skill_match + 0.25 * (semantic * 100) + 0.20 * keyword + 0.12 * exp_match + 0.08 * edu_match, 2)

                mr = MatchResult(
                    resume_id=resume.id,
                    job_id=job.id,
                    overall_score=overall,
                    skill_match_pct=round(skill_match, 2),
                    semantic_similarity=semantic,
                    keyword_coverage=keyword,
                    experience_match=round(exp_match, 2),
                    education_match=edu_match,
                    matched_skills_list=[s.title() for s in matched],
                    missing_skills_list=[s.title() for s in missing[:8]],
                    extra_skills_list=[s.title() for s in extra[:5]],
                    recommendation='Strong fit — meets most key requirements.' if overall >= 70 else 'Partial fit — consider for interview with reservations.'
                )
                db.session.add(mr)

        db.session.commit()
        print('\n[Success] Database seeded successfully!')
        print('\n  Login credentials:')
        print('  Admin:     admin@recruitiq.dev     / admin123!')
        print('  Recruiter: recruiter@recruitiq.dev / recruiter123!')
        print('  Candidate: alice.chen@email.com    / candidate123!\n')


if __name__ == '__main__':
    seed()
