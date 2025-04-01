from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Crear la base de datos si no existe
def crear_tabla():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Datos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_equipo INTEGER,
            puntuacion FLOAT,
            estacion TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/guardar', methods=['POST'])
def guardar_datos():
    numero_equipo = request.form['numero_equipo']
    puntuacion = request.form['puntuacion']
    estacion = request.form['estacion']
    
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Datos (numero_equipo, puntuacion, estacion)
        VALUES (?, ?, ?)
    ''', (numero_equipo, puntuacion, estacion))
    conn.commit()
    conn.close()
    return "Datos guardados correctamente."

# Ruta para ver los datos en formato JSON
@app.route('/ver-datos', methods=['GET'])
def ver_datos():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Datos')
    registros = cursor.fetchall()
    conn.close()
    return jsonify(registros)

# Ruta para ver los registros en una tabla HTML
@app.route('/registros')
def mostrar_registros():
    # Conexión a la base de datos
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Datos")  # Consulta todos los registros de la tabla Datos
    registros = cursor.fetchall()
    conn.close()
    # Renderiza la tabla usando la plantilla registros.html
    return render_template('registros.html', registros=registros)

# Ruta para ver el ranking calculado
@app.route('/ranking', methods=['GET'])
def ranking():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT numero_equipo, estacion, SUM(puntuacion) AS total_puntos, AVG(puntuacion) AS promedio
        FROM Datos
        GROUP BY numero_equipo, estacion
        ORDER BY promedio DESC
    ''')
    resultados = cursor.fetchall()
    conn.close()
    return render_template('ranking.html', resultados=resultados)

if __name__ == '__main__':
    crear_tabla()
    app.run(debug=True)
