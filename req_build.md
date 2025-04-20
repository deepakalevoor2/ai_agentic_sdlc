Resume ATS Score Checker Project
Build an multi agent design using your Crew AI and FAST API for Resume ATS Scorer project. 
The idea is build MVP with following components

The core components we want build:
Resume Parser: Extract text from uploaded resume files (PDF, DOCX, HTML)
Resume Keyword Analyst: Extract keywords from uploaded resume
Job Description Parser: Extract key requirements from job postings(Naukri, LinkedIn etc)
For parsing explore usage of library like unstructured, docling
Matching Algorithm: Compare resume content against job requirements
Scoring System: Generate a numeric score based on keyword matching and formatting analysis

Multi-Dimensional Scoring Approach
The scoring system(TOTAL SCORE = 100) uses a multi-dimensional approach that evaluates:
Content Match: How well the resume content matches job requirements
Format Compatibility: How well the resume format works with ATS systems
Section-Specific Scores: Targeted scores for key resume sections
Combined Overall Score: A weighted combination of all dimensions
Create a document explaining the scoring mechanism with examples.
Recommendation Engine: Suggest improvements & feedback to increase ATS compatibility

Agent Frameworks
Use CrewAI version = 0.114 and Pydantic V2 = 2.11
Coding Rules
Project Rules:-
- Add Docker File also
- Use Python 3.12
- Add the requiremnts.txt file also
- Add proper Logging Module for Log Tracing
- Follow all pep8 rules of Python
- Follow Modular Coding approaches
- Build scalalbe Restful APIs using FASTAPI
- Create a PYPI python package
- Dockerize the app & upload image in DockerHub public Repo