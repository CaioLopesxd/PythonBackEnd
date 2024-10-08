from flask import Flask, render_template, request, redirect, url_for, jsonify,make_response,flash,send_from_directory
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required
from flask_login import UserMixin
from flask_login import current_user
import gridfs

app = Flask(__name__)

app.secret_key = 'wvEeTX=W93Rp.VQBmxh;FZ'

app.config["MONGO_URI"] = "mongodb://localhost:27017/blog"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
fs = gridfs.GridFS(mongo.db)

app.config['SESSION_COOKIE_EXPIRES'] = None

class User(UserMixin):
    def __init__(self, username, user_id):
        self.username = username
        self.id = user_id
        
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Faça login para acessar esta página.')
    return redirect(url_for('login'))

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
    return render_template('login.html',user=current_user)

@app.route("/profile",methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        profilePicture = request.files.get('profilePicture')
        if profilePicture and profilePicture.filename != '':
            try:
                profilePicture_id = fs.put(profilePicture, filename=profilePicture.filename)
                mongo.db.users.update_one({'_id': ObjectId(current_user.id)}, {'$set': {'profilePicture_id': profilePicture_id}})
                flash('Imagem salva com sucesso')
            except Exception as e:
                flash(f'Erro ao salvar a imagem')
                return redirect(url_for('profile'))
    return render_template('profile.html')


@app.route("/user_profile_picture/<user_id>")
def user_profile_picture(user_id):
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user and 'profilePicture_id' in user:
            image_id = user['profilePicture_id']
            image = fs.get(image_id)
            response = make_response(image.read())
            response.content_type = 'image/jpeg'  # Ajuste conforme o formato da imagem
            return response
        else:
            # Retornar a imagem padrão se o usuário ou imagem não for encontrado
            return send_from_directory('static/images', 'perfilSemFoto.jpg'), 404
    except (gridfs.NoFile, Exception) as e:
        return send_from_directory('static/images', 'perfilSemFoto.jpg'), 404


    
@app.route("/")
def index():

    posts_cursor = mongo.db.posts.find()
    posts = list(posts_cursor)
    return render_template('index.html', posts=posts,user=current_user) 

@app.route("/server_image/<image_id>")
def server_image(image_id):
    try:
        image_id = ObjectId(image_id)  
        image = fs.get(image_id)
        response = make_response(image.read())
        response.content_type = 'image/jpeg' 
        return response
    except (gridfs.NoFile, Exception) as e:
        return str(e), 404


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/post_list")
@login_required
def post_list():
    posts_cursor = mongo.db.posts.find({'autor': current_user.username})
    posts = list(posts_cursor)
    return render_template('post_list.html', posts=posts,user=current_user)

@app.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        imagem = request.files.get('imagem')  
        
        if not titulo or not conteudo:
            flash('Preencha todos os campos obrigatórios')
            return redirect(url_for('create_post'))

        if imagem and imagem.filename != '':
            try:
                imagem_id = fs.put(imagem, filename=imagem.filename)
            except Exception as e:
                flash(f'Erro ao salvar a imagem: {e}')
                return redirect(url_for('create_post'))
        
        post = {
            'titulo': titulo,
            'conteudo': conteudo,
            'data': datetime.now(),
            'autor': current_user.username,
            'imagem_id': imagem_id  
        }

        mongo.db.posts.insert_one(post)
        return redirect(url_for('post_list'))
    
    return render_template('create_post.html',user=current_user)

@app.route("/delete_post", methods=['POST'])
def delete_post():
    post_id = request.form.get('id')
    if post_id:
        mongo.db.posts.delete_one({'_id': ObjectId(post_id)})
    return jsonify({'success': True})

@app.route("/check_login_status")
def check_login_status():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.username})
    else:
        return jsonify({'logged_in': False})
    
if __name__ == "__main__":
    app.run(debug=True)
