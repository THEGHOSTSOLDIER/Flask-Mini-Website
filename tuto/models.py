from .app import db

class Author(db.Model):
    """
    Class Author avec id et name
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return "<Author (%d) %s>" % (self.id, self.name)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    title = db.Column(db.String(120))
    url = db.Column(db.String(256))
    img = db.Column(db.String(256))
    author_id = db.Column(db.Integer,db.ForeignKey("author.id"))
    author = db.relationship("Author", backref=db.backref("books", lazy="dynamic"))

    def __repr__(self):
        return "<Book (%d) %s>" % (self.id, self.title)


def get_sample():
    return Book.query.limit(20).all()

def get_book_detail(id):
    return Book.query.get(id)

def get_author(id):
    return Author.query.get_or_404(id)

