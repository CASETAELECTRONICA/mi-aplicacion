from flask import Flask, render_template, request, redirect
import sqlite3

# Crear la aplicación Flask
app = Flask(__name__)

# Función para crear la base de datos y las tablas si no existen
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_equipos INTEGER DEFAULT 10,
            numero_estaciones INTEGER DEFAULT 5,
            calificacion_maxima INTEGER DEFAULT 100,
            nip_borrado TEXT DEFAULT '2307'
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def formulario():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Configuracion LIMIT 1')
    configuracion = cursor.fetchone()
    conn.close()
    return render_template('formulario.html', configuracion=configuracion)

@app.route('/guardar', methods=['POST'])
def guardar_datos():
    numero_equipo = int(request.form['numero_equipo'])
    estacion = int(request.form['estacion'])
    puntuacion = float(request.form['puntuacion'])

    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Configuracion LIMIT 1')
    configuracion = cursor.fetchone()
    numero_equipos, numero_estaciones, calificacion_maxima = configuracion[1], configuracion[2], configuracion[3]

    if numero_equipo > numero_equipos:
        mensaje = f"Error: El número de equipo no puede superar {numero_equipos}."
        return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)
    if estacion > numero_estaciones:
        mensaje = f"Error: El número de estación no puede superar {numero_estaciones}."
        return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)
    if puntuacion > calificacion_maxima:
        mensaje = f"Error: La puntuación no puede superar {calificacion_maxima}."
        return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)

    cursor.execute('SELECT * FROM Datos WHERE numero_equipo = ? AND estacion = ?', (numero_equipo, estacion))
    registro_existente = cursor.fetchone()

    if registro_existente:
        conn.close()
        return render_template('confirmar_actualizacion.html', numero_equipo=numero_equipo, estacion=estacion, puntuacion=puntuacion)
    else:
        cursor.execute('INSERT INTO Datos (numero_equipo, puntuacion, estacion) VALUES (?, ?, ?)', (numero_equipo, puntuacion, estacion))
        conn.commit()
        conn.close()

    mensaje = "Registro Guardado"
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Configuracion LIMIT 1')
    configuracion = cursor.fetchone()
    conn.close()
    return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)

@app.route('/validar_nip', methods=['GET', 'POST'])
def validar_nip():
    mensaje = ""
    nip_fijo = "0723"

    if request.method == 'POST':
        nip_ingresado = request.form['nip']

        if nip_ingresado == nip_fijo:
            return redirect('/configuracion')
        else:
            mensaje = "NIP incorrecto. Intenta de nuevo."

    return render_template('validar_nip.html', mensaje=mensaje)

@app.route('/validar_nip_registros', methods=['GET', 'POST'])
def validar_nip_registros():
    mensaje = ""
    nip_fijo = "0723"

    if request.method == 'POST':
        nip_ingresado = request.form['nip']

        if nip_ingresado == nip_fijo:
            return redirect('/registros')
        else:
            mensaje = "NIP incorrecto. Intenta de nuevo."

    return render_template('validar_nip.html', mensaje=mensaje)

@app.route('/validar_nip_mantenimiento', methods=['GET', 'POST'])
def validar_nip_mantenimiento():
    mensaje = ""
    nip_fijo = "0723"

    if request.method == 'POST':
        nip_ingresado = request.form['nip']

        if nip_ingresado == nip_fijo:
            return redirect('/mantenimiento')
        else:
            mensaje = "NIP incorrecto. Intenta de nuevo."

    return render_template('validar_nip.html', mensaje=mensaje)

@app.route('/registros', methods=['GET'])
def mostrar_registros():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT numero_equipo,
               COUNT(DISTINCT estacion) AS cantidad_estaciones,
               GROUP_CONCAT(puntuacion || ' (Estación ' || estacion || ')', ', ') AS puntuaciones
        FROM Datos WHERE estacion != 'Mantenimiento'
        GROUP BY numero_equipo
        ORDER BY numero_equipo ASC
    ''')
    registros = cursor.fetchall()
    conn.close()
    return render_template('registros.html', registros=registros)

@app.route('/mantenimiento', methods=['GET', 'POST'])
def mantenimiento():
    mensaje = ""
    if request.method == 'POST':
        numero_equipo = int(request.form['numero_equipo'])
        puntuacion = float(request.form['puntuacion'])
        
        conn = sqlite3.connect('equipos.db')
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(puntuacion) FROM Datos WHERE numero_equipo = ?', (numero_equipo,))
        total_actual = cursor.fetchone()[0]

        if total_actual is None:
            total_actual = 0

        nuevo_total = total_actual + puntuacion

        cursor.execute('INSERT INTO Datos (numero_equipo, puntuacion, estacion) VALUES (?, ?, ?)',
                       (numero_equipo, puntuacion, 'Mantenimiento'))

        conn.commit()
        conn.close()

        mensaje = f"Puntuación actualizada: El equipo {numero_equipo} ahora tiene un total de {nuevo_total} puntos."

    return render_template('mantenimiento.html', mensaje=mensaje)

@app.route('/ranking', methods=['GET'])
def ranking():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT numero_equipo,
               COUNT(DISTINCT CASE WHEN estacion != 'Mantenimiento' THEN estacion END) AS num_estaciones,
               SUM(puntuacion) AS total_puntos
        FROM Datos
        GROUP BY numero_equipo
        ORDER BY total_puntos DESC
    ''')
    resultados = cursor.fetchall()

    ranking_con_lugares = []
    lugar = 1
    for resultado in resultados:
        ranking_con_lugares.append((*resultado, f"{lugar}°"))
        lugar += 1

    conn.close()
    return render_template('ranking.html', resultados=ranking_con_lugares)

if __name__ == '__main__':
    crear_tabla()
    app.run(debug=True)