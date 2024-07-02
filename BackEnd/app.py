from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Create the database and the user table
with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def hello_world():
    return 'Hello, World!'

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
    app.run(debug=True)
