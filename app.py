import sqlite3
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Proyectos y Tareas", page_icon="📊", layout="wide"
)

# --- CONEXIÓN A LA BASE DE DATOS ---
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# Crear tablas
def crear_tablas():
    c.execute("""CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyecto_id INTEGER,
                titulo TEXT NOT NULL,
                estado TEXT,
                FOREIGN KEY(proyecto_id) REFERENCES proyectos(id))""")
    conn.commit()

crear_tablas()

st.title("🚀 Aplicación con CRUD Completo")
menu = ["Proyectos", "Tareas", "Vista General"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

# --- ENTIDAD 1: PROYECTOS ---
if choice == "Proyectos":
    st.header("📂 Gestión de Proyectos")
    
    # CREATE
    with st.form("form_proyecto", clear_on_submit=True):
        nombre_p = st.text_input("Nombre del Proyecto")
        desc_p = st.text_area("Descripción")
        if st.form_submit_button("Guardar Proyecto"):
            if nombre_p:
                c.execute("INSERT INTO proyectos (nombre, descripcion) VALUES (?, ?)", (nombre_p, desc_p))
                conn.commit()
                st.success("¡Proyecto guardado con éxito!")
                st.rerun()

    # READ, UPDATE & DELETE
    st.subheader("Lista de Proyectos")
    c.execute("SELECT * FROM proyectos")
    proyectos = c.fetchall()

    if proyectos:
        for p in proyectos:
            col1, col2, col3, col4 = st.columns([3, 3, 1, 1])
            col1.write(f"**{p[1]}**")
            col2.write(f"{p[2]}")
            
            edit_key = f"edit_p_{p[0]}"
            
            # Botón para activar edición
            if col3.button("✏️", key=f"btn_edit_p_{p[0]}"):
                st.session_state[edit_key] = not st.session_state.get(edit_key, False)
            
            # Botón Borrar
            if col4.button("🗑️", key=f"del_p_{p[0]}"):
                c.execute("DELETE FROM proyectos WHERE id = ?", (p[0],))
                c.execute("DELETE FROM tareas WHERE project_id = ?", (p[0],))
                conn.commit()
                st.rerun()

            # Formulario de edición desplegable
            if st.session_state.get(edit_key, False):
                with st.form(f"form_edit_p_{p[0]}"):
                    n_nom = st.text_input("Nuevo nombre", value=p[1])
                    n_desc = st.text_area("Nueva descripción", value=p[2])
                    if st.form_submit_button("Actualizar Cambios"):
                        c.execute("UPDATE proyectos SET nombre=?, descripcion=? WHERE id=?", (n_nom, n_desc, p[0]))
                        conn.commit()
                        st.session_state[edit_key] = False
                        st.rerun()
    else:
        st.info("No hay proyectos registrados.")

# --- ENTIDAD 2: TAREAS ---
elif choice == "Tareas":
    st.header("📝 Gestión de Tareas")
    c.execute("SELECT id, nombre FROM proyectos")
    proyectos_disponibles = c.fetchall()

    if proyectos_disponibles:
        with st.form("form_tarea", clear_on_submit=True):
            proyectos_dict = {p[1]: p[0] for p in proyectos_disponibles}
            proj_sel = st.selectbox("Proyecto", list(proyectos_dict.keys()))
            titulo_t = st.text_input("Título de la Tarea")
            estado_t = st.selectbox("Estado", ["Pendiente", "En Proceso", "Completada"])
            if st.form_submit_button("Guardar Tarea"):
                if titulo_t:
                    c.execute("INSERT INTO tareas (proyecto_id, titulo, estado) VALUES (?, ?, ?)", (proyectos_dict[proj_sel], titulo_t, estado_t))
                    conn.commit()
                    st.success("¡Tarea guardada con éxito!")
                    st.rerun()

        st.subheader("Lista de Tareas")
        c.execute("SELECT t.id, p.nombre, t.titulo, t.estado FROM tareas t JOIN proyectos p ON t.proyecto_id = p.id")
        tareas = c.fetchall()

        if tareas:
            for t in tareas:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                col1.write(f"**{t[1]}**")
                col2.write(f"{t[2]}")
                col3.write(f"{t[3]}")
                
                edit_t_key = f"edit_t_{t[0]}"
                
                if col4.button("✏️", key=f"btn_edit_t_{t[0]}"):
                    st.session_state[edit_t_key] = not st.session_state.get(edit_t_key, False)
                
                if col5.button("🗑️", key=f"del_t_{t[0]}"):
                    c.execute("DELETE FROM tareas WHERE id = ?", (t[0],))
                    conn.commit()
                    st.rerun()

                if st.session_state.get(edit_t_key, False):
                    with st.form(f"form_edit_t_{t[0]}"):
                        n_est = st.selectbox("Nuevo Estado", ["Pendiente", "En Proceso", "Completada"], index=["Pendiente", "En Proceso", "Completada"].index(t[3]))
                        if st.form_submit_button("Actualizar Tarea"):
                            c.execute("UPDATE tareas SET estado=? WHERE id=?", (n_est, t[0]))
                            conn.commit()
                            st.session_state[edit_t_key] = False
                            st.rerun()
        else:
            st.info("No hay tareas registradas.")
    else:
        st.warning("⚠️ Primero debes crear al menos un proyecto en la sección 'Proyectos'.")

# --- VISTA GENERAL ---
elif choice == "Vista General":
    st.header("📊 Resumen")
    c.execute("SELECT COUNT(*) FROM proyectos")
    total_p = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tareas")
    total_t = c.fetchone()[0]
    
    col1, col2 = st.columns(2)
    col1.metric("Total Proyectos", total_p)
    col2.metric("Total Tareas", total_t)
