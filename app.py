from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required
from flask import flash
from flask_login import UserMixin
from flask_login import current_user

app = Flask(__name__)

app.secret_key = 'wvEeTX=W93Rp.VQBmxh;FZ'

app.config["MONGO_URI"] = "mongodb://localhost:27017/blog"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.config['SESSION_COOKIE_EXPIRES'] = None

class User(UserMixin):
    def __init__(self, username, user_id):
        self.username = username
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user:
        return User(user['username'], user['_id']) 
    return None  

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if mongo.db.users.find_one({'username': username}):
            flash('Usuário já cadastrado')
            return redirect(url_for('register'))
        
        new_user = {
            'username': username,
            'password': hashed_password
        }
        
        mongo.db.users.insert_one(new_user)
        flash('Usuário cadastrado com sucesso')
        return redirect(url_for('login'))
    
    return render_template('register.html')   

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = mongo.db.users.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(user['username'], user['_id'])
            login_user(user_obj)
            return redirect(url_for('profile'))
        flash('Usuário ou senha inválidos')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/profile")
@login_required
def profile():
    user = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    return render_template('profile.html', user=user)

@app.route("/")
def index():
    return render_template('index.html')
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/post_list")
@login_required
def post_list():
    current_user_id = current_user.id
    posts_cursor = mongo.db.posts.find({'autor': current_user.username})
    posts = list(posts_cursor)
    return render_template('post_list.html', posts=posts)

@app.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        post = {
            'titulo': titulo,
            'conteudo': conteudo,
            'data': datetime.now(),
            'autor': current_user.username  
        }
        if post['titulo'] == '' or post['conteudo'] == '':
            erro = 'Preencha todos os campos'
            return redirect(url_for('create_post'))
        mongo.db.posts.insert_one(post)
        return redirect(url_for('post_list'))
    
    return render_template('create_post.html')

@app.route("/delete_post", methods=['POST'])
def delete_post():
    post_id = request.form.get('id')
    if post_id:
        mongo.db.posts.delete_one({'_id': ObjectId(post_id)})
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True)
