"""
Dashboard interactivo de GameScout.
"""

import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlmodel import Session, select

from app.stats import category_stats, price_zscores, price_zscores_py
from gamescout.database import get_engine
from gamescout.models import Product

st.set_page_config(
    page_title="GameScout Dashboard",
    layout="wide",
)

st.title("GameScout Dashboard")

engine = get_engine()

with Session(engine) as session:
    products = session.exec(select(Product)).all()

    data = []
    for product in products:
        data.append({
                "ID": product.product_id,
                "Título": product.title,
                "Precio": float(product.price_eur),
                "Categoría": product.type.name if product.type else "Sin categoría",
                "Type_ID": product.type_id if product.type_id is not None else 0,
            }
        )

df = pd.DataFrame(data)

if df.empty:
    st.warning("No hay productos cargados en la base de datos.")
    st.stop()

# Filtros en sidebar
st.sidebar.header("Filtros")

categorias = sorted(df["Categoría"].unique())
categorias_seleccionadas = st.sidebar.multiselect(
    "Categorías",
    categorias,
    default=categorias,
)

precio_min = float(df["Precio"].min())
precio_max = float(df["Precio"].max())

rango_precio = st.sidebar.slider(
    "Rango de precio (euros)",
    precio_min,
    precio_max,
    (precio_min, precio_max),
)

texto = st.sidebar.text_input("Buscar título")

# Filtros en cascada
df_filtrado = df.copy()

if categorias_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado["Categoría"].isin(categorias_seleccionadas)]

df_filtrado = df_filtrado[
    (df_filtrado["Precio"] >= rango_precio[0])
    & (df_filtrado["Precio"] <= rango_precio[1])
]

if texto:
    df_filtrado = df_filtrado[
        df_filtrado["Título"].str.contains(texto, case=False, na=False)
    ]

# V
col1, col2 = st.columns(2)


st.subheader("Top 10 Productos Más Caros")
top10 = df_filtrado.sort_values("Precio", ascending=False).head(10)
fig_top = px.bar(
    top10,
    x="Precio",
    y="Título",
    orientation="h",
    color="Precio",
    labels={"Precio": "Precio (€)"},
)
fig_top.update_layout(yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig_top, use_container_width=True)

st.subheader("Distribución de Precios")
fig_hist = px.histogram(
    df_filtrado,
    x="Precio",
    nbins=15,
    labels={"Precio": "Precio (€)"},
)
st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Precio Promedio por Categoría")
promedios = df_filtrado.groupby("Categoría", as_index=False)["Precio"].mean()
fig_avg = px.bar(
    promedios,
    x="Categoría",
    y="Precio",
    color="Precio",
    labels={"Precio": "Precio Promedio (€)"},
)
st.plotly_chart(fig_avg, use_container_width=True)

# dataframe de productos filtrados
st.subheader("Tabla de Productos Filtrados")
df_tabla = df_filtrado.copy()

# formatear precio a euros con dos decimales
df_tabla["Precio Formateado"] = df_tabla["Precio"].map("{:.2f} €".format)

st.dataframe(
    df_tabla[["ID", "Título", "Categoría", "Precio Formateado"]],
    use_container_width=True,
)

st.markdown("---")

# Calculos con numba
st.header("Calculos Numericos Acelerados con Numba")

if not df_filtrado.empty:
    arr_prices = df_filtrado["Precio"].to_numpy(dtype=np.float64)
    arr_types = df_filtrado["Type_ID"].to_numpy(dtype=np.int64)

    # Tabla de estadisticas 
    u_types, counts, mins, maxs, means, stds = category_stats(arr_prices, arr_types)

    # Mapeo de ID de categoría a Nombre
    type_id_to_name = dict(zip(df["Type_ID"], df["Categoría"]))

    stats_list = []
    for i in range(len(u_types)):
        c_id = u_types[i]
        stats_list.append(
            {
                "Categoría": type_id_to_name.get(c_id, f"Tipo {c_id}"),
                "Cantidad": counts[i],
                "Precio Mínimo (€)": f"{mins[i]:.2f}",
                "Precio Máximo (€)": f"{maxs[i]:.2f}",
                "Precio Promedio (€)": f"{means[i]:.2f}",
                "Desviación Estándar (€)": f"{stds[i]:.2f}",
            }
        )

    st.subheader("Estadísticas por Categoría (calculadas con @njit)")
    st.dataframe(pd.DataFrame(stats_list), use_container_width=True)

    # Outliers / ofertas
    st.subheader("Datos atipicos / Ofertas")
    umbral_z = st.slider("Umbral puntaje z", 0.5, 4.0, 2.0, step=0.1)

    z_scores_arr = price_zscores(arr_prices, arr_types)
    df_filtrado["Z-Score"] = z_scores_arr

    outliers = df_filtrado[np.abs(df_filtrado["Z-Score"]) > umbral_z].copy()
    outliers["Precio (€)"] = outliers["Precio"].map("{:.2f} €".format)
    outliers["Z-Score"] = outliers["Z-Score"].map("{:.2f}".format)

    if not outliers.empty:
        st.write(f"Se encontraron **{len(outliers)}** productos fuera del umbral |Z| > {umbral_z}:")
        st.dataframe(
            outliers[["ID", "Título", "Categoría", "Precio (€)", "Z-Score"]],
            use_container_width=True,
        )
    else:
        st.info("No hay productos que superen el umbral de Z-Score seleccionado.")

    ### Benchmark Python Puro vs. Numba
    st.subheader("Comparacion velocidad: Python vs. Numba")

    # Duplicar el arreglo para hacer el benchmark significativo en milisegundos
    bench_prices = np.tile(arr_prices, 100)
    bench_types = np.tile(arr_types, 100)

    # Warm-Up (Descarte de primera llamada por tiempo de compilación JIT)
    _ = price_zscores(bench_prices[:10], bench_types[:10])

    # Medicion con numba 
    t0 = time.perf_counter()
    _ = price_zscores(bench_prices, bench_types)
    t1 = time.perf_counter()
    time_numba = t1 - t0

    # Medicion con python 
    t2 = time.perf_counter()
    _ = price_zscores_py(bench_prices, bench_types)
    t3 = time.perf_counter()
    time_py = t3 - t2

    speedup = time_py / time_numba

    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("Python", f"{time_py * 1000:.3f} ms")
    col_b2.metric("Numba", f"{time_numba * 1000:.3f} ms")


    st.caption(
        "Nota: Se realizo una ejecuto una llamada inicial previo al calculo del tiempo para descartar "
        "el tiempo de compilacion JIT de Numba y medir solo el tiempo de ejecucion en el benchmark."
    )