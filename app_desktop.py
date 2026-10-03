import sqlite3   # Permite conectarse y trabajar con la base de datos SQLite
import tkinter as tk  # Librería estándar de Python para crear interfaces gráficas
from tkinter import ttk, messagebox  # ttk: widgets modernos | messagebox: ventanas de aviso
from PIL import Image, ImageTk  # Pillow: para cargar y mostrar imágenes (el logo)

# ============================================================
# CONEXIÓN A LA BASE DE DATOS
# ============================================================
conexion = sqlite3.connect("alumnos.db")  # Abre (o crea) el archivo de la base de datos
cursor = conexion.cursor()  # El cursor es el "lápiz" que ejecuta las instrucciones SQL

# ============================================================
# VENTANA: BUSCAR ALUMNO POR DNI
# ============================================================
def abrir_buscar():
    ventana_buscar = tk.Toplevel(ventana)  # Crea una ventana secundaria encima de la principal
    ventana_buscar.title("Buscar alumno por DNI")  # Título de la ventana
    ventana_buscar.geometry("1000x900")  # Tamaño en píxeles (ancho x alto)
    ventana_buscar.configure(bg="#f7f7f7")  # Color de fondo gris claro

    tk.Label(ventana_buscar, text="Ingrese el DNI a buscar:",  # Texto de instrucción
             bg="#f7f7f7", font=("Arial", 11)).pack(pady=15)  # pack() lo coloca en pantalla
    entrada_dni = tk.Entry(ventana_buscar, width=25, font=("Arial", 12))  # Campo para escribir el DNI
    entrada_dni.pack()

    marco_ficha = tk.Frame(ventana_buscar, bg="#ffffff", relief="groove", bd=2)  # Contenedor donde se mostrará la ficha
    marco_ficha.pack(pady=20, padx=20, fill="both", expand=True)  # Se expande para llenar el espacio

    def realizar_busqueda():
        for widget in marco_ficha.winfo_children():  # Recorre los widgets hijos del marco
            widget.destroy()  # Borra la ficha anterior (la limpia)

        dni = entrada_dni.get().strip()  # .get() lee el texto y .strip() quita espacios
        if not dni:  # Si el campo está vacío...
            messagebox.showwarning("Aviso", "Ingrese un DNI.", parent=ventana_buscar)  # Aviso
            return  # Sale de la función sin hacer nada más

        cursor.execute("SELECT * FROM alumnos WHERE dni = ?", (dni,))  # Consulta el DNI. El ? evita inyección SQL
        fila = cursor.fetchone()  # Devuelve una sola fila, o None si no hay

        if fila is None:  # No se encontró ningún alumno
            tk.Label(marco_ficha, text="No se encontró ningún alumno con ese DNI.",  # Mensaje de error
                     bg="#ffffff", fg="red").pack(pady=20)  # Texto en rojo
            return  # Sale de la función

        id, dni, nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado = fila  # Desempaqueta la fila en sus columnas

        datos = [  # Lista de pares (etiqueta, valor) para mostrar la ficha
            ("DNI:", dni),
            ("Nombre:", f"{nombre} {apellido}"),
            ("Nivel:", nivel),
            ("Curso:", curso if curso else "—"),  # Si está vacío muestra "—"
            ("Fecha de ingreso:", fecha_ingreso if fecha_ingreso else "—"),
            ("Fecha de egreso:", fecha_egreso if fecha_egreso else "—"),
            ("Estado:", estado),
        ]
        for etiqueta, valor in datos:  # Recorre la lista y crea una fila por cada dato
            fila_texto = tk.Frame(marco_ficha, bg="#ffffff")  # Contenedor de una línea
            fila_texto.pack(fill="x", padx=10, pady=2)  # Se estira horizontalmente
            tk.Label(fila_texto, text=etiqueta, bg="#ffffff",  # Etiqueta en negrita
                     font=("Arial", 10, "bold"), width=17, anchor="w").pack(side="left")  # Alineada a la izquierda
            tk.Label(fila_texto, text=valor, bg="#ffffff",  # Valor del dato
                     font=("Arial", 10), anchor="w").pack(side="left")  # Alineado a la izquierda

    ttk.Button(ventana_buscar, text="Buscar", command=realizar_busqueda).pack(pady=5)  # Botón que ejecuta la búsqueda
    ttk.Button(ventana_buscar, text="Cerrar", command=ventana_buscar.destroy).pack(pady=5)  # Botón que cierra la ventana

# ============================================================
# VENTANA: REGISTRAR NUEVO ALUMNO
# ============================================================
def abrir_registrar():
    ventana_registrar = tk.Toplevel(ventana)  # Crea una ventana secundaria
    ventana_registrar.title("Registrar nuevo alumno")  # Título
    ventana_registrar.geometry("1000x900")  # Tamaño
    ventana_registrar.configure(bg="#f7f7f7")  # Fondo gris claro

    # --- Campos de texto ---
    marco_texto = tk.Frame(ventana_registrar, bg="#f7f7f7")  # Contenedor de los campos
    marco_texto.pack(pady=10)

    campos_texto = ["DNI", "Nombre", "Apellido", "Curso",  # Lista de campos que se pedirán
                    "Fecha de ingreso (DD/MM/AAAA)", "Fecha de egreso (DD/MM/AAAA)"]
    entradas = {}  # Diccionario: guarda cada Entry asociado a su nombre de campo
    for campo in campos_texto:  # Crea un campo por cada elemento de la lista
        fila = tk.Frame(marco_texto, bg="#f7f7f7")  # Fila contenedora
        fila.pack(fill="x", padx=30, pady=4)  # Se estira horizontalmente
        tk.Label(fila, text=campo + ":", bg="#f7f7f7",  # Etiqueta con el nombre del campo
                 font=("Arial", 10), width=28, anchor="w").pack(side="left")  # Alineada a la izquierda
        entrada = tk.Entry(fila, width=18, font=("Arial", 10))  # Campo de texto
        entrada.pack(side="left")  # Se coloca al lado de la etiqueta
        entradas[campo] = entrada  # Guardamos la entrada para leerla después

    # --- Menú desplegable: Nivel ---
    tk.Label(ventana_registrar, text="Nivel:", bg="#f7f7f7",  # Etiqueta
             font=("Arial", 10)).pack(pady=(10, 0))
    nivel_var = tk.StringVar(value="Secundaria")  # Variable que guarda la selección del menú
    ttk.Combobox(ventana_registrar, textvariable=nivel_var, state="readonly",  # Menú desplegable (solo lectura)
                 values=["Secundaria"], width=20).pack(pady=3)  # Opciones disponibles

    # --- Menú desplegable: Estado ---
    tk.Label(ventana_registrar, text="Estado:", bg="#f7f7f7",  # Etiqueta
             font=("Arial", 10)).pack(pady=(10, 0))
    estado_var = tk.StringVar(value="Cursando")  # Variable que guarda la selección
    ttk.Combobox(ventana_registrar, textvariable=estado_var, state="readonly",  # Menú desplegable
                 values=["Cursando", "Egreso", "Abandono"], width=20).pack(pady=3)  # Opciones

    def convertir_fecha(texto):
        """Convierte DD/MM/AAAA a AAAA-MM-DD para guardar, o None si está vacío."""
        texto = texto.strip()  # Quita espacios
        if not texto:  # Si está vacío, no hay fecha
            return None
        partes = texto.split("/")  # Separa por la barra: ['DD', 'MM', 'AAAA']
        if len(partes) != 3:  # Si no tiene 3 partes, es inválido
            return None
        dia, mes, anio = partes  # Desempaqueta las partes
        if len(dia) == 2 and len(mes) == 2 and len(anio) == 4:  # Valida la longitud de cada parte
            return f"{anio}-{mes}-{dia}"  # Formato estándar para la base
        return None  # Si no cumple, devuelve None

    def guardar():
        dni = entradas["DNI"].get().strip()  # Lee y limpia el campo DNI
        nombre = entradas["Nombre"].get().strip()  # Lee el campo Nombre
        apellido = entradas["Apellido"].get().strip()  # Lee el campo Apellido
        curso = entradas["Curso"].get().strip()  # Lee el campo Curso
        fecha_ingreso = convertir_fecha(entradas["Fecha de ingreso (DD/MM/AAAA)"].get())  # Convierte la fecha de ingreso
        fecha_egreso = convertir_fecha(entradas["Fecha de egreso (DD/MM/AAAA)"].get())  # Convierte la fecha de egreso
        nivel = nivel_var.get()  # Lee el valor del combo de nivel
        estado = estado_var.get()  # Lee el valor del combo de estado

        if not dni or not nombre or not apellido:  # Valida que los obligatorios estén completos
            messagebox.showwarning("Aviso", "DNI, Nombre y Apellido son obligatorios.",  # Aviso
                                   parent=ventana_registrar)
            return  # Sale sin guardar

        try:
            cursor.execute("""  # INSERT agrega una fila nueva
                INSERT INTO alumnos (dni, nombre, apellido, nivel, curso,
                                     fecha_ingreso, fecha_egreso, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)  # Los ? son marcadores de posición (evitan inyección SQL)
            """, (dni, nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado))  # Valores en tupla
            conexion.commit()  # Guarda los cambios de forma permanente
            messagebox.showinfo("Éxito", "Alumno registrado correctamente.", parent=ventana_registrar)  # Confirmación
            ventana_registrar.destroy()  # Cierra la ventana tras guardar
        except sqlite3.IntegrityError:  # Este error ocurre si el DNI ya existe (columna UNIQUE)
            messagebox.showerror("Error", "Ya existe un alumno con ese DNI.", parent=ventana_registrar)  # Error

    ttk.Button(ventana_registrar, text="Guardar", command=guardar).pack(pady=10)  # Botón que guarda
    ttk.Button(ventana_registrar, text="Cerrar", command=ventana_registrar.destroy).pack(pady=5)  # Botón que cierra

# ============================================================
# VENTANA: MODIFICAR ALUMNO
# ============================================================
def abrir_modificar():
    ventana_modificar = tk.Toplevel(ventana)  # Crea una ventana secundaria
    ventana_modificar.title("Modificar alumno")  # Título
    ventana_modificar.geometry("1000x900")  # Tamaño
    ventana_modificar.configure(bg="#f7f7f7")  # Fondo gris claro

    tk.Label(ventana_modificar, text="Ingrese el DNI del alumno a modificar:",  # Instrucción
             bg="#f7f7f7", font=("Arial", 11)).pack(pady=15)
    entrada_dni = tk.Entry(ventana_modificar, width=25, font=("Arial", 12))  # Campo para el DNI
    entrada_dni.pack()

    campos_texto = ["Nombre", "Apellido", "Curso",  # Campos que se podrán modificar
                    "Fecha de ingreso (DD/MM/AAAA)", "Fecha de egreso (DD/MM/AAAA)"]
    entradas = {}  # Diccionario de entradas
    marco_formulario = tk.Frame(ventana_modificar, bg="#f7f7f7")  # Contenedor del formulario
    marco_formulario.pack(pady=10)

    nivel_var = tk.StringVar()  # Variable para el nivel
    estado_var = tk.StringVar()  # Variable para el estado

    def convertir_fecha_bd(texto):
        """Convierte AAAA-MM-DD (de la base) a DD/MM/AAAA para mostrar."""
        if not texto:  # Si está vacío
            return ""
        partes = texto.split("-")  # Separa por guiones: ['AAAA', 'MM', 'DD']
        if len(partes) == 3:  # Si tiene 3 partes
            return f"{partes[2]}/{partes[1]}/{partes[0]}"  # Reordena a DD/MM/AAAA
        return texto  # Si no, devuelve el texto tal cual

    def cargar_datos():
        for widget in marco_formulario.winfo_children():  # Recorre los widgets del formulario
            widget.destroy()  # Limpia el formulario de un intento anterior
        entradas.clear()  # Vacía el diccionario de entradas

        dni = entrada_dni.get().strip()  # Lee el DNI ingresado
        if not dni:  # Si está vacío
            messagebox.showwarning("Aviso", "Ingrese un DNI.", parent=ventana_modificar)  # Aviso
            return  # Sale

        cursor.execute("SELECT * FROM alumnos WHERE dni = ?", (dni,))  # Busca el alumno por DNI
        fila = cursor.fetchone()  # Obtiene la fila

        if fila is None:  # Si no existe
            messagebox.showerror("Error", "No se encontró ningún alumno con ese DNI.",  # Error
                                 parent=ventana_modificar)
            return  # Sale

        ventana_modificar.fila_actual = fila  # Guarda la fila actual en la ventana para usarla al guardar

        # fila: id, dni, nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado
        valores_actuales = [fila[2], fila[3], fila[5],  # Lista con los valores actuales (nombre, apellido, curso)
                            convertir_fecha_bd(fila[6]), convertir_fecha_bd(fila[7])]  # y las fechas convertidas

        for i, campo in enumerate(campos_texto):  # Crea los campos con los valores actuales precargados
            fila_campo = tk.Frame(marco_formulario, bg="#f7f7f7")  # Fila contenedora
            fila_campo.pack(fill="x", padx=20, pady=3)  # Se estira horizontalmente
            tk.Label(fila_campo, text=campo + ":", bg="#f7f7f7",  # Etiqueta
                     font=("Arial", 10), width=28, anchor="w").pack(side="left")
            entrada = tk.Entry(fila_campo, width=18, font=("Arial", 10))  # Campo de texto
            entrada.insert(0, valores_actuales[i] if valores_actuales[i] else "")  # Precarga el valor actual
            entrada.pack(side="left")  # Se coloca al lado de la etiqueta
            entradas[campo] = entrada  # Guarda la entrada

        # Menús desplegables con el valor actual
        nivel_var.set(fila[4])  # Carga el nivel actual en el combo
        estado_var.set(fila[8])  # Carga el estado actual en el combo

        tk.Label(marco_formulario, text="Nivel:", bg="#f7f7f7",  # Etiqueta
                 font=("Arial", 10)).pack(pady=(10, 0))
        ttk.Combobox(marco_formulario, textvariable=nivel_var, state="readonly",  # Menú de nivel
                     values=["Secundaria"], width=18).pack(pady=3)  # Solo secundaria


        tk.Label(marco_formulario, text="Estado:", bg="#f7f7f7",  # Etiqueta
                 font=("Arial", 10)).pack(pady=(10, 0))
        ttk.Combobox(marco_formulario, textvariable=estado_var, state="readonly",  # Menú de estado
                     values=["Cursando", "Egreso", "Abandono"], width=18).pack(pady=3)  # Opciones

    def convertir_fecha(texto):
        """Convierte DD/MM/AAAA a AAAA-MM-DD para guardar."""
        texto = texto.strip()  # Quita espacios
        if not texto:  # Si está vacío
            return None
        partes = texto.split("/")  # Separa por barras
        if len(partes) != 3:  # Si no tiene 3 partes
            return None
        dia, mes, anio = partes  # Desempaqueta
        if len(dia) == 2 and len(mes) == 2 and len(anio) == 4:  # Valida longitudes
            return f"{anio}-{mes}-{dia}"  # Formato para la base
        return None

    def guardar_cambios():
        if not hasattr(ventana_modificar, "fila_actual"):  # Verifica que se haya cargado un alumno antes
            messagebox.showwarning("Aviso", "Primero cargue el alumno por DNI.",  # Aviso
                                   parent=ventana_modificar)
            return  # Sale
        fila = ventana_modificar.fila_actual  # Recupera la fila original

        nombre = entradas["Nombre"].get().strip() or fila[2]  # Si está vacío, conserva el valor anterior
        apellido = entradas["Apellido"].get().strip() or fila[3]  # Igual para apellido
        curso = entradas["Curso"].get().strip() or fila[5]  # Igual para curso
        fecha_ingreso_texto = entradas["Fecha de ingreso (DD/MM/AAAA)"].get().strip()  # Lee la fecha de ingreso
        fecha_ingreso = convertir_fecha(fecha_ingreso_texto) if fecha_ingreso_texto else fila[6]  # Convierte o conserva
        fecha_egreso_texto = entradas["Fecha de egreso (DD/MM/AAAA)"].get().strip()  # Lee la fecha de egreso
        fecha_egreso = convertir_fecha(fecha_egreso_texto) if fecha_egreso_texto else fila[7]  # Convierte o conserva
        nivel = nivel_var.get() or fila[4]  # Conserva el nivel anterior si está vacío
        estado = estado_var.get() or fila[8]  # Conserva el estado anterior si está vacío

        cursor.execute("""  # UPDATE modifica las columnas indicadas
            UPDATE alumnos
            SET nombre = ?, apellido = ?, nivel = ?, curso = ?,
                fecha_ingreso = ?, fecha_egreso = ?, estado = ?
            WHERE dni = ?  # El WHERE es clave: sin él se modificarían TODOS los registros
        """, (nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado, fila[1]))  # Valores
        conexion.commit()  # Guarda los cambios
        messagebox.showinfo("Éxito", "Datos actualizados correctamente.", parent=ventana_modificar)  # Confirmación
        ventana_modificar.destroy()  # Cierra la ventana

    ttk.Button(ventana_modificar, text="Cargar datos", command=cargar_datos).pack(pady=5)  # Botón que carga el alumno
    ttk.Button(ventana_modificar, text="Guardar cambios", command=guardar_cambios).pack(pady=5)  # Botón que guarda
    ttk.Button(ventana_modificar, text="Cerrar", command=ventana_modificar.destroy).pack(pady=5)  # Botón que cierra

# ============================================================
# VENTANA PRINCIPAL
# ============================================================
ventana = tk.Tk()  # Crea la ventana raíz de la aplicación
ventana.title("Sistema de Certificados de Alumno Regular")  # Título de la ventana
ventana.geometry("1000x950")  # Tamaño
ventana.configure(bg="#f7f7f7")  # Fondo gris claro

imagen_logo = Image.open("imagen/logo.jpg")  # Carga el archivo del logo
imagen_logo = imagen_logo.resize((140, 140))  # Redimensiona el logo a 140x140 píxeles
logo = ImageTk.PhotoImage(imagen_logo)  # Convierte la imagen para que Tkinter pueda mostrarla
tk.Label(ventana, image=logo, bg="#f7f7f7").pack(pady=15)  # Muestra el logo

tk.Label(ventana, text="SISTEMA DE CERTIFICADOS", font=("Arial", 16, "bold"),  # Título principal en negrita
         bg="#f7f7f7", fg="#2c3e50").pack()
tk.Label(ventana, text="Centro Educativo ESC. N°382 - EPET N°28FP",  # Subtítulo
         font=("Arial", 10), bg="#f7f7f7", fg="#34495e").pack()
tk.Label(ventana, text='"Educación para la Vida"',  # Lema en cursiva
         font=("Arial", 10, "italic"), bg="#f7f7f7", fg="#7f8c8d").pack(pady=(0, 15))

estilo = ttk.Style()  # Crea un estilo personalizado
estilo.configure("Menu.TButton", font=("Arial", 12), padding=10)  # Define fuente y padding de los botones del menú

ttk.Button(ventana, text="🔍  Buscar alumno por DNI",  # Botón que abre la ventana de búsqueda
           style="Menu.TButton", command=abrir_buscar).pack(pady=6, ipadx=40)
ttk.Button(ventana, text="➕  Registrar nuevo alumno",  # Botón que abre la ventana de registro
           style="Menu.TButton", command=abrir_registrar).pack(pady=6, ipadx=40)
ttk.Button(ventana, text="✏️  Modificar alumno",  # Botón que abre la ventana de modificación
           style="Menu.TButton", command=abrir_modificar).pack(pady=6, ipadx=40)
ttk.Button(ventana, text="Salir",  # Botón que cierra la aplicación
           style="Menu.TButton", command=ventana.quit).pack(pady=15, ipadx=40)

ventana.mainloop()  # Mantiene la ventana abierta y a la escucha de eventos (clics, teclas)

cursor.close()  # Al cerrar, cierra el cursor para liberar recursos
conexion.close()  # Cierra la conexión con la base de datos

