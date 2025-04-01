@app.route('/registros')
def mostrar_registros():
    # Conexión a la base de datos
    conn = sqlite3.connect('equipos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Datos")  # Verifica que 'Datos' sea el nombre correcto de la tabla
    registros = cursor.fetchall()
    conn.close()
    # Renderiza la plantilla registros.html
    return render_template('registros.html', registros=registros)
