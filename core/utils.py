import pdfplumber
import re

SKILL_RECOMMENDATIONS = {
    "python": "Strengthen core Python concepts such as data structures, OOP, and libraries.",
    "django": "Build more Django projects focusing on authentication, ORM, and REST APIs.",
    "sql": "Practice SQL queries including joins, subqueries, and database design.",
    "rest": "Gain experience designing and consuming RESTful APIs.",
    "docker": "Learn Docker fundamentals including containerization and deployment workflows.",
    "git": "Improve version control skills using Git and GitHub workflows."
}

SKILL_SYNONYMS = {
    "python": ["python"],
    "django": ["django", "django framework"],
    "sql": ["sql", "mysql", "postgresql", "sqlite"],
    "rest": ["rest", "rest api", "api"],
    "docker": ["docker", "docker container", "containerization"],
    "git": ["git", "github"],
}
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""


def extract_skills(text):
    SKILL_SET = [
        'python', 'django', 'flask', 'sql', 'mysql',
        'javascript', 'html', 'css', 'react',
        'git', 'api', 'rest', 'machine learning'
    ]

    text = text.lower()
    found_skills = [skill for skill in SKILL_SET if skill in text]
    return list(set(found_skills))

def normalize_skills(skills_list):
    normalized = set()

    for skill in skills_list:
        skill = skill.strip().lower()

        for key, synonyms in SKILL_SYNONYMS.items():
            if skill in synonyms:
                normalized.add(key)

    return list(normalized)


def get_skill_suggestions(missing_skills):
    suggestions = []
    for skill in missing_skills:
        if skill in SKILL_RECOMMENDATIONS:
            suggestions.append(SKILL_RECOMMENDATIONS[skill])
    return suggestions