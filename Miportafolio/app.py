from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Esta línea intenta leer la URL de Render; si no existe (local), usa SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://portafolio_db_lfzo_user:GPGSFlVUerOsszPVkUsrpmBzBPIiHGcO@dpg-d781fq6a2pns73b3vmh0-a/portafolio_db_lfzo')
# Un pequeño truco: Render usa "postgres://", pero SQLAlchemy prefiere "postgresql://"
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'una_clave_muy_dificil_123'


# Modelo de datos
class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    link = db.Column(db.String(200))


from datetime import datetime


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


# Ruta principal con lógica de filtrado
@app.route('/')
def index():
    cat = request.args.get('categoria')
    if cat:
        proyectos = Proyecto.query.filter_by(categoria=cat).all()
    else:
        proyectos = Proyecto.query.all()
    return render_template('index.html', proyectos=proyectos)


@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.fecha.desc()).all()
    return render_template('blog.html', posts=posts)


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


from flask import redirect, url_for, flash  # Asegúrate de importar estos

# Una contraseña simple (en un proyecto real usarías Flask-Login, pero para empezar esto sirve)
ADMIN_PASSWORD = "1234"


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == ADMIN_PASSWORD:
            proyectos = Proyecto.query.all()
            posts = Post.query.all()
            return render_template('admin_panel.html', proyectos=proyectos, posts=posts)
        else:
            return "Acceso denegado", 403
    return render_template('admin_login.html')


@app.route('/admin/nuevo_proyecto', methods=['POST'])
def nuevo_proyecto():
    # Aquí recibimos los datos del formulario del panel
    nuevo = Proyecto(
        titulo=request.form.get('titulo'),
        categoria=request.form.get('categoria'),
        descripcion=request.form.get('descripcion'),
        link=request.form.get('link')
    )
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin/borrar_proyecto/<int:id>')
def borrar_proyecto(id):
    proyecto = Proyecto.query.get_or_404(id) # Busca el proyecto por ID o da error 404
    db.session.delete(proyecto)
    db.session.commit()
    # Después de borrar, te devuelve al panel de admin.
    # OJO: Aquí podrías pedir la contraseña de nuevo o usar una sesión.
    return redirect(url_for('index'))


# Crear la base de datos la primera vez
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
