from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/blog"
mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/post_list")
def post_list():
    posts_cursor = mongo.db.posts.find().sort('data', -1)
    posts = list(posts_cursor)
    return render_template('post_list.html', posts=posts)

@app.route("/create_post", methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        post = {
            'titulo': titulo,
            'conteudo': conteudo,
            'data': datetime.now()
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
