import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from numpy import exp
from .models import Resume
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .utils import extract_text_from_pdf, extract_email, extract_skills
from .utils import normalize_skills
from .utils import get_skill_suggestions
from django.shortcuts import get_object_or_404, redirect

SKILL_WEIGHTS = {
    "python": 3,
    "django": 3,
    "sql": 2,
    "rest": 2,
    "api": 2,
    "html": 1,
    "css": 1,
    "javascript": 1,
}
COMMON_SKILLS = [
    'python', 'django', 'sql', 'html', 'css', 'javascript',
    'react', 'java', 'c', 'c++', 'machine learning', 'ai',
    'data analysis', 'rest', 'api'
]
# Helper to get match reason
def get_match_reason(score):
    if score >= 70:
        return "Strong fit for the role"
    elif score >= 40:
        return "Partial match — some skills are missing"
    else:
        return "Low match — lacks many required skills"

'''def normalize_skills(skills):
    SKILL_ALIASES = {
        'js': 'javascript',
        'nodejs': 'node.js',
        'py': 'python',
        'webdev': 'web development',
        'webdevelopment': 'web development',
        'frontend': 'front-end',
        'backend': 'back-end',
        'reactjs': 'react',
        'restapi': 'rest api',
        'api': 'api',
        'ML': 'machine learning',
        'AI': 'artificial intelligence',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'gitHub': 'github',
        'github': 'github',
        'git': 'git',
        'c++': 'cpp',
        'C++':'cpp',
        'c':'C',
    }

    normalized = set()

    for skill in skills:
        skill = skill.strip().lower()
        if not skill:
            continue
        normalized.add(SKILL_ALIASES.get(skill, skill))

    return list(normalized) '''

@login_required
def dashboard(request):
    min_score = int(request.GET.get('min_score', 0))
    resumes = Resume.objects.all()
    jd = request.GET.get('jd', '').strip()

    search_skills = []
    results = []

    if jd:
        # Extract JD skills
        search_skills = normalize_skills(jd.split(','))

        for resume in resumes:
            resume_skills = normalize_skills(resume.skills.split(','))

            matched_skills = list(set(resume_skills) & set(search_skills))
            missing_skills = list(set(search_skills) - set(resume_skills))

            # Percentage-based ATS score
            CORE_SKILLS = ['python', 'django']
            SECONDARY_SKILLS = ['sql']
            BONUS_SKILLS = ['rest', 'api', 'git', 'docker']

            raw_score = 0
            missing_core=False
            for skill in matched_skills:
                if skill in CORE_SKILLS:
                    raw_score += 30
                elif skill in SECONDARY_SKILLS:
                    raw_score += 20
                elif skill in BONUS_SKILLS:
                    raw_score += 10
# Experience bonus
            exp = resume.experience_years
            if exp >= 5:
                raw_score += 30
            elif exp >= 3:
                raw_score += 20
            elif exp >= 1:
                raw_score += 10
            score = min(round(raw_score), 100)
            for skill in missing_skills:
              if skill in CORE_SKILLS:
               missing_core = True

              if missing_core:
               score = min(score, 70)   # hard cap if core skill missing
              elif missing_skills:
                score = min(score, 90)   # soft cap if only non-core missing

            results.append({
                'resume': resume,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'score': score,
                'match_reason': get_match_reason(score),
                'suggestions': get_skill_suggestions(missing_skills)
            })

    else:
        # No JD provided
        for resume in resumes:
            results.append({
                'resume': resume,
                'matched_skills': [],
                'missing_skills': [],
                'score': 0,
                'match_reason': 'No JD provided'
            })

    # ✅ Filter by minimum score
    results = [r for r in results if r['score'] >= min_score]

    # ✅ Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)

    # ✅ Add rank badges
    for index, item in enumerate(results):
        if index == 0:
            item['rank'] = '🥇 Top Match'
        elif index == 1:
            item['rank'] = '🥈 Strong Match'
        elif index == 2:
            item['rank'] = '🥉 Good Match'
        else:
            item['rank'] = ''

    context = {
        'results': results,
        'jd': jd,
        'min_score': min_score
    }

    return render(request, 'core/resume_dashboard.html', context)

 
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    
    if request.method == "POST":
        resume.delete()
    
    return redirect('dashboard')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ats_results.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Score', 'Matched Skills', 'Missing Skills'])

    resumes = Resume.objects.all()

    for resume in resumes:
        writer.writerow([
            resume.candidate_name,
            resume.email,
            '',
            resume.skills,
            ''
        ])

    return response

@login_required
def resume_upload(request):
    if request.method == "POST":
        pdf_file = request.FILES['resume']

        text = extract_text_from_pdf(pdf_file)
        skills = extract_skills(text)

        Resume.objects.create(
            candidate_name=request.POST['candidate_name'],
            email=request.POST['email'],
            experience_years=request.POST['experience_years'],
            skills=", ".join(skills)
        )

    return render(request, 'core/resume_upload.html')

def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'User already exists'})

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def resume_upload(request):
    if request.method == "POST":
        pdf_file = request.FILES['resume']

        text = extract_text_from_pdf(pdf_file)
        skills = extract_skills(text)

        Resume.objects.create(
            user=request.user,
            candidate_name=request.POST['candidate_name'],
            email=request.POST['email'],
            experience_years=request.POST['experience_years'],
            skills=", ".join(skills)
        )

    return render(request, 'core/resume_upload.html')

def calculate_score(candidate_skills, job_skills):
    candidate = [s.strip().lower() for s in candidate_skills.split(',')]
    job = [s.strip().lower() for s in job_skills.split(',')]

    total_weight = 0
    matched_weight = 0

    for skill in job:
        weight = SKILL_WEIGHTS.get(skill, 1)
        total_weight += weight
        if skill in candidate:
            matched_weight += weight

    if total_weight == 0:
        return 0

    return round((matched_weight / total_weight) * 100, 2)

def get_match_reason(score):
    if score >= 70:
        return "Strong fit for the role"
    elif score >= 40:
        return "Partial match — some skills are missing"
    else:
        return "Low match — lacks many required skills"