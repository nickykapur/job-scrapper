#!/usr/bin/env python3
"""
Fix misclassified jobs - reclassify based on updated logic
"""

import asyncio
import asyncpg
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

def detect_job_type(title, description=""):
    """Detect job type from title and description - UPDATED LOGIC"""
    text = f"{title} {description}".lower()

    # Cybersecurity keywords (check first - most specific)
    cybersecurity_keywords = [
        'soc analyst', 'cybersecurity', 'cyber security', 'security analyst',
        'information security', 'infosec', 'security operations', 'siem',
        'threat detection', 'incident response', 'security engineer',
        'penetration test', 'ethical hacker', 'security architect',
        'analista soc', 'analista de ciberseguridad', 'seguridad de la información',
        'operaciones de seguridad', 'respuesta a incidentes'
    ]

    # Sales/Business Development keywords (English and Spanish) - EXPANDED
    sales_keywords = [
        # English
        'account manager', 'account executive', 'bdr', 'sdr',
        'business development representative', 'sales development representative',
        'sales representative', 'inside sales', 'outbound sales',
        'saas sales', 'b2b sales', 'customer success manager',
        'account management', 'business development manager',
        'business development', 'sales development', 'sales engineer',
        'sales manager', 'sales associate', 'sales specialist',
        'key account', 'field sales', 'sales consultant',
        # Spanish
        'ejecutivo de ventas', 'gerente de cuenta', 'representante de ventas',
        'desarrollo de negocios', 'ventas', 'ejecutivo comercial',
        'gerente comercial', 'asesor comercial'
    ]

    # Finance/Accounting keywords
    finance_keywords = [
        'fp&a analyst', 'fp&a', 'financial planning and analysis',
        'financial planning analyst', 'financial analyst', 'junior financial analyst',
        'fund accounting', 'fund accountant', 'fund accounting associate',
        'fund administrator', 'investment accounting', 'portfolio accounting',
        'fund operations', 'fund operations analyst', 'fund operations associate',
        'investment operations', 'asset management operations',
        'credit analyst', 'credit risk analyst', 'junior credit analyst',
        'financial reporting', 'management accountant', 'accountant',
        'junior accountant', 'accounting analyst', 'finance associate',
        'finance analyst', 'treasury analyst', 'cash management',
        'corporate finance', 'finance business partner', 'financial reporting analyst',
        'analista financiero', 'contador', 'contabilidad', 'finanzas',
        'analista de crédito', 'tesorería', 'contable', 'analista contable'
    ]

    # HR/Recruitment keywords
    hr_keywords = [
        'hr officer', 'hr coordinator', 'hr generalist', 'hr specialist',
        'talent acquisition', 'recruiter', 'recruitment', 'recruiting',
        'people operations', 'people ops', 'people partner',
        'hr assistant', 'human resources',
        'recursos humanos', 'reclutador', 'reclutamiento', 'selección',
        'talento humano', 'analista de recursos humanos', 'coordinador de rrhh'
    ]

    # Software keywords - NOTE: 'analytics' removed as standalone
    software_keywords = [
        'software', 'developer', 'engineer', 'programming', 'programmer',
        'frontend', 'backend', 'full stack', 'devops', 'react', 'python',
        'javascript', 'node', 'java', 'web developer', 'mobile developer',
        'data scientist', 'data engineer', 'data engineering', 'data analyst',
        'data analytics', 'machine learning', 'ml engineer', 'mlops',
        'business intelligence', 'bi analyst', 'data science', 'big data',
        'data pipeline', 'data warehouse', 'data lake', 'etl', 'elt',
        'analytics engineer', 'quantitative analyst', 'research scientist',
        'applied scientist', 'ai engineer', 'deep learning', 'nlp engineer',
        'desarrollador', 'programador', 'ingeniero de software',
        'científico de datos', 'ingeniero de datos', 'analista de datos'
    ]

    # Check priority order
    for keyword in cybersecurity_keywords:
        if keyword in text:
            return 'cybersecurity'

    for keyword in sales_keywords:
        if keyword in text:
            return 'sales'

    for keyword in finance_keywords:
        if keyword in text:
            return 'finance'

    for keyword in hr_keywords:
        if keyword in text:
            return 'hr'

    for keyword in software_keywords:
        if keyword in text:
            return 'software'

    return 'other'

async def fix_job_classifications():
    """Reclassify all jobs based on updated logic"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return

    print("🔧 Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Get all jobs
        jobs = await conn.fetch("""
            SELECT id, title, description, job_type
            FROM jobs
            WHERE job_type IS NOT NULL
        """)

        print(f"📊 Found {len(jobs)} jobs to check")

        fixed_count = 0
        changes = {}

        for job in jobs:
            job_id = job['id']
            title = job['title'] or ''
            description = job['description'] or ''
            old_type = job['job_type']

            # Detect new job type
            new_type = detect_job_type(title, description)

            # If changed, update it
            if new_type != old_type:
                await conn.execute("""
                    UPDATE jobs
                    SET job_type = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                """, new_type, job_id)

                fixed_count += 1
                change_key = f"{old_type} → {new_type}"
                if change_key not in changes:
                    changes[change_key] = []
                changes[change_key].append(title[:70])

        print(f"\n✅ Reclassified {fixed_count} jobs!")

        if changes:
            print("\n📊 Changes summary:")
            for change_key, titles in changes.items():
                print(f"\n{change_key}: {len(titles)} jobs")
                for i, title in enumerate(titles[:5], 1):
                    print(f"  {i}. {title}")
                if len(titles) > 5:
                    print(f"  ... and {len(titles) - 5} more")

        # Show new distribution
        print("\n📊 New job type distribution:")
        distribution = await conn.fetch("""
            SELECT job_type, COUNT(*) as count
            FROM jobs
            GROUP BY job_type
            ORDER BY count DESC
        """)
        for row in distribution:
            print(f"   {row['job_type']}: {row['count']} jobs")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_job_classifications())
