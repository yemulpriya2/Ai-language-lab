# AI Language Lab (Django)

A structured language-learning website built with Python, Django, HTML, and CSS.

## Features
- Step-by-step lessons for each language
- Expanded language catalog (Spanish, French, German, Italian, Portuguese, Japanese, Korean, Hindi, Tamil, Chinese)
- 7 structured steps per language from beginner to advanced
- Quiz after each lesson
- Performance tracker with completion and accuracy
- Automatic level classification by performance
- AI-style fun coach that gives playful missions and growth hints
- User authentication (signup/login/logout)
- Account-linked profiles per language
- Real AI tutor backend integration with safe local fallback
- Badge unlock system by performance milestones
- Speaker and Master certificate generation page

## Tech
- Python
- Django
- HTML templates
- CSS styling

## Run Locally
1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Run migrations:
   python manage.py migrate
4. Start the server:
   python manage.py runserver
5. Open:
   http://127.0.0.1:8000/

## Real AI Tutor Setup (Optional)
Set environment variables before starting the server:

- OPENAI_API_KEY=your_api_key
- OPENAI_MODEL=gpt-4o-mini
- OPENAI_BASE_URL=https://api.openai.com/v1/chat/completions

If no key is provided, the app uses a local fallback tutor response engine.

## Optional Admin
- Create admin user:
  python manage.py createsuperuser
- Visit:
  http://127.0.0.1:8000/admin/
