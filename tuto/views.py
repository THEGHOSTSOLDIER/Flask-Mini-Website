from .app import app,db
from flask import render_template, url_for, redirect
from .models import Author,get_sample, get_book_detail, get_author
 
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, validators

from wtforms import PasswordField
from .models import User
from hashlib import sha256

from flask_login import login_user , current_user
from flask import request
from flask_login import logout_user


class AuthorForm(FlaskForm):
        id   = HiddenField('id')
        name = StringField('Nom',
                [validators.InputRequired(),
                validators.Length(min=2, max=25, 
                message="Le nom doit avoir entre 2 et 25 caractères !"),
                #validators.Regexp('^\w+$', message="Username must contain only letters numbers or underscore"),
                validators.Regexp('^[a-zA-Z \.\-]+$', message="Le nom doit contenir seulement des lettres et espaces ou - et ."),
                ])

@app.route("/")
def home():
    return render_template(
        "booksBS.html", 
        title="My Books !",
        books=get_sample())


@app.route("/detail/<id>")
def detail(id):
    books = get_sample()
    book = get_book_detail(int(id))
    return render_template(
        "detail.html",
        book=book)


@app.route("/author/<int:id>")
def one_author(id):
    auteur =  get_author(id)
    return render_template(
        "booksBS.html", 
        title="Livres de "+auteur.name,
        books=auteur.books)

@app.route("/edit/author/")
@app.route("/edit/author/<int:id>")
def edit_author(id=None):
    nom = None # saisie nouvel auteur
    if id is not None: # Modif
        a = get_author(id)
        nom = a.name
    else:
        a = None
    f = AuthorForm(id =id, name=nom)
    return render_template(
        "edit-author.html",
        author=a,form=f
    )

@app.route("/save/author/",methods=("POST",))
def save_author():
    f = AuthorForm()
    # Si en update, on a un id
    if f.id.data != "":
        id = int(f.id.data)
        a = get_author(id)
    else: # Création d'un nouvel auteur
        a = Author(name=f.name.data)
        db.session.add(a)
    if f.validate_on_submit():
        a.name = f.name.data
        db.session.commit() # Sauvegarde en BD
        return redirect(url_for('one_author',id=a.id))
    return render_template(
        "edit-author.html",
        author=a,form=f)
    
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    def get_authenticated_user(self):
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None

@app.route("/login/", methods=("GET","POST",))
def login():
    f = LoginForm()
    if f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            return redirect(url_for("home"))
    return render_template(
        "login.html",
        form=f)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))