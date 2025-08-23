#!/usr/bin/env python3
"""
Simple test of job filtering logic based on your CV
"""

def test_job_filtering_simple():
    """Test job filtering logic manually"""
    
    # Your CV skills
    software_keywords = [
        # Core programming roles
        'software', 'developer', 'engineer', 'programming', 'programmer', 
        'development', 'coding', 'technical',
        
        # Languages you know: Python, R, Javascript, HTML, Typescript, C++, Java
        'python', 'java', 'javascript', 'typescript', 'c++', 'html', 'css',
        
        # Frameworks you use: React, Angular, Express, NodeJS
        'react', 'angular', 'vue', 'node', 'nodejs', 'express', 'frontend', 'backend',
        'full stack', 'fullstack', 'full-stack',
        
        # Cloud platforms you know: AWS, Firebase, Azure
        'cloud', 'aws', 'azure', 'firebase', 'lambda', 'devops', 'infrastructure',
        
        # Data skills: Data Science, Machine Learning, Analytics
        'data', 'analytics', 'machine learning', 'ai', 'artificial intelligence',
        'data science', 'data engineer', 'tableau', 'visualization',
        
        # Database: SQL, NoSQL
        'database', 'sql', 'nosql', 'mysql', 'mongodb', 'oracle',
        
        # Mobile development: React Native mentioned in CV
        'mobile', 'react native', 'ios', 'android',
        
        # Leadership roles you've held: Technical Lead
        'technical lead', 'tech lead', 'lead developer', 'senior', 'principal',
        'architect', 'staff engineer', 'team lead',
        
        # Testing experience from CV
        'qa', 'quality assurance', 'test', 'testing', 'automation',
        
        # Other tech roles
        'web developer', 'api', 'microservices', 'integration', 'platform',
        'system', 'application', 'solution', 'product engineer'
    ]
    
    # Special handling for borderline cases
    borderline_positive = [
        'marketing tools', 'finance automation', 'revenue', 'compiler', 
        'infrastructure', 'operations', 'integration', 'reliability',
        'workday', 'salesforce', 'data operations'
    ]
    
    # Jobs that were being rejected
    test_jobs = [
        "Software Engineer, Java - Marketing Tools",
        "Full Stack Engineer, Revenue and Finance Automation", 
        "Senior Software Engineer - Java, Marketing Tools",
        "Scientist – Compiler Infrastructure",
        "Integration Reliability Engineer, Technical Operations",
        "Data Operations Engineer",
        "Salesforce Developer – nCino",
        "Lead Developer - Salesforce /nCino",
        "Principal Research Scientist",
        "Workday Intern Cohort 2025"
    ]
    
    print("🧪 Testing Job Filtering Against Your CV")
    print("=" * 60)
    
    for job_title in test_jobs:
        title_lower = job_title.lower()
        
        # Check for software keywords
        has_software = any(keyword in title_lower for keyword in software_keywords)
        
        # Check for borderline positive terms
        has_borderline = any(positive in title_lower for positive in borderline_positive)
        
        should_include = has_software or has_borderline
        
        status = "✅ SHOULD INCLUDE" if should_include else "❌ SHOULD EXCLUDE"
        
        print(f"\n{status}: {job_title}")
        
        if has_software:
            matching_keywords = [kw for kw in software_keywords if kw in title_lower]
            print(f"   📍 Software keywords found: {matching_keywords[:3]}...")
        
        if has_borderline:
            matching_borderline = [bp for bp in borderline_positive if bp in title_lower]
            print(f"   📍 Borderline positive found: {matching_borderline}")
        
        if not should_include:
            print(f"   ⚠️ This job might be wrongly excluded!")

if __name__ == "__main__":
    test_job_filtering_simple()