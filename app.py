import sqlite3
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Gestión de Redes y Cloud", page_icon="☁️", layout="wide")

# Conexión a la base de datos
conn = sqlite3.connect("cloud_networks.db", check_same_thread=False)
c = conn.cursor()

def crear_tablas():
    c.execute("""CREATE TABLE IF NOT EXISTS servidores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                proveedor TEXT NOT NULL,
                region TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS puertos_red (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servidor_id INTEGER,
                puerto INTEGER NOT NULL,
                protocolo TEXT NOT NULL,
                FOREIGN KEY(servidor_id) REFERENCES servidores(id))""")
    conn.commit()

crear_tablas()

st.title("☁️ Gestión de Redes y Computación en la Nube")
menu = ["Servidores Cloud", "Puertos de Red", "Vista General"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

# --- ENTIDAD 1: SERVIDORES ---
if choice == "Servidores Cloud":
    st.header("🖥️ Servidores Cloud")
    
    # Crear
    with st.form("form_servidor"):
        nombre_s = st.text_input("Nombre de la Instancia")
        proveedor_s = st.selectbox("Proveedor", ["AWS", "Google Cloud", "Azure", "Local"])
        region_s = st.text_input("Región")
        if st.form_submit_button("Guardar"):
            c.execute("INSERT INTO servidores (nombre, proveedor, region) VALUES (?, ?, ?)", (nombre_s, proveedor_s, region_s))
            conn.commit()
            st.rerun()

    # Leer y Editar/Borrar
    c.execute("SELECT * FROM servidores")
    for s in c.fetchall():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
        col1.write(f"**{s[1]}** ({s[2]})")
        col2.write(s[3])
        
        # Botón Editar
        if col4.button("✏️", key=f"e_s_{s[0]}"):
            st.session_state[f"edit_s_{s[0]}"] = True
        
        if st.session_state.get(f"edit_s_{s[0]}", False):
            with st.form(f"f_edit_s_{s[0]}"):
                n_nom = st.text_input("Nombre", value=s[1])
                n_prov = st.selectbox("Proveedor", ["AWS", "Google Cloud", "Azure", "Local"], index=["AWS", "Google Cloud", "Azure", "Local"].index(s[2]))
                if st.form_submit_button("Actualizar"):
                    c.execute("UPDATE servidores SET nombre=?, proveedor=? WHERE id=?", (n_nom, n_prov, s[0]))
                    conn.commit()
                    st.session_state[f"edit_s_{s[0]}"] = False
                    st.rerun()
        
        # Botón Borrar
        if col5.button("🗑️", key=f"d_s_{s[0]}"):
            c.execute("DELETE FROM servidores WHERE id=?", (s[0],))
            c.execute("DELETE FROM puertos_red WHERE servidor_id=?", (s[0],))
            conn.commit()
            st.rerun()

# --- ENTIDAD 2: PUERTOS ---
elif choice == "Puertos de Red":
    st.header("🔌 Puertos de Red")
    c.execute("SELECT id, nombre FROM servidores")
    servs = c.fetchall()
    
    if servs:
        # Crear
        with st.form("form_p"):
            s_dict = {s[1]: s[0] for s in servs}
            sel = st.selectbox("Servidor", list(s_dict.keys()))
            puerto = st.number_input("Puerto", value=80)
            prot = st.selectbox("Protocolo", ["TCP", "UDP"])
            if st.form_submit_button("Guardar"):
                c.execute("INSERT INTO puertos_red (servidor_id, puerto, protocolo) VALUES (?, ?, ?)", (s_dict[sel], puerto, prot))
                conn.commit()
                st.rerun()
        
        # Listar
        c.execute("SELECT p.id, s.nombre, p.puerto, p.protocolo FROM puertos_red p JOIN servidores s ON p.servidor_id = s.id")
        for p in c.fetchall():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.write(f"**{p[1]}** - Puerto {p[2]} ({p[3]})")
            
            if col3.button("✏️", key=f"e_p_{p[0]}"):
                st.session_state[f"edit_p_{p[0]}"] = True
            
            if st.session_state.get(f"edit_p_{p[0]}", False):
                with st.form(f"f_edit_p_{p[0]}"):
                    n_p = st.number_input("Puerto", value=p[2])
                    if st.form_submit_button("Actualizar"):
                        c.execute("UPDATE puertos_red SET puerto=? WHERE id=?", (n_p, p[0]))
                        conn.commit()
                        st.session_state[f"edit_p_{p[0]}"] = False
                        st.rerun()
            
            if col4.button("🗑️", key=f"d_p_{p[0]}"):
                c.execute("DELETE FROM puertos_red WHERE id=?", (p[0],))
                conn.commit()
                st.rerun()
    else:
        st.warning("Crea un servidor primero.")

# --- VISTA GENERAL ---
elif choice == "Vista General":
    st.header("📊 Resumen")
    c.execute("SELECT COUNT(*) FROM servidores")
    st.metric("Servidores", c.fetchone()[0])
