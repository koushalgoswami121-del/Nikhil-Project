from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

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
    return render_template('hub.html', modes=BANK.keys())

@app.route('/start_interview', methods=['POST'])
def start_interview():
    custom = request.form.get('custom_role')
    role = custom if custom else request.form.get('mode')
    if role not in BANK:
        BANK[role] = [{"q": f"Core skills for {role}?", "a": "Expertise."}] * 7
    session['mode'], session['step'], session['history'] = role, 0, [0]*7
    session['active'] = True # Mark interview as active
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

    mode, step = session.get('mode'), session.get('step', 0)
    questions = BANK.get(mode, BANK["Software Engineer"])
    
    if request.method == 'POST':
        action = request.form.get('action')
        v = TfidfVectorizer()
        t = v.fit_transform([questions[step]['a'], request.form.get('ans', '')])
        score = round(float(cosine_similarity(t[0:1], t[1:2])[0][0]) * 100)
        
        hist = session.get('history', [0]*7)
        hist[step] = score
        session['history'] = hist

        if action == "next" or action == "submit":
            if step + 1 >= len(questions):
                session['active'] = False # Kill session after finish
                return redirect(url_for('summary'))
            session['step'] = step + 1
        elif action == "prev" and step > 0:
            session['step'] = step - 1
            
        return redirect(url_for('session_room'))
    return render_template('session_room.html', q=questions[step]['q'], n=step+1, t=len(questions))

@app.route('/terminate')
def terminate():
    session['active'] = False
    flash("Current Interview Session Terminated.")
    return redirect(url_for('hub'))

@app.route('/summary')
def summary():
    h = session.get('history', [])
    avg = round(sum(h) / len(h) if h else 0)
    return render_template('summary.html', avg=avg, rubric=analyze_rubric(h), p_score=random.randint(85,98))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context(): db.create_all()
if __name__ == '__main__': app.run(debug=True, port=8080)