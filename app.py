from flask import Flask, render_template, redirect, request, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, URL
from forms import SignupForm, LoginForm, ShortenURLForm
import shortuuid
import qrcode
import io


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def home():
    form = ShortenURLForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            
            original_url = form.original_url.data
            custom_id = form.custom_short_id.data.strip() or shortuuid.ShortUUID().random(length=6)
            short_id = custom_id

            if URL.query.filter_by(short_id=short_id).first():
                flash("Custom short ID already exists.")
            else:
                new_url = URL(
                    original_url=original_url,
                    short_id=short_id,
                    user_id=current_user.id
                )
                db.session.add(new_url)
                db.session.commit()
                flash("URL shortened successfully.")
                return redirect(url_for('dashboard'))

    return render_template('home.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists. Please log in.")
            return redirect(url_for('login'))

        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please log in.")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid email or password.")
    return render_template('login.html', form=form)

#dashboard for table only
@app.route('/dashboard')
@login_required
def dashboard():
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('login'))

@app.route('/<short_id>')
def redirect_to_original(short_id):
    url = URL.query.filter_by(short_id=short_id).first_or_404()
    url.clicks += 1
    db.session.commit()
    return redirect(url.original_url)

# QR Code
@app.route('/qr/<short_id>')
@login_required
def generate_qr(short_id):
    url_entry = URL.query.filter_by(short_id=short_id, user_id=current_user.id).first_or_404()
    full_url = request.host_url + short_id

    img = qrcode.make(full_url)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')
#debug view
@app.route('/view_data')
@login_required
def view_data():
    users = User.query.all()
    urls = URL.query.all()
    return render_template('view_data.html', users=users, urls=urls)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
