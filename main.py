import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, date
from PIL import Image


def ruta_recurso(ruta_relativa):
    try:
        base_path = sys._MEIPASS  # cuando es .exe
    except Exception:
        base_path = os.path.abspath(".")  # cuando es .py
    return os.path.join(base_path, ruta_relativa)


# ------------------ CONFIG ------------------
# CSV
CLIENTES_CSV = ruta_recurso("data/clientes.csv")
PROYECTOS_CSV = ruta_recurso("data/proyectos.csv")

# Carpetas de imágenes
IMG_CLIENTES_DIR = ruta_recurso("assets/imagenes_clientes")
IMG_PROYECTOS_DIR = ruta_recurso("assets/imagenes_proyectos")

# Imágenes sueltas
LOGO_PATH = ruta_recurso("assets/LOGO_DCC.png")
SIN_IMAGEN_PATH = ruta_recurso("assets/sin_imagen.png")


# Crear carpetas si no existen
os.makedirs(IMG_CLIENTES_DIR, exist_ok=True)
os.makedirs(IMG_PROYECTOS_DIR, exist_ok=True)

# ------------------ INICIALIZAR session_state ------------------
def init_state():
    if "pagina" not in st.session_state:   # Si el usuario no ha hecho ninguna acción en ningun boton, se debe llevar a el inicio
        st.session_state.pagina = "inicio"
    if "menu_open" not in st.session_state:  # El dropdown no se abre hasta que el usuario le de click. Si le da, st.session_state.menu_open=True
        st.session_state.menu_open = False
    if "seleccion" not in st.session_state:
        st.session_state.seleccion = None

init_state()

# ------------------ FUNCIONES AUXILIARES ------------------
def guardar_csv(data, archivo):
    df_nuevo = pd.DataFrame([data])    # Se convierten los datos a la estructura de Pandas
    if os.path.exists(archivo):      # OS Revisa que el archivo exista
        df = pd.read_csv(archivo, dtype=str)
        df = pd.concat([df, df_nuevo], ignore_index=True)  # Se añaden los datos al final de la tabla de datos 
    else:
        df = df_nuevo   # Si no existe, se crea el archivo y se añade el dato
    df.to_csv(archivo, index=False)

def cargar_clientes():
    if os.path.exists(CLIENTES_CSV):   # Se utiliza OS para revisar que el archivo exista
        return pd.read_csv(CLIENTES_CSV, dtype=str)
    return pd.DataFrame(columns=["cliente_id", "nombre", "apellido", "direccion", "imagen_path"])

def cargar_proyectos():
    if os.path.exists(PROYECTOS_CSV):
        return pd.read_csv(PROYECTOS_CSV, dtype=str)     # Utilizando el pd.DataFtame, se puede guardar el CSV de manera ordenada y constante en el archivo
    return pd.DataFrame(columns=["codigo_orden", "nombre_proyecto", "cliente_id", "fecha_inicio", "fecha_fin", "imagenes_paths", "comentarios"])

# ------------------ TOPBARS ------------------
def topbar_inicial():
    logo, top1, top2, top3 = st.columns([1, 5, 5, 2])
    with logo:
        st.image(LOGO_PATH, width=200)

    with top3:
        # Toggle del menú
        if st.button("Registre Nuevo", key="reg_new_toggle_top"):
            st.session_state.menu_open = not st.session_state.menu_open  # Se niega st.session_state.menu_open, ya que cada que se le da click el estado del boton -
#                                                                          vuelve a lo contrario a lo que estaba, osea, si el dropdown esta abierto, el darle click - 
        if st.session_state.get("menu_open", False):                     # de nuevo lo cierra y visce versa. 
            with st.container():
                # Usamos keys únicas para evitar colisiones
                if st.button('Nuevo Cliente', key="btn_nuevo_cliente_top"):
                    st.session_state.pagina = "pg_nuevo_cliente"
                    st.session_state.menu_open = False                   # Se cierra el menu de dropdown para que se pueda cambiar a la pestaña de nuevo cliente - 
#                                                                          o nuevo proyecto usando st.session_state.pagina
                if st.button("Nuevo Proyecto", key="btn_nuevo_proyecto_top"):
                    st.session_state.pagina = "pg_nuevo_proyecto"
                    st.session_state.menu_open = False

# --- TOPBAR SECUNDARIA --- 
def topbar_secundaria():
    logo, _, _, top3 = st.columns([1, 5, 5, 2])
    with logo:
        st.image(LOGO_PATH, width=200)       # Se mantiene el logo de la empresa
    with top3:
        if st.button("Inicio", key="home_btn"):   # El boton de inicio cambia st.session_state.pagina para que lea inicio y el router lo interprete y cambie la -
            st.session_state.pagina = "inicio"    # pestaña.

# ------------------ ESTILO GLOBAL BOTONES ------------------
st.markdown("""
<style>
div[data-testid="stButton"] button {
    background-color: #e98450 !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 10px 20px !important;
    font-style: italic !important;
    font-weight: bold !important;
    cursor: pointer !important;
}
div[data-testid="stButton"] button:hover {
    filter: brightness(0.9);
}
</style>
""", unsafe_allow_html=True)


# -------- TARJETA IMAGEN ---------
def tarjeta_imagen(imagen_path):
    if isinstance(imagen_path, str) and imagen_path and os.path.exists(imagen_path):
        st.markdown('<div class="img-wrapper">', unsafe_allow_html=True)
        st.image(imagen_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="img-wrapper">
                <div class="img-placeholder">Sin imagen</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------ PÁGINAS ------------------

# -------- PÁGINA INICIO (BÚSQUEDA) --------
def pagina_inicio():
    topbar_inicial()

    st.markdown("<h1 style='text-align:center; color:#e98450; font-style:italic;'>Búsqueda de Datos</h1>", unsafe_allow_html=True) # Titulos de la pagina
    st.markdown("<p style='text-align:center; color:#ccc;'>Busque por cliente, nombre de proyecto o código de orden</p>", unsafe_allow_html=True)

    clientes_df = cargar_clientes()       # Se cargan los datos existentes desde los archivos CSV usando Pandas
    proyectos_df = cargar_proyectos()

    # Barra de texto donde el usuario hace la busqueda
    query = st.text_input("", placeholder="🔍 Buscar por nombre, ID o código de orden...", label_visibility="collapsed") 

    if query: # Si el usuario busco algo, se convierte a minusculas para evitar errores de mayusculas
        query = query.lower() 
        resultados = []  # Lista donde se almacenan los resultados coincidentes

        # ---- Búsqueda dentro del archivo CSV de clientes ----
        for _, row in clientes_df.iterrows():  # Recorre cada fila del archivo de clientes
            # Se verifican coincidencias basadas en nombre, apellido, o ID. 
            if query in str(row["nombre"]).lower() or query in str(row["apellido"]).lower() or query in str(row["cliente_id"]).lower():
                resultados.append({
                    "tipo": "Cliente",
                    "nombre": f"{row['nombre']} {row['apellido']}",
                    "codigo": str(row["cliente_id"])
                })

        # ---- Búsqueda dentro del archivo CSV de proyectos ----
        for _, row in proyectos_df.iterrows():  # Recorre cada fila del archivo de proyectos
            # Se verifican coincidencias basadas en nombre del proyecto o codigo de orden de producción.
            if query in str(row["nombre_proyecto"]).lower() or query in str(row["codigo_orden"]).lower():
                resultados.append({
                    "tipo": "Proyecto",
                    "nombre": row["nombre_proyecto"],
                    "codigo": str(row["codigo_orden"])
                })

        # Si hay coincidencias, se muestran los resultados
        if resultados:
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("""
            <style>
            .resultado-container {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background-color: #555;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                margin-bottom: 6px;
                font-weight: bold;
                font-style: italic;
                cursor: default;
            }
            .codigo-naranja {
                background-color: #e98450;
                color: white;
                border-radius: 20px;
                padding: 8px 20px;
                margin-left: 10px;
                font-weight: bold;
                text-align: center;
            }
            </style>
            """, unsafe_allow_html=True)

            # --- Mostrar los resultados de la búsqueda ---
            for i, r in enumerate(resultados):
                # Se usa un formulario para cada resultado con un botón independiente
                with st.form(key=f"form_{i}"):
                    html = f"""
                    <div class='resultado-container'>
                        <div>{r['tipo']} {r['nombre']}</div>
                        <div class='codigo-naranja'>{r['codigo']}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)

                    # Botón que permite abrir el perfil del cliente o proyecto seleccionado
                    submit = st.form_submit_button(label="Abrir perfil", use_container_width=True)
                    if submit:
                        # Se guarda la selección y la página actual en session_state (memoria temporal)
                        st.session_state["seleccion"] = r
                        st.session_state["pagina"] = "perfil"
        else:
            # Si no hay coincidencias, se informa al usuario
            st.info("No se encontraron resultados.")

# ---------- CUMPLEAÑOS -----------
    clientes_df = cargar_clientes()

    hoy = date.today()
    cumple_hoy = []

    for _, c in clientes_df.iterrows():
        if isinstance(c["fecha_nacimiento"], str) and c["fecha_nacimiento"]:
            fn = pd.to_datetime(c["fecha_nacimiento"]).date()
            if fn.day == hoy.day and fn.month == hoy.month:
                cumple_hoy.append(c)

    if cumple_hoy:
        st.markdown(
                "<h3 style='font-size:25px; margin-bottom:4px;'>Clientes de cumpleaños hoy!</h3>",
                unsafe_allow_html=True
            )

        cols = st.columns(4)

        for i, cliente in enumerate(cumple_hoy):
            with cols[i % 4]:

                if isinstance(cliente["imagen_path"], str) and cliente["imagen_path"] and os.path.exists(cliente["imagen_path"]):
                    st.image(cliente["imagen_path"], width=200)
                else:
                    st.image(SIN_IMAGEN_PATH, width=200)

                st.markdown(
                    f"""
                    <div style="
                        max-width: 200px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        font-weight: 600;
                        margin-top: 6px;
                    ">
                        🎂 {cliente['nombre']} {cliente['apellido']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(" ")

                if st.button(
                    "Ver perfil",
                    key=f"perfil_cumple_{cliente['cliente_id']}"
                ):
                    st.session_state.seleccion = {
                        "tipo": "Cliente",
                        "codigo": cliente["cliente_id"]
                    }
                    st.session_state.pagina = "perfil"


# -------- PÁGINA PERFIL CLIENTE --------
def pagina_perfil_cliente():
    topbar_secundaria()

    mensaje = st.session_state.pop("mensaje_exito", None)
    if mensaje:
        st.success(mensaje)

    seleccion = st.session_state.get("seleccion")

    if not seleccion or seleccion.get("tipo") != "Cliente":
        st.warning("Perfil no válido.")
        if st.button("Volver al inicio"):
            st.session_state.pagina = "inicio"
        return

    cliente_id = seleccion["codigo"]

    # Cargar datos
    clientes_df = cargar_clientes()
    proyectos_df = cargar_proyectos()

    cliente = clientes_df[clientes_df["cliente_id"] == cliente_id].iloc[0]

    nombre = cliente["nombre"]
    apellido = cliente["apellido"]
    imagen_path = cliente["imagen_path"]
    direccion = cliente["direccion"]
    fecha_nacimiento = cliente.get("fecha_nacimiento", "")

    if isinstance(fecha_nacimiento, str) and fecha_nacimiento:
        fecha_nacimiento_fmt = pd.to_datetime(fecha_nacimiento).strftime("%d/%m/%Y")
    else:
        fecha_nacimiento_fmt = "No registrada"

    proyectos_cliente = proyectos_df[proyectos_df["cliente_id"] == cliente_id]

    # --- Layout ---
    col_img, col_info = st.columns([2, 5])

    # Imagen del cliente
    with col_img:
        if (
            isinstance(imagen_path, str) and
            imagen_path.strip() != "" and
            os.path.exists(imagen_path)
        ):
            st.image(imagen_path, use_container_width=True)
        else:
            st.markdown(
                """
                <div style="
                    height:250px;
                    background-color:#555;
                    border:2px dashed #999;
                    border-radius:8px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#bbb;
                    font-style:italic;
                ">
                    Sin imagen
                </div>
                """,
                unsafe_allow_html=True
            )


    # Información del cliente
    with col_info:
        st.markdown(
            f"<h2 style='color:#e98450; font-style:italic;'>{nombre} {apellido}</h2>",
            unsafe_allow_html=True
        )
        st.markdown(f"<p style='color:white;'>ID Cliente: <strong>{cliente_id}</strong></p>", unsafe_allow_html=True)
        st.markdown(f"**Fecha de nacimiento:** {fecha_nacimiento_fmt}")
        if direccion and isinstance(direccion, str):
            st.markdown(
                f"<p style='color:#ccc;'>Dirección: <strong>{direccion}</strong></p>",
                unsafe_allow_html=True
            )

        st.markdown("<h4 style='color:white;'>Proyectos Asociados</h4>", unsafe_allow_html=True)

        if proyectos_cliente.empty:
            st.info("Este cliente no tiene proyectos asociados.")
        else:
            for _, p in proyectos_cliente.iterrows():
                col_p1, col_p2 = st.columns([4, 1])
                with col_p1:
                    st.markdown(
                        f"<div style='background:#555; padding:8px; border-radius:6px; color:white;'>"
                        f"{p['nombre_proyecto']}</div>",
                        unsafe_allow_html=True
                    )
                with col_p2:
                    if st.button(p["codigo_orden"], key=f"open_proj_{p['codigo_orden']}"):
                        st.session_state.seleccion = {
                            "tipo": "Proyecto",
                            "nombre": p["nombre_proyecto"],
                            "codigo": p["codigo_orden"]
                        }
                        st.session_state.pagina = "perfil"

    st.markdown("<br>", unsafe_allow_html=True)

    # Botón editar
    if st.button("Editar", use_container_width=True):
        st.session_state.editar_cliente_id = cliente_id
        st.session_state.pagina = "pg_editar_cliente"

# -------- PÁGINA NUEVO CLIENTE --------
def pagina_nuevo_cliente():
    topbar_secundaria()

    st.markdown(
        "<h1 style='color:#e27032; font-style:italic;'>Nuevo Cliente</h1>",
        unsafe_allow_html=True
    )

    clientes_df = cargar_clientes()

    # -------- FORMULARIO --------
    cliente_id = st.text_input("Ingrese Cédula o NIT del cliente")
    nombre = st.text_input("Ingrese Nombre del cliente")
    apellido = st.text_input("Ingrese Apellido del cliente")
    direccion = st.text_input("Ingrese Dirección del cliente")

    fecha_nacimiento = st.date_input(
        "Fecha de nacimiento (opcional)",
        value=None
    )

    col_img, col_form = st.columns([2, 3])

    # -------- UPLOADER (UNO SOLO) --------
    with col_form:
        img_cliente = st.file_uploader(
            "Adjuntar imagen (opcional)",
            type=["png", "jpg", "jpeg"],
            key="nuevo_cliente_imagen"
        )

    # -------- PREVISUALIZACIÓN --------
    with col_img:
        if img_cliente:
            st.image(img_cliente, caption="Imagen cargada", use_container_width=True)
        else:
            st.markdown(
                "<div style='height:220px; background:#444; border:2px dashed #999; "
                "border-radius:8px; display:flex; align-items:center; justify-content:center; "
                "color:#bbb;'>Sin imagen</div>",
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------ CUMPLEAÑOS -------
    fecha_nacimiento_str = ""
    if fecha_nacimiento:
        fecha_nacimiento_str = fecha_nacimiento.strftime("%Y-%m-%d")

    # -------- GUARDAR --------
    if st.button("Guardar cliente", use_container_width=True):

        # -------- VALIDACIONES --------
        if not cliente_id or not nombre:
            st.error("El ID y el nombre son obligatorios.")
            return

        if cliente_id in clientes_df["cliente_id"].values:
            st.error(f"Ya existe un cliente con la identificación {cliente_id}.")
            return

        # -------- MANEJO DE IMAGEN --------
        imagen_path = ""

        if img_cliente:
            ext = img_cliente.name.split(".")[-1]
            imagen_path = os.path.join(
                IMG_CLIENTES_DIR,
                f"{cliente_id}.{ext}"
            )
            Image.open(img_cliente).save(imagen_path)

        # -------- GUARDAR --------
        data = {
            "cliente_id": cliente_id,
            "nombre": nombre,
            "apellido": apellido,
            "direccion": direccion,
            "imagen_path": imagen_path,
            "fecha_nacimiento": fecha_nacimiento_str
        }

        guardar_csv(data, CLIENTES_CSV)

        st.session_state.pagina = "pg_guardado_cliente"
        st.session_state.nombre_guardado = f"{nombre} {apellido}"


# ------------- PÁGINA EDITAR CLIENTE ------------------

def pagina_editar_cliente():
    topbar_secundaria()

    editar_id = st.session_state.get("editar_cliente_id")

    if "confirmar_eliminar_cliente" not in st.session_state:
        st.session_state.confirmar_eliminar_cliente = False

    if editar_id and "eliminar_imagen" not in st.session_state:
        st.session_state.eliminar_imagen = False

    st.markdown(
        "<h1 style='color:#e27032; font-style:italic;'>Editar Cliente</h1>",
        unsafe_allow_html=True
    )

    cliente_id_original = st.session_state.get("editar_cliente_id")


    if not cliente_id_original:
        st.warning("No hay cliente seleccionado para editar.")
        if st.button("Volver al inicio"):
            st.session_state.pagina = "inicio"
        return

    clientes_df = cargar_clientes()
    proyectos_df = cargar_proyectos()

    cliente = clientes_df[
        clientes_df["cliente_id"] == cliente_id_original
    ].iloc[0]

    # -------- DATOS ACTUALES --------
    cliente_id = st.text_input(
        "ID del cliente",
        value=cliente["cliente_id"]
    )

    fecha_nacimiento_actual = None
    if isinstance(cliente["fecha_nacimiento"], str) and cliente["fecha_nacimiento"]:
        fecha_nacimiento_actual = pd.to_datetime(
            cliente["fecha_nacimiento"]
        ).date()


    nombre = st.text_input("Nombre", value=cliente["nombre"])
    apellido = st.text_input("Apellido", value=cliente["apellido"])
    direccion = st.text_input("Dirección", value=cliente["direccion"])
    fecha_nacimiento = st.date_input(
        "Fecha de nacimiento (opcional)",
        value=fecha_nacimiento_actual
    )


    imagen_path_actual = cliente["imagen_path"]

    col_img, col_form = st.columns([2, 3])

    # -------- PREVISUALIZACIÓN DE IMAGEN --------
    with col_img:
        if isinstance(imagen_path_actual, str) and imagen_path_actual and os.path.exists(imagen_path_actual):
            st.image(imagen_path_actual, caption="Imagen actual", use_container_width=True)
        else:
            st.markdown(
                "<div style='height:220px; background:#444; border:2px dashed #999; "
                "border-radius:8px; display:flex; align-items:center; justify-content:center; "
                "color:#bbb;'>Sin imagen</div>",
                unsafe_allow_html=True
            )

    # -------- FORMULARIO --------
    with col_form:
        st.markdown("### Reemplazar imagen (opcional)")
        img_nueva = st.file_uploader(
            "Adjuntar nueva imagen",
            type=["png", "jpg", "jpeg"]
        )

        if imagen_path_actual and isinstance(imagen_path_actual, str) and os.path.exists(imagen_path_actual):
            if st.button("Eliminar imagen"):
                st.session_state.eliminar_imagen = True
                st.info("La imagen se eliminará al guardar los cambios.")

        st.markdown("<br>", unsafe_allow_html=True)

    # -------- BOTONES --------
    col_volver, col_guardar = st.columns(2)

    with col_volver:
        if st.button("⬅ Volver al perfil", use_container_width=True):
            st.session_state.seleccion = {
                "tipo": "Cliente",
                "codigo": cliente_id_original
            }
            st.session_state.pagina = "perfil"

    with col_guardar:
        if st.button("Guardar cambios", use_container_width=True):
            # -------- VALIDAR ID SOLO SI CAMBIÓ --------
            if cliente_id != cliente_id_original:
                ids_existentes = clientes_df[
                    clientes_df["cliente_id"] != cliente_id_original
                ]["cliente_id"].values

                if cliente_id in ids_existentes:
                    st.error("Ya existe un cliente con ese ID.")
                    return

            # -------- MANEJO DE IMAGEN --------
            imagen_final = imagen_path_actual

            # Caso 1: eliminar imagen (solo ahora se borra)
            if st.session_state.eliminar_imagen:
                if imagen_path_actual and os.path.exists(imagen_path_actual):
                    os.remove(imagen_path_actual)
                imagen_final = ""
                st.session_state.eliminar_imagen = False  # reset flag

            # Caso 2: subir nueva imagen
            elif img_nueva:
                ext = img_nueva.name.split(".")[-1]
                imagen_final = os.path.join(
                    IMG_CLIENTES_DIR,
                    f"{cliente_id}.{ext}"
                )
                Image.open(img_nueva).save(imagen_final)

            # Caso 3: cambiar ID y mantener imagen
            elif imagen_path_actual and cliente_id != cliente_id_original:
                ext = imagen_path_actual.split(".")[-1]
                nueva_ruta = os.path.join(
                    IMG_CLIENTES_DIR,
                    f"{cliente_id}.{ext}"
                )
                if os.path.exists(imagen_path_actual):
                    os.rename(imagen_path_actual, nueva_ruta)
                    imagen_final = nueva_ruta
                    

            # -------- ACTUALIZAR CLIENTE --------
            clientes_df.loc[
                clientes_df["cliente_id"] == cliente_id_original,
                [
                    "cliente_id",
                    "nombre",
                    "apellido",
                    "direccion",
                    "imagen_path",
                    "fecha_nacimiento"
                ]
            ] = [
                cliente_id,
                nombre,
                apellido,
                direccion,
                imagen_final,
                fecha_nacimiento.strftime("%Y-%m-%d") if fecha_nacimiento else ""
            ]

            clientes_df.to_csv(CLIENTES_CSV, index=False)

            # -------- ACTUALIZACIÓN EN CASCADA --------
            proyectos_df.loc[
                proyectos_df["cliente_id"] == cliente_id_original,
                "cliente_id"
            ] = cliente_id

            proyectos_df.to_csv(PROYECTOS_CSV, index=False)

            # -------- MENSAJE + VOLVER A PERFIL --------
            st.session_state.seleccion = {
                "tipo": "Cliente",
                "codigo": cliente_id
            }
            st.session_state.mensaje_exito = "Datos del cliente actualizados correctamente."
            st.session_state.pagina = "perfil"

    # ---- ELIMINAR CLIENTE ------
    st.markdown("---")

    # --- Botón inicial ---
    if not st.session_state.confirmar_eliminar_cliente:
        if st.button(
            "Eliminar cliente",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.confirmar_eliminar_cliente = True

    # --- Caja de confirmación ---
    else:
        st.warning(
            " **¿Estás seguro de eliminar este cliente?**\n\n"
            "• Se eliminará el cliente **y TODOS los proyectos asociados**\n"
            "• Se borrarán **todas las imágenes relacionadas**\n"
            "• **Esta acción NO es reversible**"
        )

        col_no, col_si = st.columns(2)

        with col_no:
            if st.button(
                "No, seguir editando",
                use_container_width=True
            ):
                st.session_state.confirmar_eliminar_cliente = False

        with col_si:
            if st.button(
                "Sí, eliminar definitivamente",
                use_container_width=True
            ):
                # -------- BORRADO REAL --------

                # Imagen del cliente
                img_cliente = cliente["imagen_path"]
                if isinstance(img_cliente, str) and img_cliente and os.path.exists(img_cliente):
                    os.remove(img_cliente)

                # Proyectos asociados
                proyectos_cliente = proyectos_df[
                    proyectos_df["cliente_id"] == cliente_id_original
                ]

                # Imágenes de proyectos
                for _, p in proyectos_cliente.iterrows():
                    imgs = p.get("imagenes_paths", "")
                    if isinstance(imgs, str) and imgs:
                        for ruta in imgs.split(","):
                            ruta = ruta.strip()
                            if os.path.exists(ruta):
                                os.remove(ruta)

                # Borrar proyectos
                proyectos_df = proyectos_df[
                    proyectos_df["cliente_id"] != cliente_id_original
                ]
                proyectos_df.to_csv(PROYECTOS_CSV, index=False)

                # Borrar cliente
                clientes_df = clientes_df[
                    clientes_df["cliente_id"] != cliente_id_original
                ]
                clientes_df.to_csv(CLIENTES_CSV, index=False)

                # Limpiar estado
                st.session_state.confirmar_eliminar_cliente = False
                st.session_state.editar_cliente_id = None
                st.session_state.seleccion = None
                st.session_state.pagina = "inicio"

                st.success("Cliente y proyectos asociados eliminados correctamente.")
                st.stop()


# --------- PAGINA PERFIL PROYECTO ---------
def pagina_perfil_proyecto():
    topbar_secundaria()

    # -------- MENSAJE DE ÉXITO --------
    if "mensaje_exito" in st.session_state:
        st.success(st.session_state.mensaje_exito)
        del st.session_state.mensaje_exito


    st.markdown(
        """
        <style>
        button[data-testid="stButton"] {
            background-color: #555 !important;
            color: white !important;
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            font-size: 18px !important;
            border: none !important;
        }

        button[data-testid="stButton"]:hover {
            background-color: #777 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    seleccion = st.session_state.get("seleccion", {})
    codigo_proyecto = seleccion.get("codigo")

    if not codigo_proyecto:
        st.warning("No hay proyecto seleccionado.")
        return

    proyectos_df = cargar_proyectos()
    clientes_df = cargar_clientes()

    proyecto = proyectos_df[
        proyectos_df["codigo_orden"] == codigo_proyecto
    ].iloc[0]

    cliente_id = proyecto["cliente_id"]

    cliente_row = clientes_df[
        clientes_df["cliente_id"] == cliente_id
    ]

    if not cliente_row.empty:
        cliente_nombre = cliente_row.iloc[0]["nombre"]
        cliente_apellido = cliente_row.iloc[0]["apellido"]
    else:
        cliente_nombre = "Cliente"
        cliente_apellido = "desconocido"


    # ------------------ TÍTULO ------------------
    st.markdown(
        f"<h1 style='color:#e27032; font-style:italic;'>{proyecto['nombre_proyecto']}</h1>",
        unsafe_allow_html=True
    )

    st.markdown(f"**Código de orden:** {proyecto['codigo_orden']}")

    # ------------------ CLIENTE (ID CLICKEABLE) ------------------
    cliente_id = proyecto["cliente_id"]
    cliente = clientes_df[clientes_df["cliente_id"] == cliente_id].iloc[0]

    col_txt, col_btn = st.columns([4, 1])

    with col_txt:
        # --- BLOQUE CLIENTE (barra gris completa) ---
        st.markdown(
            f"""
            <div style="
                background:#444;
                border-radius:12px;
                padding:14px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:16px;
            ">
                <div style="color:white;">
                    <strong>Cliente:</strong> {cliente_nombre} {cliente_apellido}
                </div>
                <div id="cliente_click"></div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col_btn:

        # --- DETECTAR CLICK EN CLIENTE ---
        if st.button(
            cliente_id,
            key=f"btn_cliente_{cliente_id}",
            help="Ver perfil del cliente"
        ):
            st.session_state.seleccion = {
                "tipo": "Cliente",
                "codigo": cliente_id
            }
            st.session_state.pagina = "perfil"


    # ------------------ FECHAS ------------------
    st.write(" ")

    fecha_fin = proyecto["fecha_fin"]

    if isinstance(fecha_fin, str) and fecha_fin.strip():
        fecha_fin_txt = fecha_fin
    else:
        fecha_fin_txt = "En proceso"

    col_fi, col_ff = st.columns(2)

    with col_fi:
        st.markdown("**Fecha inicio**")
        st.markdown(proyecto["fecha_inicio"])

    with col_ff:
        st.markdown("**Fecha final**")
        st.markdown(fecha_fin_txt)




    # ------------------ COMENTARIOS ------------------
    st.markdown(
        "<h3 style='font-size:20px; margin-bottom:0px;'>Comentarios</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='background:#444; padding:12px; border-radius:8px;'>"
        f"{proyecto.get('comentarios', '')}"
        f"</div>",
        unsafe_allow_html=True
    )

    # ------------------ IMÁGENES DEL PROYECTO ------------------
    st.write(" ")
    st.markdown(
        "<h3 style='font-size:20px; margin-bottom:4px;'>Imágenes del proyecto</h3>",
        unsafe_allow_html=True
    )

    imagenes_raw = proyecto.get("imagenes_paths")

    # Normalizar imágenes (maneja NaN, None, string)
    if isinstance(imagenes_raw, str):
        imagenes = [
            img.strip()
            for img in imagenes_raw.split(",")
            if img.strip() and os.path.exists(img.strip())
        ]
    else:
        imagenes = []

    # Inicializar índice si no existe
    if "img_index" not in st.session_state:
        st.session_state.img_index = 0

    # 🔒 Asegurar índice válido SIEMPRE
    if st.session_state.img_index >= len(imagenes):
        st.session_state.img_index = 0

    # ----- CASO 0: SIN IMÁGENES -----
    if len(imagenes) == 0:
        st.info("Este proyecto no tiene imágenes asociadas.")

    # ----- CASO 1: UNA SOLA IMAGEN -----
    elif len(imagenes) == 1:
        st.image(imagenes[0], use_container_width=True)

    # ----- CASO 2: CARRUSEL -----
    else:
        col_prev, col_img, col_next = st.columns([1, 6, 1])

        with col_prev:
            if st.button("◀", key="prev_img"):
                st.session_state.img_index = (
                    st.session_state.img_index - 1
                ) % len(imagenes)

        with col_img:
            st.image(
                imagenes[st.session_state.img_index],
                use_container_width=True
            )

        with col_next:
            if st.button("▶", key="next_img"):
                st.session_state.img_index = (
                    st.session_state.img_index + 1
                ) % len(imagenes)


        st.markdown(
            f"<p style='text-align:center; color:#aaa; margin-top:4px;'>"
            f"Imagen {st.session_state.img_index + 1} de {len(imagenes)}"
            f"</p>",
            unsafe_allow_html=True
    )


    # ------------------ BOTÓN EDITAR (ABAJO DERECHA) ------------------

    st.markdown("<br><br>", unsafe_allow_html=True)

    col_vacia, col_btn = st.columns([4, 1])

    with col_btn:
        if st.button("Editar", use_container_width=True):
            st.session_state.editar_proyecto_codigo = proyecto["codigo_orden"]
            st.session_state.pagina = "editar_proyecto"


def pagina_editar_proyecto():
    topbar_secundaria()

    if "confirmar_eliminar_proyecto" not in st.session_state:
        st.session_state.confirmar_eliminar_proyecto = False

    # ------------------ OBTENER ID A EDITAR ------------------
    codigo_original = st.session_state.get("editar_proyecto_codigo")
    codigo_orden_original = codigo_original


    if not codigo_original:
        st.warning("No hay proyecto seleccionado para editar.")
        if st.button("Volver"):
            st.session_state.pagina = "inicio"
        return

    # ------------------ CARGAR DATOS ------------------
    proyectos_df = cargar_proyectos()

    proyecto = proyectos_df[
        proyectos_df["codigo_orden"] == codigo_original
    ].iloc[0]

    # ------------------ ESTADO PARA IMÁGENES ------------------
    if "imagenes_a_eliminar" not in st.session_state:
        st.session_state.imagenes_a_eliminar = set()

    # ------------------ TÍTULO ------------------
    st.markdown(
        "<h1 style='color:#e27032; font-style:italic;'>Editar Proyecto</h1>",
        unsafe_allow_html=True
    )

    # ------------------ CAMPOS EDITABLES ------------------
    codigo_orden = st.text_input(
        "Código de orden",
        value=proyecto["codigo_orden"]
    )

    nombre_proyecto = st.text_input(
        "Nombre del proyecto",
        value=proyecto["nombre_proyecto"]
    )

    cliente_id = st.text_input(
        "ID del cliente",
        value=proyecto["cliente_id"]
    )

    # -------- FECHAS SEGURAS --------
    fecha_inicio_actual = None
    fecha_fin_actual = None

    # Fecha inicio (OBLIGATORIA)
    if isinstance(proyecto["fecha_inicio"], str) and proyecto["fecha_inicio"].strip():
        fecha_inicio_actual = pd.to_datetime(
            proyecto["fecha_inicio"],
            errors="coerce"
        ).date()

    # Si aun así falla, forzar hoy (última barrera)
    if fecha_inicio_actual is None:
        fecha_inicio_actual = date.today()

    # Fecha fin (OPCIONAL)
    if isinstance(proyecto["fecha_fin"], str) and proyecto["fecha_fin"].strip():
        fecha_fin_actual = pd.to_datetime(
            proyecto["fecha_fin"],
            errors="coerce"
        ).date()


    col_fi, col_ff = st.columns(2)

    with col_fi:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=fecha_inicio_actual
        )

    with col_ff:
        en_proceso = st.checkbox(
            "Proyecto en proceso",
            value=fecha_fin_actual is None
        )

        if not en_proceso:
            fecha_fin = st.date_input(
                "Fecha final",
                value=fecha_fin_actual
            )
        else:
            fecha_fin = None


    comentarios = st.text_area(
        "Comentarios",
        value=proyecto["comentarios"],
        height=120
    )

    # ------------------ IMÁGENES EXISTENTES ------------------
    imagenes_str = proyecto["imagenes_paths"]

    if isinstance(imagenes_str, str) and imagenes_str.strip():
        imagenes = [img.strip() for img in imagenes_str.split(",")]
    else:
        imagenes = []

    st.markdown(
        "<h3 style='font-size:20px; margin-bottom:4px;'>Imágenes del proyecto</h3>",
        unsafe_allow_html=True
    )

    if not imagenes:
        st.info("Este proyecto no tiene imágenes.")
    else:
        cols = st.columns(3)

        for i, img_path in enumerate(imagenes):
            with cols[i % 3]:
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.warning("Imagen no encontrada")

                if img_path in st.session_state.imagenes_a_eliminar:
                    st.caption("🗑 Imagen marcada para eliminar")
                else:
                    if st.button("Eliminar", key=f"del_img_{i}"):
                        st.session_state.imagenes_a_eliminar.add(img_path)
                        st.rerun()

    # ------------------ SUBIR NUEVAS IMÁGENES ------------------
    st.markdown(
        "<h3 style='font-size:20px; margin-bottom:4px;'>Subir nuevas imágenes</h3>",
        unsafe_allow_html=True
    )
    nuevas_imgs = st.file_uploader(
        "Selecciona imágenes",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    # -------- BOTONES --------
    col_volver, col_guardar = st.columns(2)

    st.markdown("""
    <style>
    button[kind="secondary"] {
        background-color: #555 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with col_volver:
        if st.button("⬅ Volver al perfil", type="secondary", use_container_width=True):
            st.session_state.seleccion = {
                "tipo": "Proyecto",
                "codigo": codigo_orden
            }
            st.session_state.pagina = "perfil"

    with col_guardar:
        if st.button("Guardar cambios", use_container_width=True):

            # ---- VALIDAR CÓDIGO ÚNICO ----
            if codigo_orden != codigo_original:
                codigos_existentes = (
                    proyectos_df["codigo_orden"]
                    .astype(str)
                    .str.upper()
                    .values
                )

                if codigo_orden.upper() in codigos_existentes:
                    st.error("Ya existe un proyecto con ese código.")
                    return


            # ---- BORRAR IMÁGENES MARCADAS ----
            imagenes_finales = []

            for img in imagenes:
                if img in st.session_state.imagenes_a_eliminar:
                    if os.path.exists(img):
                        os.remove(img)
                else:
                    imagenes_finales.append(img)

            # ---- GUARDAR NUEVAS IMÁGENES ----
            if nuevas_imgs:
                for idx, img in enumerate(nuevas_imgs):
                    ext = img.name.split(".")[-1]
                    nueva_ruta = os.path.join(
                        IMG_PROYECTOS_DIR,
                        f"{codigo_orden}_{len(imagenes_finales)+idx}.{ext}"
                    )
                    Image.open(img).save(nueva_ruta)
                    imagenes_finales.append(nueva_ruta)

            imagenes_paths_final = ",".join(imagenes_finales)

            # ---- ACTUALIZAR CSV ----
            proyectos_df.loc[
                proyectos_df["codigo_orden"] == codigo_original,
                [
                    "codigo_orden",
                    "nombre_proyecto",
                    "cliente_id",
                    "fecha_inicio",
                    "fecha_fin",
                    "imagenes_paths",
                    "comentarios"
                ]
            ] = [
                codigo_orden,
                nombre_proyecto,
                cliente_id,
                fecha_inicio,
                fecha_fin,
                imagenes_paths_final,
                comentarios
            ]

            proyectos_df.to_csv(PROYECTOS_CSV, index=False)

            # ---- LIMPIAR ESTADO ----
            st.session_state.imagenes_a_eliminar = set()

            # ---- VOLVER A PERFIL ----
            st.session_state.seleccion = {
                "tipo": "Proyecto",
                "codigo": codigo_orden
            }
            st.session_state.pagina = "perfil"
            st.session_state.mensaje_exito = "Proyecto actualizado correctamente."

    # ------ ELIMINAR PROYECTO --------
    st.markdown("---")

    # --- Botón inicial ---
    if not st.session_state.confirmar_eliminar_proyecto:
        if st.button(
            "Eliminar proyecto",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.confirmar_eliminar_proyecto = True

    # --- Confirmación ---
    else:
        st.warning(
            "⚠️ **¿Estás seguro de eliminar este proyecto?**\n\n"
            "• Se eliminarán todas las imágenes del proyecto\n"
            "• Esta acción **NO es reversible**"
        )

        col_no, col_si = st.columns(2)

        with col_no:
            if st.button(
                "No, seguir editando",
                use_container_width=True
            ):
                st.session_state.confirmar_eliminar_proyecto = False

        with col_si:
            if st.button(
                "Sí, eliminar definitivamente",
                use_container_width=True
            ):
                # --- Eliminar imágenes ---
                imgs = proyecto.get("imagenes_paths", "")
                if isinstance(imgs, str) and imgs:
                    for ruta in imgs.split(","):
                        ruta = ruta.strip()
                        if os.path.exists(ruta):
                            os.remove(ruta)

                # --- Eliminar proyecto ---
                proyectos_df = proyectos_df[
                    proyectos_df["codigo_orden"] != codigo_orden_original
                ]
                proyectos_df.to_csv(PROYECTOS_CSV, index=False)

                # --- Limpiar estado ---
                st.session_state.confirmar_eliminar_proyecto = False
                st.session_state.editar_proyecto_id = None
                st.session_state.seleccion = None
                st.session_state.pagina = "inicio"

                st.success("Proyecto eliminado correctamente.")
                st.stop()


# ------------- PÁGINA NUEVO PROYECTO --------------------
def pagina_nuevo_proyecto():
    topbar_secundaria()

    fecha_inicio_actual = None
    fecha_fin_actual = None

    st.markdown("<h1 style='color:#e27032; font-style:italic;'>Nuevo Proyecto</h1>", unsafe_allow_html=True)

    proyectos_df = cargar_proyectos()   # Se carga el archivo CSV de proyectos para revisar que no hayan duplicados en el codigo de orden
    clientes_df = cargar_clientes()     # Se carga el archivo CSV de clientes para asociar el ID del cliente a el proyecto

    clientes_opciones = clientes_df.apply(         # Se hace una dropdown de los clientes para que el usuario solo tenga que seleccionar
        lambda x: f"{x['nombre']} {x['apellido']} ({x['cliente_id']})", axis=1
    ).drop_duplicates().tolist()

    nombre_proyecto = st.text_input("Ingrese Nombre del Proyecto")       # Input de los datos del proyecto
    codigo_orden = st.text_input("Ingrese Código de Orden de Producción").strip().upper()
    cliente = st.selectbox("Cliente Asociado", options=clientes_opciones if clientes_opciones else ["No hay clientes registrados"])

    col_fi, col_ff = st.columns(2)

    with col_fi:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=fecha_inicio_actual
        )

    with col_ff:
        en_proceso = st.checkbox(
            "Proyecto en proceso",
            value=fecha_fin_actual is None
        )

        if not en_proceso:
            fecha_fin = st.date_input(
                "Fecha final",
                value=fecha_fin_actual
            )
        else:
            fecha_fin = None


    comentarios = st.text_area("Comentarios adicionales")    # Otro campo de input para comentarios

    col_img1, col_img2 = st.columns(2)
    with col_img2:
        st.markdown("<p style='font-weight:500;'>Adjuntar Imágenes</p>", unsafe_allow_html=True)
        imagenes = st.file_uploader("", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        if st.button("Guardar Proyecto", key="guardar_proyecto"):    
        # --- Validación de duplicados ---
            codigos_existentes = (
                proyectos_df["codigo_orden"]
                .astype(str)
                .str.upper()
                .values
            )

            if codigo_orden.upper() in codigos_existentes:
                st.error("Ya existe un proyecto con ese código.")
                return

            # Extrae el ID del cliente del texto seleccionado en el dropdown
            cliente_id = cliente.split("(")[-1].replace(")", "") if "(" in cliente else ""

            # --- Guardado de imágenes ---
            img_paths = []
            for i, img in enumerate(imagenes or []):
                ext = img.name.split(".")[-1]
                file_path = os.path.join(IMG_PROYECTOS_DIR, f"{codigo_orden}_{i+1}.{ext}") # OS crea una ruta especifica de 
                image = Image.open(img)  # PIL abre la imagen
                image.save(file_path) 
                img_paths.append(file_path)


            data = {       # Estructura del guardado de datos
                "codigo_orden": codigo_orden,
                "nombre_proyecto": nombre_proyecto,
                "cliente_id": cliente_id,
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "fecha_fin": fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "",
                "imagenes_paths": ",".join(img_paths),
                "comentarios": comentarios
            }

            guardar_csv(data, PROYECTOS_CSV)                 # Guarda el nuevo registro en el CSV

            st.session_state.pagina = "pg_guardado_proyecto"   # Se redirige a guardado correcto
            st.session_state.nombre_guardado = nombre_proyecto

    with col_img1:
        if imagenes:
            st.image(imagenes[0], caption="Previsualización", use_container_width=True)   # imagenes[0] para previsualizar solo la primera imagen adjunta
        else:   # Placeholder si no se añade 
            st.markdown(
                "<div style='height:200px; background-color:#2f2f2f; border:2px dashed #999; border-radius:8px; "
                "display:flex; align-items:center; justify-content:center; color:#bbb;'>Sin imagen</div>",
                unsafe_allow_html=True
            )

def limpiar_imagenes_huerfanas():
    if not os.path.exists(IMG_CLIENTES_DIR):
        return

    clientes_df = cargar_clientes()
    rutas_validas = set(clientes_df["imagen_path"].dropna().values)

    for archivo in os.listdir(IMG_CLIENTES_DIR):
        ruta = os.path.join(IMG_CLIENTES_DIR, archivo)
        if ruta not in rutas_validas:
            try:
                os.remove(ruta)
            except:
                pass

# -------- PÁGINAS DE GUARDADO CORRECTO --------
def pagina_guardado_cliente():
    topbar_secundaria()
    nombre = st.session_state.get("nombre_guardado", "Cliente")     # Se obtienen los datos recien guardados
    st.markdown(f"<h2 style='color:#e98450; font-style:italic;'>{nombre}</h2>", unsafe_allow_html=True) # Se remplaza {nombre} por el nombre+apellido recien guardado
    st.markdown("<h3 style='color:white;'>fue guardado exitosamente!</h3>", unsafe_allow_html=True)
    if st.button("Volver a Inicio"):
        st.session_state.pagina = "inicio"

def pagina_guardado_proyecto():
    topbar_secundaria()
    nombre = st.session_state.get("nombre_guardado", "Proyecto")    # Se obtienen los datos recien guardados
    st.markdown(f"<h2 style='color:#e98450; font-style:italic;'>{nombre}</h2>", unsafe_allow_html=True) # Se remplaza {nombre} por el nombre del proyecto recien guardado
    st.markdown("<h3 style='color:white;'>fue guardado exitosamente!</h3>", unsafe_allow_html=True) 
    if st.button("Volver a Inicio"):
        st.session_state.pagina = "inicio"

# ------------------ RUN ------------------
if __name__ == "__main__":
    p = st.session_state.get("pagina", "inicio")      # st.session_state.get toma la definicion de st.session_state["pagina"] en las distintas funciones de pestañas
    if p == "inicio":                                 # Esto asocia una palabra o codigo, como "inicio" en st.session_state a una funcion de pagina
        pagina_inicio()                               # Se corre la funcion de pagina, y se hace el display grafico correcto.
    elif p == "pg_nuevo_cliente":
        pagina_nuevo_cliente()
    elif st.session_state.pagina == "pg_editar_cliente":
        pagina_editar_cliente()
    elif p == "pg_nuevo_proyecto":
        pagina_nuevo_proyecto()
    elif p == "pg_guardado_cliente":
        pagina_guardado_cliente()
    elif p == "pg_guardado_proyecto":
        pagina_guardado_proyecto()
    elif p == "perfil":
        if st.session_state.get("seleccion", {}).get("tipo") == "Cliente":
            pagina_perfil_cliente()
        elif st.session_state.get("seleccion", {}).get("tipo") == "Proyecto":
            pagina_perfil_proyecto()    
    elif st.session_state.pagina == "editar_proyecto":
        pagina_editar_proyecto()

    else:
        # fallback
        pagina_inicio()                               # El fallback se genera para que siempre se muestre una pagina en el programa.