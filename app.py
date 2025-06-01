from flask import Flask, render_template, flash, redirect, url_for, request
from forms import Reg_form, Login_form
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iwhebihewbcwhbihcebiwhi879834918292918942812948'

def get_db_connection():
    conn = sqlite3.connect("polls.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER,
                option_text TEXT,
                votes INTEGER DEFAULT 0,
                FOREIGN KEY (poll_id) REFERENCES polls(id)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("SQLite database initialized successfully!")
    except Exception as e:
        print(f"Error initializing SQLite database: {e}")

def execute_query(query, params=None, fetch=False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if fetch == 'one':
            result = cursor.fetchone()
            if result:
                result = tuple(result)
        elif fetch == 'all':
            result = cursor.fetchall()
            if result:
                result = [tuple(row) for row in result]
        else:
            result = None
        conn.commit()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return None

post = [
    {
        'title': 'Math Timed Quiz',
        'content': 'A Simple quiz which checks how fast u can do simple addition/subtraction/multiplication problems. We have multiple difficulty modes',
        'date_posted': 'May 29, 2025',
        'link': '/quiz'
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
    polls = execute_query("SELECT * FROM polls ORDER BY id DESC", fetch='all')
    if polls is None:
        polls = []
        flash('Error loading polls', 'danger')
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
        try:
            execute_query("INSERT INTO polls (question) VALUES (?)", (question,))
            # Get the last inserted poll ID
            result = execute_query("SELECT last_insert_rowid()", fetch='one')
            if result:
                poll_id = result[0]
                for text in valid_options:
                    execute_query("INSERT INTO options (poll_id, option_text) VALUES (?, ?)", (poll_id, text))
            flash('Poll created successfully!', 'success')
            return redirect(url_for('polls_index'))
        except Exception as e:
            flash(f'Error creating poll: {str(e)}', 'danger')
            return redirect(url_for('create_poll'))
    return render_template('polls/create.html', title="Create Poll")

@app.route('/polls/<int:poll_id>')
def view_poll(poll_id):
    question_result = execute_query("SELECT question FROM polls WHERE id=?", (poll_id,), fetch='one')
    options = execute_query("SELECT id, option_text FROM options WHERE poll_id=?", (poll_id,), fetch='all')
    if not question_result:
        flash('Poll not found.', 'danger')
        return redirect(url_for('polls_index'))
    question = question_result[0]
    if options is None:
        options = []
    return render_template('polls/poll.html', poll_id=poll_id, question=question, options=options, title=f"Poll: {question}")

@app.route('/polls/vote/<int:option_id>', methods=['POST'])
def vote(option_id):
    selected_option_id = request.form.get('option_id', type=int)
    if selected_option_id:
        option_id = selected_option_id
    try:
        execute_query("UPDATE options SET votes = votes + 1 WHERE id=?", (option_id,))
        result = execute_query("SELECT poll_id FROM options WHERE id=?", (option_id,), fetch='one')
        if not result:
            flash('Invalid vote.', 'danger')
            return redirect(url_for('polls_index'))
        poll_id = result[0]
        flash('Your vote has been recorded!', 'success')
        return redirect(url_for('poll_results', poll_id=poll_id))
    except Exception as e:
        flash(f'Error recording vote: {str(e)}', 'danger')
        return redirect(url_for('polls_index'))

@app.route('/polls/results/<int:poll_id>')
def poll_results(poll_id):
    question_result = execute_query("SELECT question FROM polls WHERE id=?", (poll_id,), fetch='one')
    options = execute_query("SELECT option_text, votes FROM options WHERE poll_id=? ORDER BY votes DESC", (poll_id,), fetch='all')
    if not question_result:
        flash('Poll not found.', 'danger')
        return redirect(url_for('polls_index'))
    question = question_result[0]
    if options is None:
        options = []
    return render_template('polls/results.html', question=question, options=options, poll_id=poll_id, title=f"Results: {question}")

# Initialize database when app starts
init_db()

if __name__ == '__main__':
    app.run(debug=True)