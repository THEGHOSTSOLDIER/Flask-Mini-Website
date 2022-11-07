import click
from .app import app, db
from .models import Author, Book


@app.cli.command()
def syncdb():
    """
    Crée les tables correspondant au modèle
    """
    db.create_all()

@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    '''
     Create all tables and populate them with data in filename
    '''
    db.create_all()

    import yaml
    books = yaml.load(open(filename),Loader=yaml.FullLoader)

    authors = dict()
    for b in books:
        nom = b["author"]
        if nom not in authors.keys():
            o = Author(name=nom)
            # On ajoute l'objet o à la session (en mémoire) :
            db.session.add(o)
            authors[nom] = o
    # On dit à la DB d'intégrer toutes les nouvelles données:
    db.session.commit()

    # Création des livres
    for b in books:
        # on récupère l'auteur du livre
        # courant dans le dico authors
        a = authors[b["author"]]
        book = Book(price   = b["price"],
                    title   = b["title"],
                    url     = b["url"],
                    img     = b["img"],
                    author_id = a.id) 
    # On ajoute l'objet book à la session :
        db.session.add(book)
    # on sauvegarde les livres en BD
    db.session.commit()

@app.cli.command()
@click.argument('username')
@click.argument('password')
def newuser(username , password):
    '''Adds a new user.'''
    from .models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User(username=username , password=m.hexdigest())
    db.session.add(u)
    db.session.commit()

@app.cli.command()
@click.argument('username')
@click.argument('password')
def passwd(username , password):
    '''Change password for user.'''
    from .models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User.query.get(username)
    u.password = m.hexdigest()
    db.session.commit()