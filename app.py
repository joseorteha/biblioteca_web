import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración de la base de datos con tu usuario
DB_CONFIG = {
    'host': 'localhost',
    'user': 'bibliotecario',
    'password': '2025',
    'database': 'biblioteca_db',
    'port': 3306
}

# Función para conectar a la base de datos
def conectar_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Conexión exitosa a la base de datos")
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clase de usuario para Flask-Login
class Usuario(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Callback para cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return Usuario(user_data['id'], user_data['username'])
    return None

@app.route('/')
@login_required
def index():
    # Consultar todos los libros
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    cursor.close()
    conn.close()

    # Generar HTML para la tabla
    tabla = ""
    for libro in libros:
        tabla += f"<tr><td>{libro[0]}</td><td>{libro[1]}</td><td>{libro[2]}</td><td>{libro[3]}</td><td>{libro[4]}</td></tr>"
    
    return render_template('index.html', tabla_datos=tabla)

@app.route('/registrar', methods=['POST'])
@login_required
def registrar():
    # Obtener datos del formulario
    titulo = request.form['titulo']
    autor = request.form['autor']
    anio = request.form['anio']
    genero = request.form['genero']

    print(f"Datos recibidos: Titulo={titulo}, Autor={autor}, Año={anio}, Genero={genero}")

    # Insertar en la base de datos
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        query = "INSERT INTO libros (titulo, autor, anio_publicacion, genero) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (titulo, autor, anio, genero))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Libro registrado con éxito!', 'success')
        print("Libro registrado con éxito!")
    except mysql.connector.Error as err:
        flash(f'Error al registrar el libro: {err}', 'danger')
        print(f"Error al registrar el libro: {err}")

    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = conectar_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and user_data['password'] == hashlib.sha256(password.encode()).hexdigest():
            user = Usuario(user_data['id'], user_data['username'])
            login_user(user)
            return redirect('/')
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)