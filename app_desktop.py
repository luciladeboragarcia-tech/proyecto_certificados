import sqlite3   # Permite conectarse y trabajar con la base de datos SQLite
import tkinter as tk  # Librería estándar de Python para crear interfaces gráficas
from tkinter import ttk, messagebox  # ttk: widgets modernos | messagebox: ventanas de aviso
from PIL import Image, ImageTk  # Pillow: para cargar y mostrar imágenes (el logo)
import os  # Para abrir el PDF generado
import datetime  # Para obtener la fecha actual
from reportlab.lib.pagesizes import A4  # Tamaño de hoja A4 para el PDF
from reportlab.lib.units import mm  # Unidad de medida en milímetros
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ImagenPDF  # Elementos del PDF
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT  # Alineaciones de texto

# ============================================================
# CONEXIÓN A LA BASE DE DATOS
# ============================================================
# sqlite3.connect() abre (o crea si no existe) el archivo de la
# base de datos. Sin conexión no se puede guardar ni consultar nada.
conexion = sqlite3.connect("alumnos.db")
cursor = conexion.cursor()  # El cursor es el "lápiz" que ejecuta las instrucciones SQL

# ============================================================
# CREACIÓN DE LA TABLA (si no existe)
# ============================================================
# Crea la tabla "alumnos". IF NOT EXISTS evita que falle si ya existe.
cursor.execute("""
CREATE TABLE IF NOT EXISTS alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    nivel TEXT NOT NULL,
    curso TEXT,
    fecha_ingreso TEXT,
    fecha_egreso TEXT,
    estado TEXT NOT NULL
)
""")
conexion.commit()  # Guarda los cambios de forma permanente

# ============================================================
# FUNCIÓN: GENERAR E IMPRIMIR CONSTANCIA
# ============================================================
def generar_constancia(fila, tipo_constancia):
    """
    Genera un PDF con la constancia del alumno en formato oficial
    y lo abre para imprimir.
    fila: tupla con los datos del alumno (id, dni, nombre, apellido,
          nivel, curso, fecha_ingreso, fecha_egreso, estado)
    tipo_constancia: "pase", "regular" o "vacante"
    """
    id, dni, nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado = fila
    nombre_completo = f"{apellido}, {nombre}"  # Orden oficial: Apellido, Nombre

    # Título y cuerpo según el tipo de constancia
    if tipo_constancia == "pase":
        titulo = "CONSTANCIA DE PASE EN TRÁMITE"
        cuerpo = (
            "Por la presente se hace constar que: <b>{nombre}</b> – "
            "<b>DNI N° {dni}</b> ha cursado el <b>{curso}</b> del secundario "
            "en la EPET N° 28 en la Tecnicatura en Mecanización Agropecuaria, "
            "hasta el {fecha_egreso}.<br/><br/>"
            "Se deja constancia de que el pase definitivo se encuentra en trámite."
        )
        pie = "Pje. Gentil, San Pedro, {fecha_texto}."
    elif tipo_constancia == "regular":
        titulo = "CONSTANCIA DE ALUMNO REGULAR"
        cuerpo = (
            "Por la presente se deja constancia que: <b>{nombre}</b> – "
            "<b>DNI N° {dni}</b> es alumno/a regular del <b>{curso}</b>, "
            "en ésta Institución Educativa.<br/><br/>"
            "Se expide la presente a pedido de la interesada, para ser "
            "presentada ante las autoridades que la requieran."
        )
        pie = "Pje. Gentil, San Pedro, Misiones; {fecha_texto}.-"
    else:  # vacante
        titulo = "CONSTANCIA DE VACANTE"
        cuerpo = (
            "La EPET Nº 28 de Paraje Gentil, San Pedro, informa que la "
            "institución cuenta con vacante para la inscripción de la "
            "alumna, <b>{nombre}</b> – <b>DNI N° {dni}</b> en "
            "<b>{curso}</b> secundaria técnica, orientación Mecanización "
            "Agropecuaria, ciclo lectivo {anio_actual}.<br/><br/>"
            "Se extiende la presente a pedido de la interesada."
        )
        pie = "Pje. Gentil, San Pedro, {fecha_texto}.-"

    dni_formateado = f"{int(dni):,}".replace(",", ".")  # Formatea el DNI con puntos
    hoy = datetime.date.today()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    fecha_texto = f"a los {hoy.day} días del mes de {meses[hoy.month - 1]} del {hoy.year}"

    texto_cuerpo = cuerpo.format(
        nombre=nombre_completo, dni=dni_formateado,
        curso=curso if curso else "—",
        fecha_egreso=fecha_egreso if fecha_egreso else "la fecha",
        anio_actual=hoy.year
    )
    texto_pie = pie.format(fecha_texto=fecha_texto)

    nombre_archivo = f"constancia_{tipo_constancia}_{dni}.pdf"
    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4,
                            leftMargin=30*mm, rightMargin=30*mm,
                            topMargin=30*mm, bottomMargin=30*mm)

    estilos = getSampleStyleSheet()
    estilo_encabezado = ParagraphStyle(
        "Encabezado", parent=estilos["BodyText"],
        alignment=TA_LEFT, fontSize=11, leading=14, spaceAfter=2)
    estilo_titulo = ParagraphStyle(
        "TituloCentrado", parent=estilos["Title"],
        alignment=TA_CENTER, fontSize=16, bold=True, spaceBefore=20, spaceAfter=20)
    estilo_cuerpo = ParagraphStyle(
        "CuerpoJustificado", parent=estilos["BodyText"],
        alignment=TA_JUSTIFY, fontSize=12, leading=18)
    estilo_fecha = ParagraphStyle(
        "Fecha", parent=estilos["BodyText"],
        alignment=TA_JUSTIFY, fontSize=12, leading=18, spaceBefore=20)
    estilo_firma = ParagraphStyle(
        "Firma", parent=estilos["BodyText"],
        alignment=TA_CENTER, fontSize=12, spaceBefore=80)
    # Carga las imágenes (escudo, fundación y firma)
    escudo = None
    fundacion = None
    firma = None
    try:
        escudo = ImagenPDF("imagen/escudo.jpg", width=10*mm, height=10*mm, hAlign="LEFT")
    except Exception:
        escudo = None
    try:
        fundacion = ImagenPDF("imagen/fundacion.jpg", width=60*mm, height=25*mm, hAlign="RIGHT")
    except Exception:
        fundacion = None
    try:
        firma = ImagenPDF("imagen/firma.jpg", width=60*mm, height=30*mm, hAlign="CENTER")
    except Exception:
        firma = None

    contenido = []
    if escudo is not None:
        contenido.append(escudo)          # Escudo arriba
        contenido.append(Spacer(1, 10))
    if fundacion is not None:
        contenido.append(fundacion)       # Fundación debajo del escudo
        contenido.append(Spacer(1, 10))
    contenido.append(Paragraph("Provincia de Misiones.", estilo_encabezado))
    contenido.append(Paragraph("Consejo General de Educación.", estilo_encabezado))
    contenido.append(Paragraph("Dirección de Educación Técnica.", estilo_encabezado))
    contenido.append(Paragraph("EPET Nº 28 – Anexo F. P. – 2° Categoría – Zona “C”.", estilo_encabezado))
    contenido.append(Spacer(1, 20))
    contenido.append(Paragraph(titulo, estilo_titulo))
    contenido.append(Spacer(1, 20))
    contenido.append(Paragraph(texto_cuerpo, estilo_cuerpo))
    contenido.append(Spacer(1, 20))
    contenido.append(Paragraph(texto_pie, estilo_fecha))

    if firma is not None:
        contenido.append(Spacer(1, 10))
        contenido.append(firma)           # Firma y sello al final
    doc.build(contenido)
    os.startfile(nombre_archivo)  # Abre el PDF para imprimir
    messagebox.showinfo("Constancia", "Constancia generada correctamente. Revise el PDF para imprimir.")
# ============================================================
# VENTANA: ELEGIR TIPO DE CONSTANCIA
# ============================================================
def elegir_constancia(fila):
    """Abre una ventana con las 3 opciones de constancia para el alumno buscado."""
    ventana_constancia = tk.Toplevel(ventana)
    ventana_constancia.title("Elegir tipo de constancia")
    ventana_constancia.geometry("400x300")
    ventana_constancia.configure(bg="#f7f7f7")

    tk.Label(ventana_constancia, text="Seleccione el tipo de constancia:",
             bg="#f7f7f7", font=("Arial", 12)).pack(pady=20)

    ttk.Button(ventana_constancia, text="📄 Constancia de Pase",
               command=lambda: generar_constancia(fila, "pase")).pack(pady=8, ipadx=20, ipady=5)
    ttk.Button(ventana_constancia, text="📄 Constancia de Alumno Regular",
               command=lambda: generar_constancia(fila, "regular")).pack(pady=8, ipadx=20, ipady=5)
    ttk.Button(ventana_constancia, text="📄 Constancia de Vacante",
               command=lambda: generar_constancia(fila, "vacante")).pack(pady=8, ipadx=20, ipady=5)
    ttk.Button(ventana_constancia, text="Cerrar",
               command=ventana_constancia.destroy).pack(pady=15)

# ============================================================
# VENTANA: BUSCAR ALUMNO POR DNI
# ============================================================
def abrir_buscar():
    ventana_buscar = tk.Toplevel(ventana)  # Crea una ventana secundaria encima de la principal
    ventana_buscar.title("Buscar alumno por DNI")
    ventana_buscar.geometry("500x550")
    ventana_buscar.configure(bg="#f7f7f7")

    tk.Label(ventana_buscar, text="Ingrese el DNI a buscar:",
             bg="#f7f7f7", font=("Arial", 11)).pack(pady=15)
    entrada_dni = tk.Entry(ventana_buscar, width=25, font=("Arial", 12))
    entrada_dni.pack()

    marco_ficha = tk.Frame(ventana_buscar, bg="#ffffff", relief="groove", bd=2)
    marco_ficha.pack(pady=20, padx=20, fill="both", expand=True)

    def realizar_busqueda():
        for widget in marco_ficha.winfo_children():  # Limpia la ficha anterior
            widget.destroy()

        dni = entrada_dni.get().strip()
        if not dni:  # Si el campo está vacío
            messagebox.showwarning("Aviso", "Ingrese un DNI.", parent=ventana_buscar)
            return
        if not dni.isdigit():  # Valida que el DNI sea numérico
            messagebox.showwarning("Aviso", "El DNI debe ser numérico.", parent=ventana_buscar)
            return
        cursor.execute("SELECT * FROM alumnos WHERE dni = ?", (dni,))  # El ? evita inyección SQL
        fila = cursor.fetchone()

        if fila is None:  # No se encontró ningún alumno
            tk.Label(marco_ficha, text="No se encontró ningún alumno con ese DNI.",
                     bg="#ffffff", fg="red").pack(pady=20)
            return

        id, dni, nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado = fila

        datos = [
            ("DNI:", dni),
            ("Nombre:", f"{nombre} {apellido}"),
            ("Nivel:", nivel),
            ("Curso:", curso if curso else "—"),
            ("Fecha de ingreso:", fecha_ingreso if fecha_ingreso else "—"),
            ("Fecha de egreso:", fecha_egreso if fecha_egreso else "—"),
            ("Estado:", estado),
        ]
        for etiqueta, valor in datos:
            fila_texto = tk.Frame(marco_ficha, bg="#ffffff")
            fila_texto.pack(fill="x", padx=10, pady=2)
            tk.Label(fila_texto, text=etiqueta, bg="#ffffff",
                     font=("Arial", 10, "bold"), width=17, anchor="w").pack(side="left")
            tk.Label(fila_texto, text=valor, bg="#ffffff",
                     font=("Arial", 10), anchor="w").pack(side="left")

        ventana_buscar.fila_actual = fila  # Guarda la fila para imprimir después

    ttk.Button(ventana_buscar, text="Buscar", command=realizar_busqueda).pack(pady=5)
    ttk.Button(ventana_buscar, text="🖨️  Imprimir constancia",
               command=lambda: elegir_constancia(ventana_buscar.fila_actual)
               if hasattr(ventana_buscar, "fila_actual")
               else messagebox.showwarning("Aviso", "Primero busque un alumno por DNI.", parent=ventana_buscar)
               ).pack(pady=5)
    ttk.Button(ventana_buscar, text="Cerrar", command=ventana_buscar.destroy).pack(pady=5)

# ============================================================
# VENTANA: REGISTRAR NUEVO ALUMNO
# ============================================================
def abrir_registrar():
    ventana_registrar = tk.Toplevel(ventana)
    ventana_registrar.title("Registrar nuevo alumno")
    ventana_registrar.geometry("500x500")
    ventana_registrar.configure(bg="#f7f7f7")

    marco_texto = tk.Frame(ventana_registrar, bg="#f7f7f7")
    marco_texto.pack(pady=10)

    campos_texto = ["DNI", "Nombre", "Apellido",
                    "Fecha de ingreso (DD/MM/AAAA)", "Fecha de egreso (DD/MM/AAAA)"]
    entradas = {}
    for campo in campos_texto:
        fila = tk.Frame(marco_texto, bg="#f7f7f7")
        fila.pack(fill="x", padx=30, pady=4)
        tk.Label(fila, text=campo + ":", bg="#f7f7f7",
                 font=("Arial", 10), width=28, anchor="w").pack(side="left")
        entrada = tk.Entry(fila, width=18, font=("Arial", 10))
        entrada.pack(side="left")
        entradas[campo] = entrada

    # Nivel: texto fijo
    fila_nivel = tk.Frame(marco_texto, bg="#f7f7f7")
    fila_nivel.pack(fill="x", padx=30, pady=4)
    tk.Label(fila_nivel, text="Nivel:", bg="#f7f7f7",
             font=("Arial", 10), width=28, anchor="w").pack(side="left")
    tk.Label(fila_nivel, text="Secundaria", bg="#f7f7f7",
             font=("Arial", 10), width=18, anchor="w").pack(side="left")

    # Curso: menú desplegable
    fila_curso = tk.Frame(marco_texto, bg="#f7f7f7")
    fila_curso.pack(fill="x", padx=30, pady=4)
    tk.Label(fila_curso, text="Curso:", bg="#f7f7f7",
             font=("Arial", 10), width=28, anchor="w").pack(side="left")
    curso_var = tk.StringVar(value="1 año")
    ttk.Combobox(fila_curso, textvariable=curso_var, state="readonly",
                 values=["1 año", "2 año", "3 año", "4 año", "5 año", "6 año"],
                 width=17).pack(side="left")

    # Estado: menú desplegable
    fila_estado = tk.Frame(marco_texto, bg="#f7f7f7")
    fila_estado.pack(fill="x", padx=30, pady=4)
    tk.Label(fila_estado, text="Estado:", bg="#f7f7f7",
             font=("Arial", 10), width=28, anchor="w").pack(side="left")
    estado_var = tk.StringVar(value="Cursando")
    ttk.Combobox(fila_estado, textvariable=estado_var, state="readonly",
                 values=["Cursando", "Egreso", "Abandono"],
                 width=17).pack(side="left")

    def convertir_fecha(texto):
        """Convierte DD/MM/AAAA a AAAA-MM-DD para guardar, o None si está vacío."""
        texto = texto.strip()
        if not texto:
            return None
        partes = texto.split("/")
        if len(partes) != 3:
            return None
        dia, mes, anio = partes
        if len(dia) == 2 and len(mes) == 2 and len(anio) == 4:
            return f"{anio}-{mes}-{dia}"
        return None

    def guardar():
        dni = entradas["DNI"].get().strip()
        nombre = entradas["Nombre"].get().strip()
        apellido = entradas["Apellido"].get().strip()
        curso = curso_var.get()
        fecha_ingreso = convertir_fecha(entradas["Fecha de ingreso (DD/MM/AAAA)"].get())
        fecha_egreso = convertir_fecha(entradas["Fecha de egreso (DD/MM/AAAA)"].get())
        nivel = "Secundaria"  # Nivel fijo
        estado = estado_var.get()

        if not dni or not nombre or not apellido:  # Valida obligatorios
            messagebox.showwarning("Aviso", "DNI, Nombre y Apellido son obligatorios.",
                                   parent=ventana_registrar)
            return
        if not dni.isdigit():
            messagebox.showwarning("Aviso", "El DNI debe ser numérico.", parent=ventana_registrar)
            return
        cursor.execute("SELECT * FROM alumnos WHERE dni = ?", (dni,))
        if cursor.fetchone() is not None:  # DNI duplicado
            messagebox.showerror("Error", "Ya existe un alumno con ese DNI.", parent=ventana_registrar)
            return
        if estado in ["Egreso", "Abandono"] and not fecha_egreso:
            messagebox.showwarning("Aviso", "La fecha de egreso es obligatoria para alumnos en estado 'Egreso' o 'Abandono'.", parent=ventana_registrar)
            return
        try:
            cursor.execute("""
                INSERT INTO alumnos (dni, nombre, apellido, nivel, curso,
                                     fecha_ingreso, fecha_egreso, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (dni, nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado))
            conexion.commit()
            messagebox.showinfo("Éxito", "Alumno registrado correctamente.", parent=ventana_registrar)
            ventana_registrar.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un alumno con ese DNI.", parent=ventana_registrar)
            return

    ttk.Button(ventana_registrar, text="Guardar", command=guardar).pack(pady=10)
    ttk.Button(ventana_registrar, text="Cerrar", command=ventana_registrar.destroy).pack(pady=5)

# ============================================================
# VENTANA: MODIFICAR ALUMNO
# ============================================================
def abrir_modificar():
    ventana_modificar = tk.Toplevel(ventana)
    ventana_modificar.title("Modificar alumno")
    ventana_modificar.geometry("500x500")
    ventana_modificar.configure(bg="#f7f7f7")

    tk.Label(ventana_modificar, text="Ingrese el DNI del alumno a modificar:",
             bg="#f7f7f7", font=("Arial", 11)).pack(pady=15)
    entrada_dni = tk.Entry(ventana_modificar, width=25, font=("Arial", 12))
    entrada_dni.pack()

    campos_texto = ["Nombre", "Apellido",
                    "Fecha de ingreso (DD/MM/AAAA)", "Fecha de egreso (DD/MM/AAAA)"]
    entradas = {}
    marco_formulario = tk.Frame(ventana_modificar, bg="#f7f7f7")
    marco_formulario.pack(pady=10)

    nivel_var = tk.StringVar()
    curso_var = tk.StringVar()
    estado_var = tk.StringVar()

    def convertir_fecha_bd(texto):
        """Convierte AAAA-MM-DD (de la base) a DD/MM/AAAA para mostrar."""
        if not texto:
            return ""
        partes = texto.split("-")
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        return texto

    def cargar_datos():
        for widget in marco_formulario.winfo_children():
            widget.destroy()
        entradas.clear()

        dni = entrada_dni.get().strip()
        if not dni:
            messagebox.showwarning("Aviso", "Ingrese un DNI.", parent=ventana_modificar)
            return
        if not dni.isdigit():
            messagebox.showwarning("Aviso", "El DNI debe ser numérico.", parent=ventana_modificar)
            return
        cursor.execute("SELECT * FROM alumnos WHERE dni = ?", (dni,))
        fila = cursor.fetchone()

        if fila is None:
            messagebox.showerror("Error", "No se encontró ningún alumno con ese DNI.",
                                 parent=ventana_modificar)
            return

        ventana_modificar.fila_actual = fila  # Guarda la fila para guardar después

        valores_actuales = [fila[2], fila[3],
                            convertir_fecha_bd(fila[6]), convertir_fecha_bd(fila[7])]

        for i, campo in enumerate(campos_texto):
            fila_campo = tk.Frame(marco_formulario, bg="#f7f7f7")
            fila_campo.pack(fill="x", padx=20, pady=3)
            tk.Label(fila_campo, text=campo + ":", bg="#f7f7f7",
                     font=("Arial", 10), width=28, anchor="w").pack(side="left")
            entrada = tk.Entry(fila_campo, width=18, font=("Arial", 10))
            entrada.insert(0, valores_actuales[i] if valores_actuales[i] else "")
            entrada.pack(side="left")
            entradas[campo] = entrada

        # Nivel: texto fijo
        fila_nivel = tk.Frame(marco_formulario, bg="#f7f7f7")
        fila_nivel.pack(fill="x", padx=20, pady=3)
        tk.Label(fila_nivel, text="Nivel:", bg="#f7f7f7",
                 font=("Arial", 10), width=28, anchor="w").pack(side="left")
        tk.Label(fila_nivel, text="Secundaria", bg="#f7f7f7",
                 font=("Arial", 10), width=18, anchor="w").pack(side="left")

        # Curso: menú desplegable
        fila_curso = tk.Frame(marco_formulario, bg="#f7f7f7")
        fila_curso.pack(fill="x", padx=20, pady=3)
        tk.Label(fila_curso, text="Curso:", bg="#f7f7f7",
                 font=("Arial", 10), width=28, anchor="w").pack(side="left")
        curso_var.set(fila[5] if fila[5] else "1 año")
        ttk.Combobox(fila_curso, textvariable=curso_var, state="readonly",
                     values=["1 año", "2 año", "3 año", "4 año", "5 año", "6 año"],
                     width=17).pack(side="left")

        # Estado: menú desplegable
        fila_estado = tk.Frame(marco_formulario, bg="#f7f7f7")
        fila_estado.pack(fill="x", padx=20, pady=3)
        tk.Label(fila_estado, text="Estado:", bg="#f7f7f7",
                 font=("Arial", 10), width=28, anchor="w").pack(side="left")
        estado_var.set(fila[8])
        ttk.Combobox(fila_estado, textvariable=estado_var, state="readonly",
                     values=["Cursando", "Egreso", "Abandono"],
                     width=17).pack(side="left")

    def convertir_fecha(texto):
        """Convierte DD/MM/AAAA a AAAA-MM-DD para guardar."""
        texto = texto.strip()
        if not texto:
            return None
        partes = texto.split("/")
        if len(partes) != 3:
            return None
        dia, mes, anio = partes
        if len(dia) == 2 and len(mes) == 2 and len(anio) == 4:
            return f"{anio}-{mes}-{dia}"
        return None

    def guardar_cambios():
        if not hasattr(ventana_modificar, "fila_actual"):
            messagebox.showwarning("Aviso", "Primero cargue el alumno con su DNI.", parent=ventana_modificar)
            return
        dni = ventana_modificar.fila_actual[1]  # El DNI no se puede cambiar
        nombre = entradas["Nombre"].get().strip()
        apellido = entradas["Apellido"].get().strip()
        curso = curso_var.get()
        fecha_ingreso = convertir_fecha(entradas["Fecha de ingreso (DD/MM/AAAA)"].get())
        fecha_egreso = convertir_fecha(entradas["Fecha de egreso (DD/MM/AAAA)"].get())
        nivel = "Secundaria"  # Nivel fijo
        estado = estado_var.get()

        if not nombre or not apellido:
            messagebox.showwarning("Aviso", "Nombre y Apellido son obligatorios.", parent=ventana_modificar)
            return
        try:
            cursor.execute("""
                UPDATE alumnos
                SET nombre = ?, apellido = ?, nivel = ?, curso = ?,
                    fecha_ingreso = ?, fecha_egreso = ?, estado = ?
                WHERE dni = ?
            """, (nombre, apellido, nivel, curso, fecha_ingreso, fecha_egreso, estado, dni))
            conexion.commit()
            messagebox.showinfo("Éxito", "Datos actualizados correctamente.", parent=ventana_modificar)
            ventana_modificar.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}", parent=ventana_modificar)

    ttk.Button(ventana_modificar, text="Cargar datos", command=cargar_datos).pack(pady=5, ipadx=20, ipady=5)
    ttk.Button(ventana_modificar, text="Guardar cambios", command=guardar_cambios).pack(pady=5, ipadx=20, ipady=5)
    ttk.Button(ventana_modificar, text="Cerrar", command=ventana_modificar.destroy).pack(pady=5, ipadx=20, ipady=5)

# ============================================================
# VENTANA PRINCIPAL
# ============================================================
ventana = tk.Tk()  # Crea la ventana principal
ventana.title("Sistema de Certificados de Alumno Regular")  # Título de la ventana
ventana.geometry("800x700")  # Tamaño
ventana.configure(bg="#f7f7f7")  # Fondo gris claro

# Intenta cargar y mostrar el logo de la institución
try:
    imagen_logo = Image.open("imagen/logo.jpg")  # Abre la imagen del logo
    imagen_logo = imagen_logo.resize((150, 150))  # La redimensiona a 150x150
    logo = ImageTk.PhotoImage(imagen_logo)  # La convierte a un formato que Tkinter entiende
    tk.Label(ventana, image=logo, bg="#f7f7f7").pack(pady=20)  # La muestra en la ventana
except FileNotFoundError:
    pass  # Si no existe el logo, sigue sin mostrar nada

tk.Label(ventana, text="SISTEMA DE CERTIFICADOS",  # Título del sistema
         bg="#f7f7f7", font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(ventana, text="DE ALUMNO REGULAR",  # Subtítulo
         bg="#f7f7f7", font=("Arial", 14, "bold")).pack(pady=5)

# Botones del menú principal
ttk.Button(ventana, text="🔍  Buscar alumno por DNI", command=abrir_buscar).pack(pady=10, ipadx=70, ipady=12)
ttk.Button(ventana, text="➕  Registrar nuevo alumno", command=abrir_registrar).pack(pady=10, ipadx=70, ipady=12)
ttk.Button(ventana, text="✏️  Modificar alumno", command=abrir_modificar).pack(pady=10, ipadx=70, ipady=12)
ttk.Button(ventana, text="Salir", command=ventana.quit).pack(pady=10, ipadx=70, ipady=12)

ventana.mainloop()  # Mantiene la ventana abierta hasta que se cierre

# Al cerrar, libera la base de datos
cursor.close()
conexion.close()