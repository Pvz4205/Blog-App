from flask import Flask, render_template, url_for, request, session, redirect, flash
import datetime
import json
import math
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
app = Flask(__name__)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
with open("config.json", "r") as c:
    param = json.load(c)["parameters"]
    print(param["title"])
if param["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = param["URI_local"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param["URI_Production"]
db = SQLAlchemy(app)
admin_user = "jullan"
admin_password = "4205"
app.secret_key = "2005"
class Post(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    subtitle = Column(String(500), nullable=False)
    image = Column(String(500))
    author = Column(String(30))
    date = Column(String(30))
    content1 = Column(String(500))
    content2 = Column(String(500))
    slug = Column(String(30), unique=True)
class Contact(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    email = Column(String(500), nullable=False)
    message = Column(String(500), nullable=False)
    date = Column(String(20), nullable=False)
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(500), nullable=False)
    email = Column(String(500), nullable=False)
    password = Column(String(500), nullable=False)
@app.route('/')
def index():
    info = Post.query.all()
    total = len(info)
    n = 2
    num_pages = math.ceil(total/n)
    cur_page = request.args.get("page")
    if not str(cur_page).isnumeric():
        cur_page = 1
    else:
        cur_page = int(cur_page)
    str_index = (cur_page-1)*n
    sel_post = info[str_index:str_index+n]
    if cur_page == 1:
        previous = "#"
        next = "/?page="+str(cur_page+1)
    elif cur_page == num_pages:
        previous = "/?page=" + str(cur_page - 1)
        next = "#"
    else:
        previous = "/?page=" + str(cur_page - 1)
        next = "/?page=" + str(cur_page + 1)
    return render_template("index.html", data=sel_post, param=param, previous=previous, next=next)
@app.route('/post/<slug>')
def post(slug):
    single_post = Post.query.filter_by(slug=slug).first()
    return render_template("post.html", param=param, data=single_post)
@app.route('/about')
def about():
    return render_template("about.html", param=param)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template("contact.html", param=param)
    elif request.method == 'POST':
        newcontact = Contact()
        newcontact.name = request.form.get('name')
        newcontact.email = request.form.get('email')
        newcontact.message = request.form.get('message')
        newcontact.date = datetime.datetime.now().date()
        db.session.add(newcontact)
        db.session.commit()
        return render_template("contact.html", param=param)
@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        exist_user = User.query.filter_by(username = user).first()
        if exist_user and exist_user.password == password:
            #session['loggedin'] = True
            login_user(exist_user)
            return redirect(url_for('admin'))
        elif not exist_user:
            flash("Username does not exist")
        elif exist_user.password != password:
            flash("Password is incorrect")
    return render_template("login.html", param=param)
@app.route('/admin')
@login_required
def admin():
    all_post = Post.query.filter_by().all()
    name = current_user.username
    return render_template("admin/index.html", param=param, all=all_post, name=name)
@app.route('/edit/<string:post_id>', methods=["GET", "POST"])
@login_required
def edit(post_id):
    name = current_user.username
    if request.method == "GET":
        post1 = Post.query.filter_by(id=post_id).first()
        return render_template("admin/edit_post.html", param=param, post=post1, name=name)
    else:
        if post_id != 0:
            edit_post = Post.query.filter_by(id=post_id).first()
            edit_post.title = request.form.get("title")
            edit_post.subtitle = request.form.get("subtitle")
            edit_post.author = request.form.get("author")
            edit_post.image = request.form.get("image")
            edit_post.date = datetime.datetime.now().strftime("%d %B %Y")
            edit_post.content1 = request.form.get("content1")
            edit_post.content2 = request.form.get("content2")
            edit_post.slug = request.form.get("slug")
            db.session.commit()
            return redirect(url_for("admin"))
        else:
            edit_post = Post()
            edit_post.title = request.form.get("title")
            edit_post.subtitle = request.form.get("subtitle")
            edit_post.author = request.form.get("author")
            edit_post.image = request.form.get("image")
            edit_post.date = datetime.datetime.now().strftime("%d %B %Y")
            edit_post.content1 = request.form.get("content1")
            edit_post.content2 = request.form.get("content2")
            edit_post.slug = request.form.get("slug")
            db.sessio.add(edit_post)
            db.session.commit()
            return redirect(url_for("admin"))
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        new_user = User()
        new_user.username = request.form.get("username")
        new_user.email = request.form.get("email")
        new_user.password = request.form.get("password")
        exist_user = User.query.filter_by(email = new_user.email).first()
        if exist_user:
            flash(" Email Address already exists ")
        else:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("signup.html", param=param)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
