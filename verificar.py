import sqlite3
conexion = sqlite3.connect("alumnos.db")
cursor = conexion.cursor()

# Si quedó la tabla vieja de un intento fallido, la eliminamos
cursor.execute("DROP TABLE IF EXISTS alumnos_vieja")

# Verificamos qué columnas tiene la tabla actual
cursor.execute("PRAGMA table_info(alumnos)")
columnas = [fila[1] for fila in cursor.fetchall()]
print("Columnas actuales de 'alumnos':", columnas)

conexion.commit()
conexion.close()
