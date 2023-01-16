import os

from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


#Inicialização
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
Bootstrap(app)


# database setup.
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'todo.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config['SECRET_KEY'] = 'secret'

login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#class models.
class Restaurante(db.Model):
    __tablename__ = "restaurantes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __str__(self):
        return f"[Restaurante] name: {self.name}"


class Prato(db.Model):
    __tablename__ = "pratos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    restaurante = db.Column('Restaurante', db.ForeignKey(Restaurante.id))

    def __init__(self, id, name, description, category, price, restaurante):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.restaurante = restaurante

    def __repr__(self):
        return f"[Prato] description: {self.description[:50]}"

#USUARIOS
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(86), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

@login_manager.user_loader
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()

# applications routes.
###################### PRINCIPAL/INDEX ########################            
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':                    
        nome_prato = request.form['name']
        if nome_prato == '' :        
            pratos = Prato.query.order_by(Prato.id).all()       
            return render_template("index.html", pratos=pratos) 
        else: 
            if request.method == 'POST':                           
                nome_prato_aux = "%{}%".format(nome_prato)
                pratos = Prato.query.filter(Prato.name.like(nome_prato_aux)).all()
                return render_template("index.html", pratos=pratos)
    else:
        pratos = Prato.query.order_by(Prato.id).all()        
        return render_template("index.html", pratos=pratos)

###################### RESTAURANTE ########################            
@app.route('/inclusao_restaurante', methods=['POST', 'GET'])
def inclusao_restaurante():
    if request.method == 'POST':

        restaurante = Restaurante(id=request.form['id'], name=request.form['name'])
        try:
            db.session.add(restaurante)
            db.session.commit()
            return redirect(url_for('inclusao_restaurante'))
        except:
            return "Houve um erro ao inserir o restaurante"
    else:
        restaurantes = Restaurante.query.order_by(Restaurante.id).all()
        return render_template("inclusao_restaurante.html", restaurantes=restaurantes)
   
@app.route('/restaurante/update/<int:id>', methods=['GET', 'POST'])
def update_restaurante(id):
    restaurante = Restaurante.query.get_or_404(id)
    if request.method == 'POST':
        restaurante.name = request.form['name']
        try:
            db.session.commit()
            return redirect(url_for('inclusao_restaurante'))
        except:
            return "Houve um erro ao atualizar o restaurante"
    else:
        return render_template('update_restaurante.html', restaurante=restaurante)

@app.route('/restaurante/delete/<int:id>')
def delete_restaurante(id):
    restaurante = Restaurante.query.get_or_404(id)
    try:
        db.session.delete(restaurante)
        db.session.commit()
        return redirect(url_for('inclusao_restaurante'))
    except:
        return "Houve um erro ao excluir o restaurante"

###################### PRATO ########################
@app.route('/inclusao_prato', methods=['POST', 'GET'])
def inclusao_prato():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        restaurante = request.form['restaurante']
        prato = Prato(id, name, description, category, price, restaurante)
        db.session.add(prato)

        db.session.commit()
        return redirect(url_for('inclusao_prato'))
    else:
        pratos = Prato.query.order_by(Prato.id).all()
        return render_template("inclusao_prato.html", pratos=pratos)        

@app.route('/prato/update/<int:id>', methods=['GET', 'POST'])
def update_prato(id):
    prato = Prato.query.get_or_404(id)
    if request.method == 'POST':
        prato.name        = request.form['name']
        prato.description = request.form['description']
        prato.category    = request.form['category']
        prato.price       = request.form['price']        
        prato.restaurante = request.form['restaurante']
        try:
            db.session.commit()
            return redirect(url_for('inclusao_prato'))    
        except:
            return "Houve um erro, ao atualizar o prato"
    
    return render_template('update_prato.html', prato=prato)
    
@app.route('/prato/delete/<int:id>')
def delete_prato(id):
    prato = Prato.query.get_or_404(id)
    try:
        db.session.delete(prato)
        db.session.commit()
        return redirect(url_for('inclusao_prato'))
    except:
        return "Houve um erro ao excluir o prato"


@app.route('/prato/pesquisa/<prato>')
def pesquisa_prato(name):        
    pratos = Prato.filter_by(name=name).first()    
    return render_template("index.html", pratos=pratos)

###################### LOGIN ########################            
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pwd = request.form['password']

        user = User(name, email, pwd)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not user.verify_password(pwd):            
            return "Falha no Login"
            #return redirect(url_for('login'))        

        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
