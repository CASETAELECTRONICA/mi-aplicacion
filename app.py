from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Función para crear la base de datos y la tabla (si no existen)
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
    # Renderiza el formulario de registro
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

@app.route('/ver-datos', methods=['GET'])
def ver_datos():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Datos")
    registros = cursor.fetchall()
    conn.close()
    return jsonify(registros)

@app.route('/registros', methods=['GET'])
def mostrar_registros():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Datos")
    registros = cursor.fetchall()
    conn.close()
    return render_template('registros.html', registros=registros)

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