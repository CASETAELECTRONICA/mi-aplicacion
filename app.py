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

    # Obtener configuración para validar los datos ingresados
    cursor.execute('SELECT * FROM Configuracion LIMIT 1')
    configuracion = cursor.fetchone()
    numero_equipos, numero_estaciones, calificacion_maxima = configuracion[1], configuracion[2], configuracion[3]

    # Validar los datos
    if numero_equipo > numero_equipos:
        mensaje = f"Error: El número de equipo no puede superar {numero_equipos}."
        return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)
    if estacion > numero_estaciones:
        mensaje = f"Error: El número de estación no puede superar {numero_estaciones}."
        return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)
    if puntuacion > calificacion_maxima:
        mensaje = f"Error: La puntuación no puede superar {calificacion_maxima}."
        return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)

    # Revisar si ya existe el registro
    cursor.execute('SELECT * FROM Datos WHERE numero_equipo = ? AND estacion = ?', (numero_equipo, estacion))
    registro_existente = cursor.fetchone()

    if registro_existente:
        conn.close()
        # Redirigir al formulario de confirmación de actualización
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

@app.route('/actualizar', methods=['POST'])
def actualizar_datos():
    numero_equipo = int(request.form['numero_equipo'])
    estacion = int(request.form['estacion'])
    puntuacion = float(request.form['puntuacion'])

    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    # Actualizar el registro existente
    cursor.execute('UPDATE Datos SET puntuacion = ? WHERE numero_equipo = ? AND estacion = ?', 
                   (puntuacion, numero_equipo, estacion))
    conn.commit()
    conn.close()

    mensaje = f"Registro actualizado: Equipo {numero_equipo}, Estación {estacion}, Puntuación {puntuacion}."
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Configuracion LIMIT 1')
    configuracion = cursor.fetchone()
    conn.close()
    return render_template('formulario.html', configuracion=configuracion, mensaje=mensaje)

@app.route('/validar_nip', methods=['GET', 'POST'])
def validar_nip():
    mensaje = ""
    if request.method == 'POST':
        nip = request.form['nip']

        conn = sqlite3.connect('equipos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nip_borrado FROM Configuracion LIMIT 1')
        nip_correcto = cursor.fetchone()[0]
        conn.close()

        if nip == nip_correcto:
            return redirect('/configuracion')  # Redirigir a la configuración si el NIP es correcto
        else:
            mensaje = "NIP incorrecto. Intenta de nuevo."

    return render_template('validar_nip.html', mensaje=mensaje)

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    mensaje = ""
    if request.method == 'POST':
        numero_equipos = int(request.form['numero_equipos'])
        numero_estaciones = int(request.form['numero_estaciones'])
        calificacion_maxima = int(request.form['calificacion_maxima'])
        nip_borrado = request.form['nip_borrado']
        cursor.execute('''
            UPDATE Configuracion
            SET numero_equipos = ?, numero_estaciones = ?, calificacion_maxima = ?, nip_borrado = ?
            WHERE id = 1
        ''', (numero_equipos, numero_estaciones, calificacion_maxima, nip_borrado))
        conn.commit()
        mensaje = "Configuración Guardada"

    # Obtener configuración actual
    cursor.execute('SELECT * FROM Configuracion LIMIT 1')
    configuracion_actual = cursor.fetchone()
    conn.close()
    return render_template('configuracion.html', configuracion=configuracion_actual, mensaje=mensaje)

@app.route('/registros', methods=['GET'])
def mostrar_registros():
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            numero_equipo,
            COUNT(DISTINCT estacion) AS cantidad_estaciones,
            GROUP_CONCAT(puntuacion || ' (Estación ' || estacion || ')', ', ') AS puntuaciones
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

    # Obtener el número máximo de estaciones desde la configuración
    cursor.execute('SELECT numero_estaciones FROM Configuracion LIMIT 1')
    numero_maximo_estaciones = cursor.fetchone()[0]

    cursor.execute('''
        SELECT numero_equipo,
               COUNT(DISTINCT estacion) AS num_estaciones,
               SUM(puntuacion) AS total_puntos
        FROM Datos
        GROUP BY numero_equipo
        ORDER BY total_puntos DESC
    ''')
    resultados = cursor.fetchall()

    # Calcular el promedio usando el número máximo de estaciones configurado
    ranking_con_lugares = []
    lugar = 1
    for resultado in resultados:
        promedio = resultado[2] / numero_maximo_estaciones  # Usar número máximo de estaciones para el promedio
        ranking_con_lugares.append((*resultado, promedio, f"{lugar}°"))  # Añadir el promedio y el lugar
        lugar += 1

    conn.close()
    return render_template('ranking.html', resultados=ranking_con_lugares)

@app.route('/eliminar', methods=['POST'])
def eliminar_registros():
    nip = request.form['nip']

    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nip_borrado FROM Configuracion LIMIT 1')
    nip_correcto = cursor.fetchone()[0]

    mensaje = ""
    if nip == nip_correcto:
        cursor.execute("DELETE FROM Datos")
        conn.commit()
        mensaje = "Todos los registros han sido eliminados correctamente."
    else:
        mensaje = "NIP incorrecto. No se eliminaron los registros."

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
    conn.close()

    return render_template('ranking.html', resultados=resultados, mensaje=mensaje)

if __name__ == '__main__':
    crear_tabla()
    app.run(debug=True)