import sqlite3

conn = sqlite3.connect('equipos.db')
cursor = conn.cursor()

# Crear la tabla de datos
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

print("Base de datos creada con éxito.")