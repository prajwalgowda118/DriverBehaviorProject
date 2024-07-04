from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os


temp = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
#app = Flask(__name__)
app=Flask(__name__,template_folder=temp)

# Ensure the instance directory exists inside the BackEnd folder
instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)


# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

#template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

#template_dir = os.path.join(template_dir, 'Driver-Behavior-Dataset/BackEnd/templates/login.html')

#working = 'C:\Python34\pro\\frontend\\templates'
print(instance_path)

# Create the database and the user table if they don't exist
with app.app_context():
    if not os.path.exists(os.path.join(instance_path, 'users.db')):
        print("Creating database and tables...")
        db.create_all()
        print("Database and tables created.")
    else:
        print("Database already exists.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def hello_world():
    return render_template('login.html') 
    #'Hello, World!'
    #render_template('login.html')
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! Welcome to your dashboard.'

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(user_list), 200

@app.route('/users', methods=['POST'])
def add_user():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'message': 'User already exists!'}), 400

    new_user = User(username=username, email=email, password=password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 400

@app.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.username = request.json.get('username', user.username)
    user.email = request.json.get('email', user.email)
    user.password = request.json.get('password', user.password)

    try:
        db.session.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 400

@app.route('/users/<int:id>', methods=['PATCH'])
@login_required
def patch_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'username' in request.json:
        user.username = request.json['username']
    if 'email' in request.json:
        user.email = request.json['email']
    if 'password' in request.json:
        user.password = request.json['password']

    try:
        db.session.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 400

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, port=5000)
