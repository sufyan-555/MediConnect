from flask import Flask, render_template, request, session, redirect, url_for
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import base64
from datetime import datetime as dt
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg'
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

app=Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'H4B'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config["SQLALCHEMY_BINDS"]={"medicine":"sqlite:///meds.db",
                                "park":"sqlite:///parks.db"}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    monday = db.Column(db.Boolean, default=False)
    tuesday = db.Column(db.Boolean, default=False)
    wednesday = db.Column(db.Boolean, default=False)
    thursday = db.Column(db.Boolean, default=False)
    friday = db.Column(db.Boolean, default=False)
    saturday = db.Column(db.Boolean, default=False)
    sunday = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(80), nullable=False)
    image=db.Column(db.LargeBinary)

class Park(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(5), nullable=False)
    val1 = db.Column(db.Integer, nullable=False)
    val2 = db.Column(db.Integer, nullable=False)
    pram = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(80), nullable=False)





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login_page')
def login_page():
    return render_template("login.html")

@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")

@app.route('/Addmedicine')
@login_required
def Addmedicine():
    user_medicines = Medicine.query.filter_by(email=current_user.email).all()
    for medicine in user_medicines:
        if medicine.image:
            medicine.image = base64.b64encode(medicine.image).decode('utf-8')
    return render_template("Addmedicine.html",medicines=user_medicines)


def generate_plot(ids, pram_values):
    plt.figure(figsize=(10, 6))
    plt.plot(ids, pram_values, marker='o', linestyle='-', color='b', label='Pram Values')
    plt.xlabel('ID')
    plt.ylabel('Pram')
    plt.title('Last 100 Values of Pram')
    plt.grid(True)
    plt.legend()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.close()

    return plot_url

@app.route('/park')
def park():
    park_entries = Park.query.filter_by(email=current_user.email).order_by(Park.id.desc()).limit(100).all()
    ids = [entry.id for entry in park_entries]
    pram_values = [entry.pram for entry in park_entries]
    plot_url = generate_plot(ids, pram_values)

    if len(pram_values) > 60:
        diff = np.diff(pram_values)
        avg_diff = np.mean(diff)
        
        if avg_diff < 0:
            trend_comment = "The parameter shows an increasing trend. You should take a medical checkup"
        elif avg_diff > 0:
            trend_comment = "The parameter shows a decreasing trend. You are good to go :)"
        else:
            trend_comment = "The parameter shows no clear trend."
    else:
        trend_comment=None
    print(trend_comment)
    return render_template("park.html", plot_url=plot_url,result=trend_comment)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    new_user = User(username=username, email=email, 
                    password=password)
    
    db.session.add(new_user)
    db.session.commit()
    return redirect('/login_page')


@app.route('/add_med', methods=['GET', 'POST'])
@login_required
def medicineAdd_page():
    if request.method == 'POST':
        name = request.form['medicine_name']
        time = request.form['medicine_time']
        chat_id=request.form['chat_id']
        monday = 'monday' in request.form
        tuesday = 'tuesday' in request.form
        wednesday = 'wednesday' in request.form
        thursday = 'thursday' in request.form
        friday = 'friday' in request.form
        saturday = 'saturday' in request.form
        sunday = 'sunday' in request.form
        img_data = request.files['med_img'].read() if 'med_img' in request.files else None
        if img_data:
            print("Fine")
        else:
            print("none")
        
        new_med = Medicine(name=name, time=time,chat_id=chat_id, monday=monday, tuesday=tuesday,
                           wednesday=wednesday, thursday=thursday, friday=friday,
                           saturday=saturday, sunday=sunday,image=img_data,email=current_user.email)
        
        db.session.add(new_med)
        db.session.commit()
        print("Added")
    
    return redirect('/Addmedicine')


@app.route('/delete/<int:id>')               
@login_required
def delete(id):
    med = Medicine.query.filter_by(id=id, email=current_user.email).first()
    db.session.delete(med)
    db.session.commit()
    return redirect("/Addmedicine")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect('/dashboard')
        else:
            return redirect('/login')

    return render_template('login.html')

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dash.html",current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("index.html")

@app.route('/submit_distances', methods=['POST'])
def submit_distances():
    data = request.json
    distance1 = data.get('distance1')
    distance2 = data.get('distance2')
    print(f"Distance 1: {distance1}")
    print(f"Distance 2: {distance2}")

    new_entry = Park(date=dt.now().date().isoformat(),
                val1=float(distance1),
                val2=float(distance2),
                pram=float(((float(distance1)-float(distance2))**2)**0.5),
                email=current_user.email)

    
    db.session.add(new_entry)
    db.session.commit()

    return redirect("/dashboard")


@app.route('/calculator')
def calculator():
    return render_template("calculator.html")


if __name__=="__main__":
    app.run(debug=True)