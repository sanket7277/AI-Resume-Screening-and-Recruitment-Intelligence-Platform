"""
Script to remove all dummy resumes except Sanket Kolhe's,
then seed multi-domain resumes for Sanket Kolhe.
"""
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.resume import Resume, CandidateProfile
from app.models.match_result import MatchResult
from app.models.user import User

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

RESUMES = [
    {
        "domain": "Data Analyst",
        "filename": "sanket_kolhe_data_analyst.pdf",
        "raw_text": """SANKET KOLHE
Data Analyst
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Results-driven Data Analyst with 2.5 years of hands-on experience in transforming raw data into actionable business insights. Proficient in Python, SQL, Tableau, and Power BI. Skilled at building ETL pipelines, statistical modeling, and crafting executive dashboards that drive strategic decisions. Passionate about uncovering patterns in large datasets and communicating complex findings to non-technical stakeholders.

SKILLS
Python, SQL, R, Tableau, Power BI, Excel, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, MySQL, PostgreSQL, MongoDB, Apache Spark, Jupyter Notebook, Git, Data Warehousing, ETL, Statistical Analysis, Hypothesis Testing, A/B Testing, Data Visualization, Data Cleaning, Regression Analysis, Time Series Analysis

EXPERIENCE
Data Analyst | Infosys Ltd | Pune, India | 2023 - 2026
- Designed and maintained 15+ interactive Tableau dashboards tracking KPIs across sales, marketing, and operations departments
- Built automated ETL pipelines using Python and Apache Airflow, reducing manual data processing time by 60%
- Conducted A/B testing for product feature launches, directly influencing product roadmap decisions for 3 features
- Performed cohort analysis and customer segmentation using K-means clustering, improving targeted marketing ROI by 25%
- Wrote complex SQL queries to extract and transform data from 10+ relational databases for monthly business reviews

Junior Data Analyst | TCS | Mumbai, India | 2021 - 2023
- Analyzed sales data to identify revenue trends and seasonal patterns, presented quarterly reports to leadership
- Created Power BI reports integrating data from CRM, ERP, and web analytics platforms
- Automated weekly reporting workflows using Python scripts, saving 8 hours per week
- Cleaned and preprocessed datasets with 500K+ records for machine learning model training

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
Google Data Analytics Professional Certificate
Microsoft Power BI Data Analyst Associate
IBM Data Science Professional Certificate

PROJECTS
Sales Forecasting Dashboard - Built a time series forecasting model using ARIMA and Prophet to predict quarterly sales with 92% accuracy. Visualized results in Tableau.
Customer Churn Prediction - Developed a logistic regression model to predict customer churn with 88% accuracy using Python and Scikit-learn.
COVID-19 Data Analysis - Analyzed global COVID-19 datasets, built interactive dashboards in Power BI tracking infection rates, recoveries, and vaccination progress.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["Python", "SQL", "R", "Tableau", "Power BI", "Excel", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn", "MySQL", "PostgreSQL", "MongoDB", "Apache Spark", "Git", "ETL", "Statistical Analysis", "A/B Testing", "Data Visualization", "Data Cleaning", "Regression Analysis", "Time Series Analysis"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Data Analyst", "company": "Infosys Ltd", "duration_raw": "2023 - 2026"},
            {"role": "Junior Data Analyst", "company": "TCS", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["Google Data Analytics Professional Certificate", "Microsoft Power BI Data Analyst Associate", "IBM Data Science Professional Certificate"],
        "summary": "Results-driven Data Analyst with 2.5 years of hands-on experience in transforming raw data into actionable business insights. Proficient in Python, SQL, Tableau, and Power BI."
    },
    {
        "domain": "Cloud Engineer",
        "filename": "sanket_kolhe_cloud_engineer.pdf",
        "raw_text": """SANKET KOLHE
Cloud Engineer
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Certified AWS and Azure Cloud Engineer with 3 years of experience designing, deploying, and managing scalable cloud infrastructure. Expertise in infrastructure-as-code, containerization, CI/CD pipelines, and cloud-native services. Strong background in automating deployment workflows and implementing robust security practices on multi-cloud environments.

SKILLS
AWS, Azure, GCP, Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, Linux, Bash, Python, CloudFormation, ARM Templates, VPC, EC2, S3, Lambda, RDS, EKS, IAM, CloudWatch, Azure DevOps, Networking, Load Balancing, Auto Scaling, Serverless, Microservices, Prometheus, Grafana, Helm, Nginx

EXPERIENCE
Cloud Engineer | Wipro Technologies | Pune, India | 2023 - 2026
- Architected and deployed multi-region AWS infrastructure serving 2M+ daily requests using Terraform and CloudFormation
- Managed Kubernetes clusters on EKS with 50+ microservices, achieving 99.95% uptime SLA
- Implemented CI/CD pipelines using Jenkins and GitHub Actions, reducing deployment time from 4 hours to 15 minutes
- Designed VPC architectures with proper subnet segmentation, security groups, and NACLs for production workloads
- Set up centralized monitoring using Prometheus, Grafana, and CloudWatch with automated alerting

Junior Cloud Engineer | Cognizant | Hyderabad, India | 2021 - 2023
- Migrated 25+ on-premise applications to AWS, reducing infrastructure costs by 40%
- Automated server provisioning using Ansible playbooks and Terraform modules
- Managed Azure Active Directory and IAM policies for enterprise clients with 500+ users
- Configured auto-scaling groups and load balancers for high-availability web applications

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
AWS Solutions Architect Associate
AWS Cloud Practitioner
Microsoft Azure Fundamentals (AZ-900)
Certified Kubernetes Administrator (CKA)
HashiCorp Certified Terraform Associate

PROJECTS
Multi-Cloud Disaster Recovery - Designed a cross-cloud DR strategy across AWS and Azure with automated failover using Route53 and Terraform. Achieved RPO < 5 minutes.
Serverless Data Pipeline - Built event-driven data pipeline using AWS Lambda, S3, SQS, and DynamoDB processing 1M+ events per day.
Kubernetes Platform Engineering - Deployed a self-service developer platform on EKS with Helm charts, ArgoCD, and custom operators.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "Linux", "Bash", "Python", "CloudFormation", "EC2", "S3", "Lambda", "RDS", "EKS", "IAM", "CloudWatch", "Prometheus", "Grafana", "Helm", "Nginx", "Microservices", "Serverless", "Networking"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Cloud Engineer", "company": "Wipro Technologies", "duration_raw": "2023 - 2026"},
            {"role": "Junior Cloud Engineer", "company": "Cognizant", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["AWS Solutions Architect Associate", "AWS Cloud Practitioner", "Azure Fundamentals", "Certified Kubernetes Administrator"],
        "summary": "Certified AWS and Azure Cloud Engineer with 3 years of experience designing, deploying, and managing scalable cloud infrastructure."
    },
    {
        "domain": "Java Full Stack Developer",
        "filename": "sanket_kolhe_java_fullstack.pdf",
        "raw_text": """SANKET KOLHE
Java Full Stack Developer
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Experienced Java Full Stack Developer with 3+ years of expertise in building enterprise-grade web applications using Spring Boot, React, and microservices architecture. Strong proficiency in RESTful API design, relational databases, and agile methodologies. Track record of delivering high-performance, scalable solutions for banking and e-commerce domains.

SKILLS
Java, Spring Boot, Spring MVC, Spring Security, Hibernate, JPA, React, Angular, JavaScript, TypeScript, HTML, CSS, Bootstrap, REST API, GraphQL, Maven, Gradle, JUnit, Mockito, MySQL, PostgreSQL, Oracle, MongoDB, Redis, RabbitMQ, Kafka, Docker, Kubernetes, Jenkins, Git, Agile, Scrum, JIRA, IntelliJ IDEA, Microservices, Design Patterns, SOLID Principles

EXPERIENCE
Java Full Stack Developer | Persistent Systems | Pune, India | 2023 - 2026
- Developed and maintained 5 microservices using Spring Boot handling 500K+ daily transactions for a banking platform
- Built responsive front-end modules using React with Redux, improving page load times by 35%
- Designed RESTful APIs following OpenAPI 3.0 specification consumed by mobile and web clients
- Implemented Spring Security with JWT and OAuth2 for authentication and role-based access control
- Wrote comprehensive unit tests using JUnit 5 and Mockito achieving 90%+ code coverage

Associate Software Engineer | Tech Mahindra | Pune, India | 2021 - 2023
- Built full-stack e-commerce features using Java, Spring MVC, and Angular serving 100K+ users
- Optimized SQL queries and database indexing strategies, reducing API response times by 50%
- Integrated third-party payment gateways (Razorpay, Stripe) into existing Spring Boot applications
- Participated in code reviews, sprint planning, and retrospectives as part of an Agile team

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
Oracle Certified Professional Java SE 11 Developer
AWS Developer Associate
Spring Professional Certification

PROJECTS
Banking Microservices Platform - Architected a distributed banking system with 8 microservices using Spring Boot, Kafka, and PostgreSQL. Implemented saga pattern for distributed transactions.
E-Commerce SPA - Built a single-page application using React, Redux, and TypeScript with Spring Boot backend. Features include real-time inventory, cart management, and payment processing.
Task Management API - Developed a RESTful API for project management with Spring Boot, JPA, and PostgreSQL. Includes role-based access, WebSocket notifications, and Swagger documentation.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["Java", "Spring Boot", "Spring MVC", "Spring Security", "Hibernate", "JPA", "React", "Angular", "JavaScript", "TypeScript", "HTML", "CSS", "Bootstrap", "REST API", "GraphQL", "Maven", "JUnit", "MySQL", "PostgreSQL", "Oracle", "MongoDB", "Redis", "Kafka", "Docker", "Kubernetes", "Jenkins", "Git", "Microservices", "Design Patterns"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Java Full Stack Developer", "company": "Persistent Systems", "duration_raw": "2023 - 2026"},
            {"role": "Associate Software Engineer", "company": "Tech Mahindra", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["Oracle Certified Professional Java SE 11 Developer", "AWS Developer Associate", "Spring Professional Certification"],
        "summary": "Experienced Java Full Stack Developer with 3+ years of expertise in building enterprise-grade web applications using Spring Boot, React, and microservices architecture."
    },
    {
        "domain": "Cybersecurity Analyst",
        "filename": "sanket_kolhe_cybersecurity.pdf",
        "raw_text": """SANKET KOLHE
Cybersecurity Analyst
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Dedicated Cybersecurity Analyst with 3 years of experience in threat detection, vulnerability assessment, incident response, and security operations. Proficient in SIEM tools, penetration testing, network security, and compliance frameworks. Passionate about protecting critical infrastructure and staying ahead of evolving cyber threats.

SKILLS
Network Security, Penetration Testing, Vulnerability Assessment, SIEM, Splunk, QRadar, Wireshark, Nmap, Metasploit, Burp Suite, Nessus, Kali Linux, Python, Bash, PowerShell, Firewall Management, IDS/IPS, OWASP Top 10, ISO 27001, NIST, SOC Operations, Incident Response, Digital Forensics, Malware Analysis, Endpoint Detection, CrowdStrike, Threat Intelligence, Risk Assessment, Compliance Auditing

EXPERIENCE
Cybersecurity Analyst | Infosys Ltd | Pune, India | 2023 - 2026
- Monitored and analyzed security events across 500+ endpoints using Splunk SIEM, reducing mean time to detect (MTTD) by 45%
- Conducted penetration testing on web applications and internal networks, identifying and remediating 200+ vulnerabilities
- Led incident response for 15+ security incidents including ransomware, phishing, and unauthorized access attempts
- Implemented CrowdStrike endpoint detection and response (EDR) across the organization
- Developed Python scripts for automated threat hunting and IOC correlation

Junior Security Analyst | HCL Technologies | Noida, India | 2021 - 2023
- Performed regular vulnerability assessments using Nessus and OpenVAS across production environments
- Configured and maintained firewall rules, IDS/IPS policies, and VPN tunnels for enterprise clients
- Created security awareness training materials and conducted phishing simulation campaigns
- Assisted in ISO 27001 and SOC 2 compliance audits, ensuring adherence to security policies

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
CompTIA Security+
Certified Ethical Hacker (CEH)
AWS Certified Security Specialty
CISSP Associate

PROJECTS
SOC Automation Framework - Built automated incident response playbooks using Python and Splunk SOAR, reducing incident response time by 70%.
Web Application Security Scanner - Developed a custom vulnerability scanner in Python that identifies OWASP Top 10 vulnerabilities with automated reporting.
Honeypot Network - Deployed a network of honeypots to study attacker behavior and techniques, contributing to internal threat intelligence feeds.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["Network Security", "Penetration Testing", "Vulnerability Assessment", "SIEM", "Splunk", "QRadar", "Wireshark", "Nmap", "Metasploit", "Burp Suite", "Nessus", "Kali Linux", "Python", "Bash", "PowerShell", "Firewall Management", "IDS/IPS", "OWASP Top 10", "ISO 27001", "NIST", "SOC Operations", "Incident Response", "Digital Forensics", "Malware Analysis", "CrowdStrike", "Threat Intelligence", "Risk Assessment"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Cybersecurity Analyst", "company": "Infosys Ltd", "duration_raw": "2023 - 2026"},
            {"role": "Junior Security Analyst", "company": "HCL Technologies", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["CompTIA Security+", "Certified Ethical Hacker", "AWS Certified Security Specialty"],
        "summary": "Dedicated Cybersecurity Analyst with 3 years of experience in threat detection, vulnerability assessment, incident response, and security operations."
    },
    {
        "domain": "Python Developer",
        "filename": "sanket_kolhe_python_developer.pdf",
        "raw_text": """SANKET KOLHE
Python Developer
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Versatile Python Developer with 3 years of experience building web applications, automation scripts, APIs, and data pipelines. Expert in Django, Flask, FastAPI, and modern Python best practices. Strong foundation in software design patterns, testing, and deployment using Docker and cloud platforms.

SKILLS
Python, Django, Flask, FastAPI, REST API, Celery, Redis, RabbitMQ, SQLAlchemy, PostgreSQL, MySQL, MongoDB, HTML, CSS, JavaScript, React, Docker, Kubernetes, Git, GitHub Actions, CI/CD, Linux, Bash, Pytest, Unittest, Selenium, Scrapy, Beautiful Soup, Pandas, NumPy, AWS Lambda, S3, EC2, Nginx, Gunicorn, WebSockets, GraphQL, Design Patterns, OOP

EXPERIENCE
Python Developer | Capgemini | Pune, India | 2023 - 2026
- Developed and maintained enterprise REST APIs using Django REST Framework serving 1M+ daily requests
- Built asynchronous task processing pipelines using Celery and RabbitMQ for email, notifications, and report generation
- Designed FastAPI microservices for real-time data processing with WebSocket support
- Implemented automated testing using Pytest with 95% code coverage, integrated into CI/CD via GitHub Actions
- Deployed containerized applications on AWS ECS with Docker, reducing deployment errors by 80%

Junior Python Developer | LTIMindtree | Pune, India | 2021 - 2023
- Built internal workflow automation tools using Flask, reducing manual effort by 15 hours per week
- Developed web scrapers using Scrapy and Beautiful Soup to aggregate competitive intelligence data
- Created RESTful APIs for mobile applications using Django REST Framework
- Maintained and optimized PostgreSQL databases handling 5M+ records

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
PCEP Certified Entry-Level Python Programmer
AWS Developer Associate
Docker Certified Associate

PROJECTS
E-Commerce API Platform - Built a full-featured e-commerce API using Django REST Framework with JWT auth, product catalog, cart, order management, and Stripe payments.
Real-Time Chat Application - Developed a WebSocket-based chat application using FastAPI and React with Redis pub/sub for message distribution.
Automated Web Scraping Pipeline - Built a distributed web scraping system using Scrapy, Celery, and MongoDB that collects and processes 100K+ pages daily.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["Python", "Django", "Flask", "FastAPI", "REST API", "Celery", "Redis", "RabbitMQ", "SQLAlchemy", "PostgreSQL", "MySQL", "MongoDB", "JavaScript", "React", "Docker", "Kubernetes", "Git", "CI/CD", "Linux", "Pytest", "Selenium", "Scrapy", "Pandas", "NumPy", "AWS Lambda", "Nginx", "WebSockets", "GraphQL", "OOP"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Python Developer", "company": "Capgemini", "duration_raw": "2023 - 2026"},
            {"role": "Junior Python Developer", "company": "LTIMindtree", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["PCEP Certified Entry-Level Python Programmer", "AWS Developer Associate", "Docker Certified Associate"],
        "summary": "Versatile Python Developer with 3 years of experience building web applications, automation scripts, APIs, and data pipelines."
    },
    {
        "domain": "Machine Learning Engineer",
        "filename": "sanket_kolhe_ml_engineer.pdf",
        "raw_text": """SANKET KOLHE
Machine Learning Engineer
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Machine Learning Engineer with 3 years of experience developing and deploying production ML models. Strong expertise in deep learning, NLP, computer vision, and MLOps. Proficient in TensorFlow, PyTorch, and Scikit-learn. Experienced in building end-to-end ML pipelines from data collection and feature engineering to model training, evaluation, and deployment.

SKILLS
Python, TensorFlow, PyTorch, Keras, Scikit-learn, XGBoost, LightGBM, Pandas, NumPy, OpenCV, NLTK, SpaCy, Hugging Face Transformers, CNN, RNN, LSTM, GANs, Reinforcement Learning, NLP, Computer Vision, MLflow, Kubeflow, Docker, Kubernetes, AWS SageMaker, GCP Vertex AI, SQL, MongoDB, Apache Spark, Airflow, Feature Engineering, Model Optimization, A/B Testing, Git

EXPERIENCE
Machine Learning Engineer | Accenture | Bangalore, India | 2023 - 2026
- Developed and deployed 10+ production ML models for fraud detection, recommendation, and NLP classification
- Built real-time inference pipelines using TensorFlow Serving and FastAPI serving 500K+ predictions daily
- Fine-tuned transformer models (BERT, RoBERTa) for sentiment analysis achieving 94% accuracy
- Implemented MLOps practices using MLflow and Kubeflow for experiment tracking and model versioning
- Designed feature stores and data pipelines using Apache Spark and Airflow

Junior ML Engineer | Tata Elxsi | Pune, India | 2021 - 2023
- Trained CNN models for image classification and object detection in manufacturing quality control
- Built NLP pipelines for text classification, named entity recognition, and document summarization
- Conducted hyperparameter tuning using Optuna and Bayesian optimization, improving model accuracy by 12%
- Created data labeling workflows and annotation tools for computer vision datasets

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
TensorFlow Developer Certificate
AWS Machine Learning Specialty
Deep Learning Specialization (Coursera)

PROJECTS
Resume Screening System - Built an NLP-based resume screening platform using BERT embeddings and cosine similarity for intelligent candidate-job matching.
Object Detection for Manufacturing - Developed a YOLOv5-based defect detection system achieving 96% mAP on production line imagery.
Recommendation Engine - Built a hybrid recommendation system using collaborative filtering and content-based approaches for an e-commerce platform.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["Python", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "XGBoost", "LightGBM", "Pandas", "NumPy", "OpenCV", "NLTK", "SpaCy", "Hugging Face Transformers", "CNN", "RNN", "LSTM", "NLP", "Computer Vision", "MLflow", "Kubeflow", "Docker", "Kubernetes", "AWS SageMaker", "SQL", "MongoDB", "Apache Spark", "Feature Engineering", "A/B Testing", "Git"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Machine Learning Engineer", "company": "Accenture", "duration_raw": "2023 - 2026"},
            {"role": "Junior ML Engineer", "company": "Tata Elxsi", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["TensorFlow Developer Certificate", "AWS Machine Learning Specialty", "Deep Learning Specialization"],
        "summary": "Machine Learning Engineer with 3 years of experience developing and deploying production ML models. Strong expertise in deep learning, NLP, computer vision, and MLOps."
    },
    {
        "domain": "DevOps Engineer",
        "filename": "sanket_kolhe_devops.pdf",
        "raw_text": """SANKET KOLHE
DevOps Engineer
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
DevOps Engineer with 3 years of experience in building and managing CI/CD pipelines, container orchestration, and infrastructure automation. Expert in Docker, Kubernetes, Terraform, and cloud platforms. Focused on improving deployment velocity, system reliability, and developer productivity through automation and observability.

SKILLS
Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, GitLab CI, ArgoCD, AWS, Azure, GCP, Linux, Bash, Python, Go, Prometheus, Grafana, ELK Stack, Datadog, Nginx, HAProxy, Helm, Istio, Vault, SonarQube, Nexus, Artifactory, Packer, Vagrant, Networking, DNS, SSL/TLS, Infrastructure as Code, Site Reliability Engineering

EXPERIENCE
DevOps Engineer | Persistent Systems | Pune, India | 2023 - 2026
- Built and maintained CI/CD pipelines for 30+ microservices using Jenkins, GitHub Actions, and ArgoCD
- Managed production Kubernetes clusters (EKS, AKS) with 100+ pods and zero-downtime deployments
- Implemented Infrastructure as Code using Terraform managing 200+ AWS resources across 3 environments
- Set up comprehensive observability stack with Prometheus, Grafana, and ELK achieving MTTR under 15 minutes
- Reduced infrastructure costs by 35% through right-sizing, spot instances, and automated scaling policies

Junior DevOps Engineer | Zensar Technologies | Pune, India | 2021 - 2023
- Containerized 20+ legacy Java and Node.js applications using Docker multi-stage builds
- Configured GitLab CI pipelines with automated testing, security scanning, and deployment stages
- Managed Linux servers (Ubuntu, CentOS) across development, staging, and production environments
- Implemented HashiCorp Vault for secrets management across all application environments

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
Certified Kubernetes Administrator (CKA)
AWS Solutions Architect Associate
HashiCorp Certified Terraform Associate
Docker Certified Associate

PROJECTS
GitOps Platform - Implemented a complete GitOps workflow using ArgoCD, Helm, and Kubernetes with automated rollbacks and canary deployments.
Monitoring-as-Code - Built a Terraform module library for deploying Prometheus, Grafana, and alerting rules across multiple Kubernetes clusters.
Self-Service Infrastructure Portal - Developed an internal tool using Python and Flask for developers to provision infrastructure resources via Terraform.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "ArgoCD", "AWS", "Azure", "GCP", "Linux", "Bash", "Python", "Go", "Prometheus", "Grafana", "ELK Stack", "Nginx", "Helm", "Istio", "Vault", "SonarQube", "Infrastructure as Code", "Site Reliability Engineering"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "DevOps Engineer", "company": "Persistent Systems", "duration_raw": "2023 - 2026"},
            {"role": "Junior DevOps Engineer", "company": "Zensar Technologies", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["Certified Kubernetes Administrator", "AWS Solutions Architect Associate", "HashiCorp Certified Terraform Associate", "Docker Certified Associate"],
        "summary": "DevOps Engineer with 3 years of experience in building and managing CI/CD pipelines, container orchestration, and infrastructure automation."
    },
    {
        "domain": "Frontend Developer",
        "filename": "sanket_kolhe_frontend.pdf",
        "raw_text": """SANKET KOLHE
Frontend Developer
Email: sanketkolhe727@gmail.com | Phone: +91-9876543210
Location: Pune, Maharashtra, India
LinkedIn: linkedin.com/in/sanketkolhe | GitHub: github.com/sanketkolhe

PROFESSIONAL SUMMARY
Creative Frontend Developer with 3 years of experience crafting responsive, performant, and accessible web applications. Expert in React, Next.js, and modern CSS frameworks. Passionate about UI/UX design, component-driven architecture, and delivering pixel-perfect interfaces with smooth animations and excellent user experience.

SKILLS
React, Next.js, Angular, Vue.js, JavaScript, TypeScript, HTML5, CSS3, SASS, TailwindCSS, Bootstrap, Material UI, Chakra UI, Redux, Zustand, React Query, Webpack, Vite, Babel, Jest, Cypress, Storybook, Figma, Adobe XD, REST API, GraphQL, WebSockets, PWA, Web Accessibility (WCAG), SEO, Git, Responsive Design, Motion Design, Framer Motion

EXPERIENCE
Frontend Developer | Zensar Technologies | Pune, India | 2023 - 2026
- Built 10+ production React applications with Next.js for SSR/SSG, achieving 95+ Lighthouse performance scores
- Implemented component library using Storybook with 50+ reusable components used across 5 product teams
- Integrated complex data visualizations using D3.js and Chart.js for analytics dashboards
- Improved Core Web Vitals by optimizing bundle sizes, lazy loading, and image optimization, reducing LCP by 40%
- Conducted code reviews focusing on accessibility (WCAG 2.1 AA) and performance best practices

Junior Frontend Developer | Mphasis | Bangalore, India | 2021 - 2023
- Developed responsive web interfaces using React, Redux, and TailwindCSS for fintech applications
- Created interactive prototypes in Figma and translated designs into pixel-perfect React components
- Implemented end-to-end testing using Cypress achieving 85% test coverage
- Built PWA features including service workers, offline support, and push notifications

EDUCATION
Bachelor of Technology in Computer Science | Savitribai Phule Pune University | 2021
CGPA: 8.5/10

CERTIFICATIONS
Meta Front-End Developer Professional Certificate
AWS Certified Cloud Practitioner
Google UX Design Certificate

PROJECTS
Portfolio Website - Built a personal portfolio using Next.js, Framer Motion, and TailwindCSS with dark mode, smooth animations, and CMS integration.
Real-Time Dashboard - Created an analytics dashboard with React, D3.js, and WebSockets displaying live metrics with interactive charts and filters.
Design System - Built a comprehensive design system with 60+ components, theming support, and documentation using Storybook and TypeScript.

LANGUAGES
English, Hindi, Marathi
""",
        "skills": ["React", "Next.js", "Angular", "Vue.js", "JavaScript", "TypeScript", "HTML5", "CSS3", "SASS", "TailwindCSS", "Bootstrap", "Material UI", "Redux", "Webpack", "Vite", "Jest", "Cypress", "Storybook", "Figma", "REST API", "GraphQL", "WebSockets", "PWA", "Web Accessibility", "SEO", "Git", "Responsive Design", "Framer Motion"],
        "education": [{"degree": "Bachelor of Technology", "institution": "Savitribai Phule Pune University", "graduation_year": 2021}],
        "experience": [
            {"role": "Frontend Developer", "company": "Zensar Technologies", "duration_raw": "2023 - 2026"},
            {"role": "Junior Frontend Developer", "company": "Mphasis", "duration_raw": "2021 - 2023"}
        ],
        "total_years": 5.0,
        "certifications": ["Meta Front-End Developer Professional Certificate", "AWS Certified Cloud Practitioner", "Google UX Design Certificate"],
        "summary": "Creative Frontend Developer with 3 years of experience crafting responsive, performant, and accessible web applications. Expert in React, Next.js, and modern CSS frameworks."
    },
]


with app.app_context():
    # Find Sanket's user account
    sanket_user = User.query.filter_by(email="sanketkolhe727@gmail.com").first()
    if not sanket_user:
        sanket_user = User.query.filter(User.username.ilike("%sanket%")).first()
    if not sanket_user:
        # fallback: use first candidate user
        sanket_user = User.query.filter_by(role="candidate").first()

    if not sanket_user:
        print("ERROR: No candidate user found in the database!")
        sys.exit(1)

    print(f"Using user: {sanket_user.username} (ID={sanket_user.id})")

    # Step 1: Delete all resumes EXCEPT Sanket's existing one
    all_resumes = Resume.query.all()
    kept = 0
    deleted = 0
    for r in all_resumes:
        # Keep only Sanket's original uploaded resume
        if r.user_id == sanket_user.id and r.candidate_name and "SANKET" in r.candidate_name.upper():
            kept += 1
            print(f"  KEPT: ID={r.id} Name={r.candidate_name}")
        else:
            # Delete match results first
            MatchResult.query.filter_by(resume_id=r.id).delete()
            if r.candidate_profile:
                db.session.delete(r.candidate_profile)
            db.session.delete(r)
            deleted += 1

    db.session.commit()
    print(f"\nDeleted {deleted} dummy resumes, kept {kept} original Sanket resume(s).")

    # Step 2: Seed multi-domain resumes
    created = 0
    for resume_data in RESUMES:
        # Check if already exists
        existing = Resume.query.filter_by(
            user_id=sanket_user.id,
            original_filename=resume_data["filename"]
        ).first()
        if existing:
            print(f"  SKIP (already exists): {resume_data['filename']}")
            continue

        resume = Resume(
            user_id=sanket_user.id,
            filename=resume_data["filename"],
            original_filename=resume_data["filename"],
            file_type="pdf",
            file_size=len(resume_data["raw_text"]),
            raw_text=resume_data["raw_text"],
            status="analyzed"
        )
        db.session.add(resume)
        db.session.flush()  # Get the resume.id

        profile = CandidateProfile(
            resume_id=resume.id,
            name="Sanket Kolhe",
            email="sanketkolhe727@gmail.com",
            phone="+91-9876543210",
            location="Pune, Maharashtra, India",
            summary=resume_data["summary"],
            total_experience_years=resume_data["total_years"]
        )
        profile.skills_list = resume_data["skills"]
        profile.education_list = resume_data["education"]
        profile.experience_list = resume_data["experience"]
        profile.certifications_list = resume_data["certifications"]
        profile.links_dict = {"linkedin": "linkedin.com/in/sanketkolhe", "github": "github.com/sanketkolhe"}
        profile.languages_list = ["English", "Hindi", "Marathi"]

        db.session.add(profile)
        created += 1
        print(f"  CREATED: {resume_data['domain']} - {resume_data['filename']}")

    db.session.commit()
    print(f"\nDone! Created {created} multi-domain resumes for Sanket Kolhe.")
    print(f"Total resumes in DB: {Resume.query.count()}")
