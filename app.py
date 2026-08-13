import sqlite3
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Proyectos y Tareas", page_icon="📊", layout="wide"
)

# --- CONEXIÓN A LA BASE DE DATOS ---
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()


# Crear tablas (Entidad 1: Proyectos | Entidad 2: Tareas)
def crear_tablas():
  c.execute(
      """CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT
            )"""
  )
  c.execute(
      """CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyecto_id INTEGER,
                titulo TEXT NOT NULL,
                estado TEXT,
                FOREIGN KEY(proyecto_id) REFERENCES proyectos(id)
            )"""
  )
  conn.commit()


crear_tablas()

# --- INTERFAZ GRÁFICA ---
st.title("🚀 Aplicación Web con Base de Datos (Opción 3)")
st.write(
    "Simulacro Individual - CRUD con 2 entidades (Proyectos y Tareas) conectado"
    " a base de datos."
)

menu = ["Proyectos", "Tareas", "Vista General"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

# --- ENTIDAD 1: PROYECTOS ---
if choice == "Proyectos":
  st.header("📂 Gestión de Proyectos (Entidad 1)")

  # CREATE (Crear)
  with st.form("form_proyecto"):
    st.subheader("Crear Nuevo Proyecto")
    nombre_p = st.text_input("Nombre del Proyecto")
    desc_p = st.text_area("Descripción")
    submit_p = st.form_submit_button("Guardar Proyecto")
    if submit_p and nombre_p:
      c.execute(
          "INSERT INTO proyectos (nombre, descripcion) VALUES (?, ?)",
          (nombre_p, desc_p),
      )
      conn.commit()
      st.success(f"Proyecto '{nombre_p}' creado con éxito.")

  # READ & DELETE (Leer y Borrar)
  st.subheader("Lista de Proyectos Existentes")
  c.execute("SELECT * FROM proyectos")
  proyectos = c.fetchall()

  if proyectos:
    for p in proyectos:
      col1, col2, col3 = st.columns([3, 4, 2])
      col1.write(f"**ID {p[0]}: {p[1]}**")
      col2.write(f"{p[2]}")

      if col3.button("Eliminar", key=f"del_p_{p[0]}"):
        c.execute("DELETE FROM proyectos WHERE id = ?", (p[0],))
        c.execute("DELETE FROM tareas WHERE proyecto_id = ?", (p[0],))
        conn.commit()
        st.rerun()
  else:
    st.info("No hay proyectos registrados todavía.")

# --- ENTIDAD 2: TAREAS ---
elif choice == "Tareas":
  st.header("📝 Gestión de Tareas (Entidad 2)")

  c.execute("SELECT id, nombre FROM proyectos")
  proyectos_disponibles = c.fetchall()

  if not proyectos_disponibles:
    st.warning(
        "⚠️ Primero debes crear al menos un proyecto en la sección 'Proyectos'."
    )
  else:
    # CREATE (Crear)
    with st.form("form_tarea"):
      st.subheader("Crear Nueva Tarea")
      proyectos_dict = {p[1]: p[0] for p in proyectos_disponibles}
      proj_seleccionado = st.selectbox(
          "Asociar al Proyecto", list(proyectos_dict.keys())
      )
      titulo_t = st.text_input("Título de la Tarea")
      estado_t = st.selectbox(
          "Estado", ["Pendiente", "En Proceso", "Completada"]
      )
      submit_t = st.form_submit_button("Guardar Tarea")

      if submit_t and titulo_t:
        p_id = proyectos_dict[proj_seleccionado]
        c.execute(
            "INSERT INTO tareas (proyecto_id, titulo, estado) VALUES (?, ?, ?)",
            (p_id, titulo_t, estado_t),
        )
        conn.commit()
        st.success(f"Tarea '{titulo_t}' creada con éxito.")

    # READ & DELETE (Leer y Borrar)
    st.subheader("Lista de Tareas Existentes")
    c.execute(
        """SELECT t.id, p.nombre, t.titulo, t.estado 
                 FROM tareas t JOIN proyectos p ON t.proyecto_id = p.id"""
    )
    tareas = c.fetchall()

    if tareas:
      for t in tareas:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        col1.write(f"**Proyecto:** {t[1]}")
        col2.write(f"**Tarea:** {t[2]}")
        col3.write(f"**Estado:** {t[3]}")

        if col4.button("Eliminar", key=f"del_t_{t[0]}"):
          c.execute("DELETE FROM tareas WHERE id = ?", (t[0],))
          conn.commit()
          st.rerun()
    else:
      st.info("No hay tareas registradas todavía.")

# --- VISTA GENERAL ---
elif choice == "Vista General":
  st.header("📊 Resumen General")
  c.execute("SELECT COUNT(*) FROM proyectos")
  total_p = c.fetchone()[0]
  c.execute("SELECT COUNT(*) FROM tareas")
  total_t = c.fetchone()[0]

  col1, col2 = st.columns(2)
  col1.metric("Total de Proyectos", total_p)
  col2.metric("Total de Tareas", total_t)
