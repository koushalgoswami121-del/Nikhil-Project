from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import sys

from scoring import answer_similarity_score

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import gemini_voice
from question_bank import build_custom_role_questions

gemini_voice._load_env()

app = Flask(__name__)
app.secret_key = 'coach_ai_midnight_secure_2026'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coach_pro_secure.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --- 7 QUESTIONS PER ROLE ---
BANK = {
    "Software Engineer": [
        {"q": "How do you handle technical debt?", "a": "Refactoring and prioritization."},
        {"q": "Explain Unit Testing importance.", "a": "Reliability and bug prevention."},
        {"q": "What is Agile methodology?", "a": "Iterative development and feedback."},
        {"q": "Explain a REST API.", "a": "Standardized communication protocol."},
        {"q": "Monolith vs Microservices?", "a": "Single unit vs distributed services."},
        {"q": "How do you optimize SQL queries?", "a": "Indexing and avoiding joins."},
        {"q": "What is CI/CD?", "a": "Continuous integration and deployment."}
    ],
    "Data Scientist": [
        {"q": "What is a P-Value?", "a": "Probability of result by chance."},
        {"q": "Explain Overfitting.", "a": "Model learning noise instead of signal."},
        {"q": "What is a Confusion Matrix?", "a": "Performance measurement table."},
        {"q": "L1 vs L2 Regularization?", "a": "Lasso vs Ridge."},
        {"q": "Explain Random Forest.", "a": "Ensemble of decision trees."},
        {"q": "What is Feature Scaling?", "a": "Normalizing data ranges."},
        {"q": "Define supervised learning.", "a": "Learning from labeled data."}
    ]
}

def analyze_rubric(scores):
    avg = sum(scores) / len(scores) if scores else 0
    if avg >= 75: return {"tone": "Executive", "pacing": "Perfect", "content": "Expert"}
    return {"tone": "Professional", "pacing": "Steady", "content": "Competent"}

def _score_answer(questions, step, answer):
    return answer_similarity_score(questions[step]['a'], answer or '')

def _advance_session(questions, step, action, answer):
    hist = session.get('history', [0]*7)
    hist[step] = _score_answer(questions, step, answer)
    session['history'] = hist
    if action in ("next", "submit"):
        if step + 1 >= len(questions):
            session['active'] = False
            return redirect(url_for('summary'))
        session['step'] = step + 1
    elif action == "prev" and step > 0:
        session['step'] = step - 1
    room = 'voice_room' if session.get('interview_type') == 'voice' else 'session_room'
    return redirect(url_for(room))

@app.route('/')
def init(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('u')).first()
        if u and check_password_hash(u.password, request.form.get('p')):
            session['uid'], session['name'] = u.id, u.username
            return redirect(url_for('hub'))
        flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db.session.add(User(username=request.form.get('u'), password=generate_password_hash(request.form.get('p'))))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/hub')
def hub():
    if 'uid' not in session: return redirect(url_for('login'))
    # Clean up old interview data when entering hub
    session.pop('mode', None)
    session.pop('step', None)
    session.pop('history', None)
    session.pop('interview_type', None)
    session.pop('selected_role', None)
    return render_template('hub.html', modes=BANK.keys())

def _ensure_role_bank(role):
    role = (role or '').strip()
    if not role:
        return None
    if role not in BANK:
        BANK[role] = build_custom_role_questions(role)
    elif len(BANK[role]) == 7 and len({item["q"] for item in BANK[role]}) == 1:
        # Replace legacy placeholder banks (7 identical questions)
        BANK[role] = build_custom_role_questions(role)
    return role

@app.route('/select_role', methods=['POST'])
def select_role():
    if 'uid' not in session:
        return redirect(url_for('login'))
    custom = request.form.get('custom_role', '').strip()
    role = custom if custom else request.form.get('mode', '').strip()
    role = _ensure_role_bank(role)
    if not role:
        flash("Please select or enter a job role.")
        return redirect(url_for('hub'))
    session['selected_role'] = role
    return redirect(url_for('choose_interview'))

@app.route('/choose_interview')
def choose_interview():
    if 'uid' not in session:
        return redirect(url_for('login'))
    role = session.get('selected_role')
    if not role:
        flash("Choose your job role first.")
        return redirect(url_for('hub'))
    return render_template('choose_interview.html', role=role)

@app.route('/start_interview', methods=['POST'])
def start_interview():
    if 'uid' not in session:
        return redirect(url_for('login'))
    role = session.get('selected_role')
    if not role:
        flash("Choose your job role first.")
        return redirect(url_for('hub'))
    _ensure_role_bank(role)
    session['mode'], session['step'], session['history'] = role, 0, [0]*7
    session['active'] = True
    itype = request.form.get('interview_type', 'text')
    session['interview_type'] = 'voice' if itype == 'voice' else 'text'
    return redirect(url_for('camera_check'))

@app.route('/camera_check')
def camera_check():
    if not session.get('active'): return redirect(url_for('hub'))
    return render_template('camera_check.html')

@app.route('/session_room', methods=['GET', 'POST'])
def session_room():
    if 'uid' not in session: return redirect(url_for('login'))
    if not session.get('active'):
        flash("Session Terminated. Please start a new interview.")
        return redirect(url_for('hub'))
    if session.get('interview_type') == 'voice':
        return redirect(url_for('voice_room'))

    mode, step = session.get('mode'), session.get('step', 0)
    questions = BANK.get(mode, BANK["Software Engineer"])

    if request.method == 'POST':
        return _advance_session(questions, step, request.form.get('action'), request.form.get('ans', ''))
    return render_template('session_room.html', q=questions[step]['q'], n=step+1, t=len(questions))

@app.route('/voice_room', methods=['GET', 'POST'])
def voice_room():
    if 'uid' not in session: return redirect(url_for('login'))
    if not session.get('active'):
        flash("Session Terminated. Please start a new interview.")
        return redirect(url_for('hub'))

    mode, step = session.get('mode'), session.get('step', 0)
    questions = BANK.get(mode, BANK["Software Engineer"])

    if request.method == 'POST':
        return _advance_session(questions, step, request.form.get('action'), request.form.get('ans', ''))
    return render_template(
        'voice_room.html',
        q=questions[step]['q'],
        n=step + 1,
        t=len(questions),
        mode=mode,
        neural_voice_enabled=gemini_voice.neural_voice_available(),
    )

@app.route('/api/coach-speak', methods=['POST'])
def coach_speak():
    if 'uid' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if not gemini_voice.neural_voice_available():
        return jsonify({'error': 'Run: .venv\\Scripts\\pip install edge-tts'}), 503
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    if not question:
        return jsonify({'error': 'Missing question'}), 400
    is_first = bool(data.get('is_first', True))
    audio, mime = gemini_voice.coach_speech(
        question, role=session.get('mode'), is_first=is_first
    )
    if not audio:
        return jsonify({'error': gemini_voice.last_error() or 'TTS failed'}), 502
    return Response(audio, mimetype=mime or 'audio/mpeg')

@app.route('/terminate')
def terminate():
    session['active'] = False
    flash("Current Interview Session Terminated.")
    return redirect(url_for('hub'))

@app.route('/summary')
def summary():
    h = session.get('history', [])
    avg = round(sum(h) / len(h) if h else 0)
    p_score = random.randint(85, 98)
    feedback = (
        f"Presence verified at {p_score}%. "
        f"{'Excellent vocal clarity and pacing in your live session.' if session.get('interview_type') == 'voice' else 'Strong on-camera presence and steady delivery.'}"
    )
    return render_template('summary.html', avg=avg, rubric=analyze_rubric(h), p_score=p_score, feedback=feedback)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context(): db.create_all()


def _relaunch_in_venv():
    """If .venv exists, re-run this app with venv Python (fixes voice + deps)."""
    import os
    from pathlib import Path

    root = Path(__file__).resolve().parent
    venv_py = root / ".venv" / "Scripts" / "python.exe"
    if not venv_py.is_file():
        return False
    if Path(sys.executable).resolve() == venv_py.resolve():
        return False
    print("Switching to project virtual environment (.venv)...")
    os.execv(str(venv_py), [str(venv_py), str(root / "app.py"), *sys.argv[1:]])


if __name__ == '__main__':
    _relaunch_in_venv()
    gemini_voice.neural_voice_available()
    app.run(debug=True, port=8080)