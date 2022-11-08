from .app import app,db
from flask import render_template, url_for, redirect
from .models import Book, Author, get_sample, get_book_detail, get_author
 
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, validators

from wtforms import PasswordField
from .models import User
from hashlib import sha256

from flask_login import login_user , current_user
from flask import request
from flask_login import logout_user

from flask_login import login_required


class AuthorForm(FlaskForm):
        id   = HiddenField('id')
        name = StringField('Nom',
                [validators.InputRequired(),
                validators.Length(min=2, max=25, 
                message="Le nom doit avoir entre 2 et 25 caractères !"),
                #validators.Regexp('^\w+$', message="Username must contain only letters numbers or underscore"),
                validators.Regexp('^[a-zA-Z \.\-]+$', message="Le nom doit contenir seulement des lettres et espaces ou - et ."),
                ])

class BookForm(FlaskForm):
        id = HiddenField('id')
        title = StringField('Titre',
                [validators.InputRequired(),
                validators.Length(min=2, max=100, 
                message="Le titre doit avoir entre 2 et 100 caractères !"),
                validators.Regexp('^[a-zA-Z0-9 \.\-]+$', message="Le titre doit contenir seulement des lettres, des chiffres et espaces ou - et ."),
                ])
        price = StringField('Prix',
                [validators.InputRequired(),
                validators.Length(min=1, max=10, 
                message="Le prix doit avoir entre 1 et 10 caractères !"),
                #validators.Regexp can contain only numbers and a dot
                validators.Regexp('^[0-9\.]+$', message="Le prix doit contenir seulement des chiffres et un point"),
                ])
        url = StringField('URL',
                [validators.InputRequired(),
                validators.Length(min=2, max=100, 
                message="L'URL doit avoir entre 2 et 100 caractères !"),
                #validators.Regexp can only contain letters, numbers, underscore, dash, dot, slash
                validators.Regexp('^[a-zA-Z0-9\-\_\.\/\:]+$', message="L'URL doit contenir seulement des lettres, des chiffres et - _ . /"),
                ])
        """
        img = StringField('Image',
                [validators.InputRequired(),
                validators.Length(min=2, max=100, 
                message="L'image doit avoir entre 2 et 100 caractères !"),
                validators.Regexp('^[a-zA-Z0-9 \.\-]+$', message="L'image doit contenir seulement des lettres, des chiffres et espaces ou - et ."),
                ])
        """
        author_id = StringField('Auteur',
                [validators.InputRequired(),
                validators.Length(min=1, max=10, 
                message="L'auteur doit avoir entre 1 et 10 caractères !"),
                validators.Regexp('^[0-9]+$', message="L'auteur doit contenir seulement des chiffres"),
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
@login_required
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

@app.route("/edit/book/")
@app.route("/edit/book/<int:id>")
@login_required
def edit_book(id=None):
    titre = None # saisie nouveau livre
    prix = None
    url = None
    img = None
    author_id = None
    if id is not None: # Modif
        a = get_book_detail(int(id))
        titre = a.title
        prix = a.price
        url = a.url
        #img = a.img
        author_id = a.author_id
    else:
        a = None
    f = BookForm(id =id, title=titre, price=prix, url=url, author_id=author_id)
    return render_template(
        "edit-book.html",
        book=a,form=f
    )

@app.route("/save/book/",methods=("POST",))
def save_book():
    f = BookForm()
    # Si en update, on a un id
    if f.id.data != "":
        id = int(f.id.data)
        a = get_book_detail(int(id))
    else: # Création d'un nouveau livre
        a = Book(title=f.title.data, price=f.price.data, url=f.url.data, author_id=f.author_id.data)
        db.session.add(a)
    if f.validate_on_submit():
        a.title = f.title.data
        a.price = f.price.data
        a.url = f.url.data
        #a.img = f.img.data
        a.author_id = f.author_id.data
        db.session.commit() # Sauvegarde en BD
        return redirect(url_for('detail',id=a.id))
    return render_template(
        "edit-book.html",
        book=a,form=f)
    
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField()
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
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("home")
            return redirect(next)
    return render_template(
        "login.html",
        form=f)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))