from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask app with templates folder
app = Flask(__name__, template_folder='templates')

# Configuration - Using environment variables for security
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions with the SINGLE app instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }

# Create tables
with app.app_context():
    try:
        db.create_all()
        print("✅ Database created successfully!")
        print(f"📁 Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"⚠️  Database error: {e}")
        print("⚠️  Continuing anyway...")

# Routes
@app.route('/')
def home():
    # Return HTML interface
    try:
        return render_template('index.html')
    except Exception as e:
        # If template doesn't exist, return JSON
        return jsonify({
            "message": "Welcome to To-Do API (HTML interface not found)",
            "version": "1.0",
            "endpoints": {
                "api_docs": "GET /api",
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "todos": {
                    "get_all": "GET /api/todos",
                    "create": "POST /api/todos"
                }
            }
        })

@app.route('/api')
def api_docs():
    # Return JSON documentation
    return jsonify({
        "message": "Welcome to To-Do API",
        "version": "1.0",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login"
            },
            "todos": {
                "get_all": "GET /api/todos",
                "create": "POST /api/todos",
                "get_one": "GET /api/todos/<id>",
                "update": "PUT /api/todos/<id>",
                "delete": "DELETE /api/todos/<id>"
            }
        }
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password required"}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 409
        
        # Create user
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(
            username=data['username'],
            password=hashed_password,
            email=data.get('email')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password required"}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    try:
        user_id = get_jwt_identity()
        todos = Todo.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            "todos": [todo.to_dict() for todo in todos]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos', methods=['POST'])
@jwt_required()
def create_todo():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        
        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            user_id=user_id
        )
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify({
            "message": "Todo created successfully",
            "todo": todo.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        
        if not todo:
            return jsonify({"error": "Todo not found"}), 404
        
        return jsonify({
            "todo": todo.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        
        if not todo:
            return jsonify({"error": "Todo not found"}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            todo.completed = data['completed']
        
        todo.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Todo updated successfully",
            "todo": todo.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        
        if not todo:
            return jsonify({"error": "Todo not found"}), 404
        
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify({
            "message": "Todo deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting To-Do API server...")
    print("🌐 Open: http://localhost:5000")
    print("📁 Database:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("🔐 Authentication: JWT-based")
    print("\n📚 Available endpoints:")
    print("  GET  /              - Web interface")
    print("  GET  /api           - API documentation")
    print("  POST /api/auth/register - Register new user")
    print("  POST /api/auth/login    - Login and get token")
    print("  GET  /api/todos     - Get todos (requires auth)")
    print("\nPress CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)