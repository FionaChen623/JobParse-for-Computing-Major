"""
extractor.py — Keyword-based job description field extractor.

Extracts structured information from raw JD text using
pattern matching and keyword dictionaries. No external
APIs or LLMs required.
"""

import re
from typing import Dict

__all__ = ['extract_fields']

# ── Keyword dictionaries ────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    'Algorithm Engineering': [
        'algorithm', 'recommendation', 'ranking', 'recognition',
        'CV', 'NLP', 'computer vision', 'speech', 'search',
        'deep learning', 'machine learning', 'sorting model',
    ],
    'Data & Analytics': [
        'data analysis', 'data mining', 'data warehouse', 'ETL',
        'data engineering', 'data product', 'data pipeline', 'big data',
        'BI', 'business intelligence', 'analytics',
    ],
    'Software Development': [
        'backend', 'frontend', 'full stack', 'full-stack',
        'software engineer', 'software development', 'architecture',
        'web development', 'mobile development', 'API',
    ],
    'AI / Agent': [
        'agent', 'LLM', 'large language model', 'AI product',
        'prompt', 'RAG', 'AIGC', 'GPT', 'Claude', 'ChatGPT',
    ],
    'Product / Operations': [
        'product manager', 'product owner', 'product operation',
        'user research', 'growth', 'strategy',
    ],
}

LANGUAGES = [
    'Python', 'Java', 'C++', 'C#', 'Go', 'Rust', 'SQL', 'R',
    'MATLAB', 'Scala', 'Kotlin', 'Dart', 'Swift', 'Ruby', 'PHP',
    'TypeScript', 'JavaScript', 'Shell', 'Bash', 'Perl', 'Lua',
]

BIG_DATA_TOOLS = [
    'Spark', 'Flink', 'Hadoop', 'Hive', 'HBase', 'Kafka',
    'ClickHouse', 'Doris', 'Elasticsearch', 'Presto', 'Trino',
    'Airflow', 'Tableau', 'Power BI', 'DataWorks', 'Snowflake',
    'Redshift',
]

ML_FRAMEWORKS = [
    'PyTorch', 'TensorFlow', 'Keras', 'scikit-learn', 'XGBoost',
    'LightGBM', 'CatBoost', 'MindSpore', 'PaddlePaddle', 'ONNX',
    'DeepSpeed', 'Megatron', 'LangChain', 'LlamaIndex',
    'HuggingFace', 'Transformers',
]

WEB_TECH = [
    'React', 'Vue', 'Angular', 'Next.js', 'Nuxt.js',
    'HTML', 'CSS', 'Sass', 'Less', 'Webpack', 'Vite',
    'gRPC', 'GraphQL', 'REST', 'Node.js', 'Express',
    'Flask', 'FastAPI', 'Django', 'Spring Boot',
]

CLOUD_DEVOPS = [
    'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes',
    'K8s', 'Terraform', 'Ansible', 'CI/CD', 'Jenkins',
    'GitHub Actions',
]

AI_CODING_TOOLS = [
    'Claude Code', 'Codex', 'OpenClaw', 'Cursor', 'Windsurf',
    'GitHub Copilot', 'Copilot', 'Cline', 'Aider',
]

SOFT_SKILLS = [
    'communication', 'collaboration', 'teamwork', 'leadership',
    'project management', 'problem solving', 'critical thinking',
    'self-motivated', 'learning', 'ownership', 'innovation',
]

BONUS_JOURNALS_CONFERENCES = [
    'ACL', 'EMNLP', 'NeurIPS', 'KDD', 'ICML', 'CVPR', 'ICCV',
    'ECCV', 'ICLR', 'AAAI', 'IJCAI', 'SIGIR', 'WWW', 'NAACL',
    'COLING', 'PMP', 'CFA', 'CTF', 'Kaggle', 'ACM ICPC',
]

INDUSTRY_KEYWORDS = {
    'Technology': ['tech', 'technology', 'software', 'internet', 'AI'],
    'Finance': ['finance', 'financial', 'bank', 'investment', 'fintech'],
    'FMCG': ['fmcg', 'consumer', 'retail', 'e-commerce'],
    'Healthcare': ['health', 'medical', 'pharma', 'biotech'],
    'Telecom': ['telecom', 'telecommunication', 'network', '5G'],
    'Manufacturing': ['manufacturing', 'industrial', 'hardware', 'factory'],
    'Energy': ['energy', 'oil', 'power', 'renewable', 'solar'],
}


# ── Helpers ─────────────────────────────────────────────────────────────

def _extract_keywords(text: str, keywords: list) -> str:
    """Return comma-separated matched keywords from text."""
    found = []
    for kw in sorted(keywords, key=len, reverse=True):
        if kw.lower() in text.lower() and kw not in found:
            found.append(kw)
    return ','.join(found)


# ── Main extractor ──────────────────────────────────────────────────────

def extract_fields(text: str) -> Dict[str, str]:
    """
    Extract structured fields from raw JD text using keyword/pattern matching.

    Returns a dict matching the COLUMNS schema from database.py.
    """
    text = text.strip()
    if not text:
        return {}

    # Job title: first line
    first_line = text.split('\n')[0].strip()
    # Remove common JD meta markers
    for prefix in ['Job Title:', 'Position:', 'Role:', '职位', '岗位']:
        if first_line.lower().startswith(prefix.lower()):
            first_line = first_line[len(prefix):].strip()
            break

    # Category scoring
    cat_scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                cat_scores[cat] = cat_scores.get(cat, 0) + 1
    auto_cat = max(cat_scores, key=cat_scores.get) if cat_scores else 'Other'

    # Company name: often before a pipe/bar or at the start
    company_match = re.search(
        r'([A-Za-z\u4e00-\u9fa5]+(?:[ \(][^)）]+[\)）])?)',
        text
    )
    auto_company = company_match.group(1).strip() if company_match else ''

    # Location
    loc_match = re.search(
        r'(?:location|city|place)[:\s]*([A-Za-z\u4e00-\u9fa5]+[/\u4e00-\u9fa5A-Za-z]*)',
        text, re.IGNORECASE
    )
    auto_loc = loc_match.group(1) if loc_match else ''

    # Education
    edu_match = re.search(
        r'(PhD|Master|Bachelor|Bachelor\'s|Master\'s|本科|硕士|博士)',
        text
    )
    auto_edu = edu_match.group(1) if edu_match else 'Not specified'

    # Experience
    exp_match = re.search(r'(\d+)[-~–to](\d+)\s*(year|yr)', text, re.IGNORECASE)
    auto_exp = f'{exp_match.group(1)}-{exp_match.group(2)} years' if exp_match else ''
    if not auto_exp:
        exp_match2 = re.search(
            r'(fresh|entry.level|senior|lead|staff|principal|not\.specified|unlimited|\d+\+?\s*(year|yr))',
            text, re.IGNORECASE
        )
        auto_exp = exp_match2.group(1) if exp_match2 else 'Not specified'

    # Skills extraction
    auto_langs = _extract_keywords(text, LANGUAGES)
    auto_bigdata = _extract_keywords(text, BIG_DATA_TOOLS)
    auto_ml = _extract_keywords(text, ML_FRAMEWORKS)
    auto_web = _extract_keywords(text, WEB_TECH)
    auto_cloud = _extract_keywords(text, CLOUD_DEVOPS)
    auto_ai_tools = _extract_keywords(text, AI_CODING_TOOLS)
    auto_soft = _extract_keywords(text, SOFT_SKILLS)
    auto_bonus = _extract_keywords(text, BONUS_JOURNALS_CONFERENCES)

    # Core knowledge: grab sentences after common lead-ins
    knowledge_matches = re.findall(
        r'(?:熟悉|了解|掌握|精通|skilled|proficient|expertise in|experience with)[：:\s]*([^。\n]{5,60})',
        text
    )
    auto_knowledge = ', '.join(k.strip() for k in knowledge_matches) if knowledge_matches else ''

    # Industry
    auto_ind = ''
    for ind, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                auto_ind = ind
                break
        if auto_ind:
            break

    return {
        'job_title': first_line,
        'job_category': auto_cat,
        'company_name': auto_company,
        'company_industry': auto_ind,
        'location': auto_loc,
        'experience_required': auto_exp,
        'education_required': auto_edu,
        'core_knowledge': auto_knowledge,
        'programming_languages': auto_langs,
        'big_data_tools': auto_bigdata,
        'ml_frameworks': auto_ml,
        'web_dev': auto_web,
        'cloud_tools': auto_cloud,
        'ai_coding_tools': auto_ai_tools,
        'soft_skills': auto_soft,
        'bonus_journals': auto_bonus,
        'certificates': '',
        'other_requirements': '',
        'raw_text': text,
    }
