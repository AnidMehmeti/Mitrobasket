from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv







app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/mitrobasket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

class Player(db.Model):
    __tablename__ = 'players'

    numri_lojtarit = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emri = db.Column(db.String(25), nullable=False)
    emri_prindit = db.Column(db.String(25), nullable=True)
    mbiemri = db.Column(db.String(25), nullable=False)
    mosha = db.Column(db.Integer, nullable=False)
    data_regjistrimit = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    numri_telefonit = db.Column(db.String(20), nullable=False)
    orari_grupit = db.Column(db.String(10), nullable=False)

def calculate_orari(mosha):
    if 6 <= mosha <= 7:
        return "10:00-11:00"
    elif 8 <= mosha <= 9:
        return "11:00-12:00"
    elif 10 <= mosha <= 11:
        return "12:00-13:00"
    elif 12 <= mosha <= 13:
        return "13:00-14:00"
    elif 14 <= mosha:
        return "14:00-15:00"
    else:
        return ""

class Coach(db.Model):
    __tablename__ = 'coaches'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    emri = request.form.get('full_name')
    emri_prindit = request.form.get('parent_name')
    mbiemri = request.form.get('last_name')
    mosha = request.form.get('age')
    numri_telefonit = request.form.get('telephone_number')

    if not (emri and mbiemri and mosha and numri_telefonit):
        return "Missing required fields", 400

    try:
        mosha = int(mosha)
    except ValueError:
        return "Invalid age", 400

    # DUPLICATE CHECK
    existing_player = Player.query.filter_by(
        emri=emri,
        mbiemri=mbiemri,
        numri_telefonit=numri_telefonit
    ).first()

    if existing_player:
        error_message = "Ky lojtar është regjistruar më parë!"
        return render_template('index.html', error=error_message)


    orari = calculate_orari(mosha)

    player = Player(
        emri=emri,
        emri_prindit=emri_prindit,
        mbiemri=mbiemri,
        mosha=mosha,
        numri_telefonit=numri_telefonit,
        orari_grupit=orari
    )
    db.session.add(player)
    db.session.commit()

    return render_template('confirmation.html', emri=emri, orari=orari)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Initialize failed attempts
        if 'login_attempts' not in session:
            session['login_attempts'] = 0

        coach = Coach.query.filter_by(username=username).first()

        if coach and coach.check_password(password):
            session['coach_logged_in'] = True
            session['login_attempts'] = 0  # Reset attempts on success
            return redirect(url_for("coach_view"))
        else:
            session['login_attempts'] += 1
            flash("Passwordi është gabim", "error")

            if session['login_attempts'] >= 2:
                flash("Shumë tentativa të pasuksesshme. Po ju kthejmë në faqen kryesore.", "error")
                session['login_attempts'] = 0
                return redirect(url_for("home"))

    return render_template("login.html")



from datetime import datetime, timedelta

@app.route("/coach")
def coach_view():
    if not session.get("coach_logged_in"):
        return redirect(url_for("login"))

    all_players = Player.query.order_by(Player.orari_grupit).all()

    # Calculate next payment date for each player
    for player in all_players:
        player.next_payment_date = player.data_regjistrimit + timedelta(days=30)

    # Group players by time slot
    grouped_players = {}
    for player in all_players:
        group = player.orari_grupit
        if group not in grouped_players:
            grouped_players[group] = []
        grouped_players[group].append(player)

    return render_template("coach.html", grouped_players=grouped_players)


@app.route('/delete_player/<int:player_id>', methods=["POST"])
def delete_player(player_id):
    if not session.get("coach_logged_in"):
        return redirect(url_for("login"))

    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for("coach_view"))

@app.route("/logout")
def logout():
    session.pop("coach_logged_in", None)
    return redirect(url_for("login"))


with app.app_context():
    db.create_all()

    # Create a default coach only if it doesn't exist
    if not Coach.query.filter_by(username="coach").first():
        coach = Coach(username="coach", password_hash=generate_password_hash("password123"))
        db.session.add(coach)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
