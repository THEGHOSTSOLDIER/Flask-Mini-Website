from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)

import os.path
def mkpath(p):
        """
         renvoie chemin complet du répertoire p passé en paramètre
        """
        return os.path.normpath(
                os.path.join(
                        os.path.dirname(__file__), p))

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'
+mkpath('../books.db'))
app.config['SECRET_KEY'] = "334b0166-1e09-4e83-9593-26cac9b07096"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"