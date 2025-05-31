from flask import Flask, render_template, flash, redirect, url_for, request
from forms import Reg_form, Login_form
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iwhebihewbcwhbihcebiwhi879834918292918942812948'

def init_db():
    with sqlite3.connect("polls.db") as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER,
                option_text TEXT,
                votes INTEGER DEFAULT 0,
                FOREIGN KEY (poll_id) REFERENCES polls(id)
            )
        """)

post = [
    {
        'title': 'Math Timed Quiz',
        'content': 'A Simple quiz which checks how fast u can do simple addition/subtraction/multiplication problems. We have multiple difficulty modes',
        'date_posted': 'May 29, 2025',
        'link': '/quiz'  # Future link for math quiz
    },
    {
        'title': 'Polling System',
        'content': 'A Polling system for mass polls and live-results.',
        'date_posted': 'Available Now',
        'link': '/polls'
    }
]

# Main app routes
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home", posts=post)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = Reg_form()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", form=form, title="Register")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login_form()
    return render_template("login.html", form=form, title="Login")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

# Polling system routes
@app.route('/polls')
def polls_index():
    with sqlite3.connect("polls.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM polls ORDER BY id DESC")
        polls = c.fetchall()
    return render_template('polls/index.html', polls=polls, title="Polls")

@app.route('/polls/create', methods=['GET', 'POST'])
def create_poll():
    if request.method == 'POST':
        question = request.form['question']
        option_texts = request.form.getlist('options')
        
        # Filter out empty options
        valid_options = [text.strip() for text in option_texts if text.strip()]
        
        if len(valid_options) < 2:
            flash('Please provide at least 2 options for your poll.', 'danger')
            return redirect(url_for('create_poll'))
            
        with sqlite3.connect("polls.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO polls (question) VALUES (?)", (question,))
            poll_id = c.lastrowid
            for text in valid_options:
                c.execute("INSERT INTO options (poll_id, option_text) VALUES (?, ?)", (poll_id, text))
            conn.commit()
        
        flash('Poll created successfully!', 'success')
        return redirect(url_for('polls_index'))
    return render_template('polls/create.html', title="Create Poll")

@app.route('/polls/<int:poll_id>')
def view_poll(poll_id):
    with sqlite3.connect("polls.db") as conn:
        c = conn.cursor()
        c.execute("SELECT question FROM polls WHERE id=?", (poll_id,))
        result = c.fetchone()
        if not result:
            flash('Poll not found.', 'danger')
            return redirect(url_for('polls_index'))
        question = result[0]
        c.execute("SELECT id, option_text FROM options WHERE poll_id=?", (poll_id,))
        options = c.fetchall()
    return render_template('polls/poll.html', poll_id=poll_id, question=question, options=options, title=f"Poll: {question}")

@app.route('/polls/vote/<int:option_id>', methods=['POST'])
def vote(option_id):
    # Get the selected option from the form
    selected_option_id = request.form.get('option_id', type=int)
    
    # Use the selected option ID from form, not URL parameter
    if selected_option_id:
        option_id = selected_option_id
    
    with sqlite3.connect("polls.db") as conn:
        c = conn.cursor()
        # Update votes for the correct option
        c.execute("UPDATE options SET votes = votes + 1 WHERE id=?", (option_id,))
        conn.commit()
        # Get poll_id for redirect
        c.execute("SELECT poll_id FROM options WHERE id=?", (option_id,))
        result = c.fetchone()
        if not result:
            flash('Invalid vote.', 'danger')
            return redirect(url_for('polls_index'))
        poll_id = result[0]
    
    flash('Your vote has been recorded!', 'success')
    return redirect(url_for('poll_results', poll_id=poll_id))

@app.route('/polls/results/<int:poll_id>')
def poll_results(poll_id):
    with sqlite3.connect("polls.db") as conn:
        c = conn.cursor()
        c.execute("SELECT question FROM polls WHERE id=?", (poll_id,))
        result = c.fetchone()
        if not result:
            flash('Poll not found.', 'danger')
            return redirect(url_for('polls_index'))
        question = result[0]
        c.execute("SELECT option_text, votes FROM options WHERE poll_id=? ORDER BY votes DESC", (poll_id,))
        options = c.fetchall()
    return render_template('polls/results.html', question=question, options=options, poll_id=poll_id, title=f"Results: {question}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)