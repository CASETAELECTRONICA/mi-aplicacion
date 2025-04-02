from flask import Flask, render_template, request, redirect
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
    return render_template('formulario.html')

@app.route('/guardar', methods=['POST'])
def guardar_datos():
    numero_equipo = request.form['numero_equipo']
    estacion = request.form['estacion']
    puntuacion = request.form['puntuacion']

    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    # Verificar si el equipo ya existe en la misma estación
    cursor.execute('SELECT * FROM Datos WHERE numero_equipo = ? AND estacion = ?', (numero_equipo, estacion))
    registro_existente = cursor.fetchone()

    if registro_existente:
        conn.close()
        return render_template('confirmar_actualizacion.html', numero_equipo=numero_equipo, estacion=estacion, puntuacion=puntuacion)
    else:
        cursor.execute('INSERT INTO Datos (numero_equipo, puntuacion, estacion) VALUES (?, ?, ?)', (numero_equipo, puntuacion, estacion))
        conn.commit()
        conn.close()
        return redirect('/')

@app.route('/actualizar', methods=['POST'])
def actualizar_datos():
    numero_equipo = request.form['numero_equipo']
    estacion = request.form['estacion']
    puntuacion = request.form['puntuacion']

    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE Datos SET puntuacion = ? WHERE numero_equipo = ? AND estacion = ?', (puntuacion, numero_equipo, estacion))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/registros', methods=['GET'])
def mostrar_registros():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT numero_equipo, GROUP_CONCAT(puntuacion || ' (Estación ' || estacion || ')', ', ') AS puntuaciones
        FROM Datos
        GROUP BY numero_equipo
        ORDER BY numero_equipo ASC
    ''')
    registros = cursor.fetchall()
    conn.close()
    return render_template('registros.html', registros=registros)

@app.route('/ranking', methods=['GET'])
def ranking():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    # Consulta para calcular total de puntos, cantidad de estaciones y promedio por equipo
    cursor.execute('''
        SELECT numero_equipo,
               COUNT(DISTINCT estacion) AS num_estaciones,
               SUM(puntuacion) AS total_puntos,
               (SUM(puntuacion) * 1.0 / COUNT(DISTINCT estacion)) AS promedio
        FROM Datos
        GROUP BY numero_equipo
        ORDER BY promedio DESC
    ''')
    resultados = cursor.fetchall()

    # Añadir lugares basados en el promedio
    ranking_con_lugares = []
    lugar = 1
    for resultado in resultados:
        ranking_con_lugares.append((*resultado, f"{lugar}°"))
        lugar += 1

    conn.close()
    return render_template('ranking.html', resultados=ranking_con_lugares)

@app.route('/debug-registros', methods=['GET'])
def debug_registros():
    try:
        conn = sqlite3.connect('equipos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Datos")
        registros = cursor.fetchall()
        conn.close()
        return f"Registros actuales en la base de datos: {registros}"
    except Exception as e:
        return f"Error al consultar la base de datos: {e}"

if __name__ == '__main__':
    crear_tabla()
    app.run(debug=True)