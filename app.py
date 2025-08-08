from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv 
import os
import re

#Create Flask instance
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/mitrobasket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

#Table for storing player information
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

#Function to calculate time slot based on age
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

#Only coaches can access the player data
class Coach(db.Model):
    __tablename__ = 'coaches'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#Home route
@app.route('/')
def home():
    return render_template('index.html')

#Register route
@app.route('/register', methods=['POST'])
#Retrieve form data and validate it
def register():
    emri = request.form.get('full_name').strip()
    emri_prindit = request.form.get('parent_name').strip()
    mbiemri = request.form.get('last_name').strip()
    mosha = request.form.get('age')
    numri_telefonit = request.form.get('telephone_number')

    if not (emri and mbiemri and mosha and numri_telefonit):
        return "Mbushini të gjitha fushat", 400

    try:
        mosha = int(mosha)
    except ValueError:
        return "Mosha nuk është valide", 400
    
    # Format check for phone number - +383 4X XXX XXX
    pattern = r"^\+383 4\d \d{3} \d{3}$"
    if not re.match(pattern, numri_telefonit):
        flash("Formati i numrit të telefonit duhet të jetë: +383 4X XXX XXX", "error")
        return render_template("index.html")
    

    #Check if the player already exists - duplicate
    existing_player = Player.query.filter_by(
        emri=emri,
        mbiemri=mbiemri,
        numri_telefonit=numri_telefonit
    ).first()

    if existing_player:
        error_message = "Ky lojtar është regjistruar më parë!"
        return render_template('index.html', error=error_message)

    #Assign time slot based on age
    orari = calculate_orari(mosha)

    #Create and save the player to the database
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

    #Redirect to confirmation page
    return render_template('confirmation.html', emri=emri, orari=orari)

#Login route for coaches
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

            #Lockout after 3 failed attempts
            if session['login_attempts'] >= 3:
                flash("Shumë tentativa të pasuksesshme. Po ju kthejmë në faqen kryesore.", "error")
                session['login_attempts'] = 0
                return redirect(url_for("home"))

    return render_template("login.html")

# Coach view route
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

#Coaches can delete players by ID (primary key)
@app.route('/delete_player/<int:player_id>', methods=["POST"])
def delete_player(player_id):
    if not session.get("coach_logged_in"):
        return redirect(url_for("login"))

    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for("coach_view"))

#Logout route for coachesS
@app.route("/logout")
def logout():
    session.pop("coach_logged_in", None)
    return redirect(url_for("login"))

#Database initialization
with app.app_context():
    db.create_all()

    default_username = os.getenv("COACH_USERNAME")
    default_password = os.getenv("COACH_PASSWORD")

    #Check if the default coach exists, if not create it
    if not Coach.query.filter_by(username=default_username).first():
        coach = Coach(username=default_username, password_hash=generate_password_hash(default_password))
        db.session.add(coach)
        db.session.commit()

#Run the application locally
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
