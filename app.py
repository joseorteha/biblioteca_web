from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Configuración de la base de datos con tu usuario
DB_CONFIG = {
    'host': 'localhost',  # Cambia a tu IP pública para acceso remoto
    'user': 'ortega',
    'password': '2025',  # Reemplaza con tu contraseña real
    'database': 'biblioteca_db',
    'port': 3306
}

# Función para conectar a la base de datos
def conectar_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
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
def registrar():
    # Obtener datos del formulario
    titulo = request.form['titulo']
    autor = request.form['autor']
    anio = request.form['anio']
    genero = request.form['genero']

    # Insertar en la base de datos
    conn = conectar_db()
    cursor = conn.cursor()
    query = "INSERT INTO libros (titulo, autor, anio_publicacion, genero) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (titulo, autor, anio, genero))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)