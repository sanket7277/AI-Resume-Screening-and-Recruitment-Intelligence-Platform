"""
scripts/test_app.py — Automated endpoint testing suite.
Verifies all core blueprints, database models, and matching engine integrations.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume, CandidateProfile
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult

app = create_app('testing')

class TestRecruitIQ(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.seed_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_test_data(self):
        # Create test users
        self.admin = User(username='test_admin', email='test_admin@test.com', role='admin')
        self.admin.set_password('pass123!')
        
        self.recruiter = User(username='test_recruiter', email='test_recruiter@test.com', role='recruiter')
        self.recruiter.set_password('pass123!')
        
        self.candidate = User(username='test_candidate', email='test_candidate@test.com', role='candidate')
        self.candidate.set_password('pass123!')
        
        db.session.add_all([self.admin, self.recruiter, self.candidate])
        db.session.commit()

        # Create a job
        self.job = JobDescription(
            recruiter_id=self.recruiter.id,
            title='Software Engineer',
            company='TestCorp',
            description='Test Job Description',
            required_skills_list=['python', 'sql']
        )
        db.session.add(self.job)
        db.session.commit()

        # Create a resume
        self.resume = Resume(
            user_id=self.candidate.id,
            filename='test_resume.pdf',
            original_filename='test_resume.pdf',
            file_size=1024,
            file_type='pdf',
            status='analyzed',
            raw_text='Python and SQL software engineer.'
        )
        db.session.add(self.resume)
        db.session.flush()

        self.profile = CandidateProfile(
            resume_id=self.resume.id,
            name='Test Candidate',
            email='test_candidate@test.com',
            skills_list=['python', 'sql'],
            total_experience_years=3.5,
            education_list=[{'degree': 'Bachelors'}]
        )
        db.session.add(self.profile)
        db.session.commit()

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_auth_pages(self):
        # Login page GET
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        
        # Register page GET
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.login('test_admin@test.com', 'pass123!')
        self.assertIn(b'test_admin', response.data)

    def test_dashboard_redirects_if_anonymous(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)

    def test_dashboard_success_after_login(self):
        self.login('test_recruiter@test.com', 'pass123!')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_resume_list_and_view(self):
        self.login('test_recruiter@test.com', 'pass123!')
        response = self.client.get('/resume/')
        self.assertEqual(response.status_code, 200)
        # Template renders candidate_name, not filename
        self.assertIn(b'Test Candidate', response.data)

        response = self.client.get(f'/resume/view/{self.resume.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Candidate', response.data)

    def test_job_list_and_detail(self):
        self.login('test_candidate@test.com', 'pass123!')
        response = self.client.get('/jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Software Engineer', response.data)

    def test_matching_engine_computation(self):
        self.login('test_recruiter@test.com', 'pass123!')
        try:
            response = self.client.post('/matching/run', data=dict(
                job_id=self.job.id,
                resume_ids=[str(self.resume.id)]
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            mr = MatchResult.query.filter_by(resume_id=self.resume.id, job_id=self.job.id).first()
            self.assertIsNotNone(mr)
        except Exception as e:
            if 'DLL load failed' in str(e) or 'Application Control' in str(e):
                self.skipTest(f'OS Application Control blocked scipy DLL: {e}')
            raise

    def test_analytics_dashboard(self):
        self.login('test_recruiter@test.com', 'pass123!')
        response = self.client.get('/analytics/')
        self.assertEqual(response.status_code, 200)

    def test_api_endpoints(self):
        self.login('test_recruiter@test.com', 'pass123!')
        
        # API stats overview
        response = self.client.get('/api/v1/stats/overview')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'total_resumes', response.data)

        # API search
        response = self.client.get('/api/v1/search?q=python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Candidate', response.data)


if __name__ == '__main__':
    unittest.main()
