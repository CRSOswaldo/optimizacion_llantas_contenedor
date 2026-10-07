#!/usr/bin/env python3
"""
Interfaz visual (Streamlit) para cálculo de volumen de llantas
(sección rectangular revolvida) y optimización de la combinación
dentro de un contenedor de 39 m³ (rango 80-90 %).
"""

import math
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sympy import symbols, diff, solve


# ---------------------------------------------------------------------------
# Lógica de cálculo
# ---------------------------------------------------------------------------

def volumen_rectangular(ancho_mm: float, perfil: float, rin_pulgadas: float) -> dict:
    W = ancho_mm
    H = W * (perfil / 100.0)
    r_rin = (rin_pulgadas * 25.4) / 2.0
    vol_mm3 = math.pi * W * H * (2 * r_rin + H)
    vol_litros = vol_mm3 / 1_000_000.0
    return {
        "ancho_mm": W,
        "perfil": perfil,
        "rin_pulgadas": rin_pulgadas,
        "altura_H_mm": round(H, 2),
        "volumen_litros": round(vol_litros, 3),
        "etiqueta": f"{int(W)}/{int(perfil)} R{int(rin_pulgadas)}"
    }


def calcular_combinacion(llantas: list, Vc: float = 39000.0):
    if not llantas:
        return None

    k = len(llantas)
    f = symbols("f")
    U = -(f - 0.85) ** 2
    dU = diff(U, f)
    d2U = diff(dU, f)
    criticos = solve(dU, f)
    punto_critico = float(criticos[0]) if criticos else 0.85
    segunda = float(d2U.subs(f, punto_critico))

    vol_objetivo = punto_critico * Vc
    vol_por_tipo = vol_objetivo / k

    cantidades = []
    for t in llantas:
        v = t["volumen_litros"]
        n = max(1, round(vol_por_tipo / v))
        cantidades.append(n)

    total = sum(n * t["volumen_litros"] for n, t in zip(cantidades, llantas))
    f_actual = total / Vc
    if not (0.80 <= f_actual <= 0.90):
        factor = (0.85 * Vc) / total
        cantidades = [max(1, round(n * factor)) for n in cantidades]

    vols_unitarios = [t["volumen_litros"] for t in llantas]
    volumenes_parciales = [n * v for n, v in zip(cantidades, vols_unitarios)]
    volumen_total = sum(volumenes_parciales)
    f_real = volumen_total / Vc

    return {
        "cantidades": cantidades,
        "volumenes_parciales": volumenes_parciales,
        "volumen_total": volumen_total,
        "porcentaje": f_real * 100,
        "punto_critico": punto_critico,
        "segunda_derivada": segunda,
        "dU_str": str(dU),
        "d2U_str": str(d2U),
        "etiquetas": [t["etiqueta"] for t in llantas],
        "vols_unitarios": vols_unitarios,
    }


# ---------------------------------------------------------------------------
# Interfaz Streamlit
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Optimización de Llantas – Contenedor 39 m³",
    page_icon="🛞",
    layout="wide"
)

st.title("🛞 Volumen de llantas + Optimización de contenedor")
st.caption("Modelo: sección rectangular revolvida  ·  Contenedor: 39 000 L  ·  Rango objetivo: 80 – 90 %")

# Estado de la sesión
if "llantas" not in st.session_state:
    st.session_state.llantas = []

# ----- Entrada de datos -----
st.subheader("1. Agregar llantas")
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    ancho = st.number_input("Ancho (mm)", min_value=100.0, max_value=400.0, value=205.0, step=5.0)
with col2:
    perfil = st.number_input("Perfil (%)", min_value=25.0, max_value=90.0, value=55.0, step=5.0)
with col3:
    rin = st.number_input("Rin (pulgadas)", min_value=10.0, max_value=30.0, value=17.0, step=1.0)
with col4:
    st.write("")
    st.write("")
    btn_agregar = st.button("➕ Agregar", use_container_width=True)

if btn_agregar:
    datos = volumen_rectangular(ancho, perfil, rin)
    st.session_state.llantas.append(datos)
    st.success(f"Agregada: **{datos['etiqueta']}** → {datos['volumen_litros']} L")

col_a, col_b = st.columns([1, 5])
with col_a:
    if st.button("🗑️ Limpiar lista", use_container_width=True):
        st.session_state.llantas = []
        st.rerun()

# ----- Tabla de llantas agregadas -----
st.subheader("2. Llantas en la lista")
if st.session_state.llantas:
    df_lista = pd.DataFrame([
        {"#": i+1, "Medida": t["etiqueta"], "Volumen (L)": t["volumen_litros"]}
        for i, t in enumerate(st.session_state.llantas)
    ])
    st.dataframe(df_lista, use_container_width=True, hide_index=True)
else:
    st.info("Todavía no hay llantas. Agrega al menos una para calcular.")

# ----- Calcular -----
st.subheader("3. Optimización")
btn_calcular = st.button("⚙️ Calcular optimización", type="primary")

if btn_calcular:
    if not st.session_state.llantas:
        st.warning("Agrega al menos una llanta antes de calcular.")
    else:
        r = calcular_combinacion(st.session_state.llantas)

        # Función y derivadas
        st.markdown("#### Función de utilidad y análisis de derivadas")
        c1, c2, c3 = st.columns(3)
        c1.metric("Función", "U(f) = -(f − 0.85)²")
        c2.metric("1ª derivada", f"U'(f) = {r['dU_str']}")
        c3.metric("2ª derivada", f"U''(f) = {r['d2U_str']}")

        st.success(
            f"**Punto crítico:** f* = {r['punto_critico']:.2f}  "
            f"(U'' = {r['segunda_derivada']:.1f} → **MÁXIMO**).  "
            f"El óptimo está en el centro del rango 80-90 %."
        )

        # Tabla de combinación
        st.markdown("#### Combinación óptima de medidas")
        df_res = pd.DataFrame({
            "Medida": r["etiquetas"],
            "Vol. unitario (L)": [f"{v:.3f}" for v in r["vols_unitarios"]],
            "Cantidad": r["cantidades"],
            "Vol. parcial (L)": [f"{v:.1f}" for v in r["volumenes_parciales"]],
        })
        st.dataframe(df_res, use_container_width=True, hide_index=True)

        # Totales
        total_n = sum(r["cantidades"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de llantas", f"{total_n}")
        m2.metric("Volumen total", f"{r['volumen_total']:.1f} L")
        m3.metric("Llenado del contenedor", f"{r['porcentaje']:.2f} %")

        if 80 <= r["porcentaje"] <= 90:
            st.success("✓ El volumen total está **dentro** del rango 80-90 %.")
        else:
            st.warning("⚠ El volumen total quedó fuera del rango por el redondeo a enteros.")

        # Expresión matemática
        terminos = " + ".join([f"n_{i+1}·{v:.3f}" for i, v in enumerate(r["vols_unitarios"])])
        st.code(f"V(n₁, n₂, …, nₖ) = {terminos}\nV = {r['volumen_total']:.1f} L  ≈  {r['porcentaje']/100:.4f} · 39 000 L")

        # ----- Gráficas -----
        st.markdown("#### Gráficas")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

        # U(f)
        f_vals = np.linspace(0, 1, 300)
        U_vals = -(f_vals - 0.85) ** 2
        ax1.axvspan(0.80, 0.90, color="green", alpha=0.18, label="Rango 80-90 %")
        ax1.plot(f_vals, U_vals, "b-", lw=2, label=r"$U(f)=-(f-0.85)^2$")
        ax1.plot(0.85, 0, "ro", ms=9, label="f* = 0.85")
        f_real = r["porcentaje"] / 100
        ax1.plot(f_real, -(f_real - 0.85) ** 2, "gs", ms=8, label=f"Actual f={f_real:.3f}")
        ax1.axvline(0.85, color="red", ls=":", alpha=0.7)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(-0.7, 0.08)
        ax1.set_xlabel("Fracción de llenado f")
        ax1.set_ylabel("Utilidad U(f)")
        ax1.set_title("Función de utilidad y punto crítico")
        ax1.legend(loc="lower center", fontsize=8)
        ax1.grid(True, alpha=0.3)

        # Barras
        x = np.arange(len(r["etiquetas"]))
        colores = plt.cm.viridis(np.linspace(0.25, 0.75, len(x)))
        bars = ax2.bar(x, r["cantidades"], color=colores, edgecolor="black", lw=0.6)
        ax2.set_xticks(x)
        ax2.set_xticklabels(r["etiquetas"], rotation=25, ha="right", fontsize=8)
        ax2.set_ylabel("Cantidad de llantas")
        ax2.set_title(f"Combinación óptima ({r['porcentaje']:.1f} % del contenedor)")
        ax2.grid(True, axis="y", alpha=0.3)
        for bar, n in zip(bars, r["cantidades"]):
            ax2.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + max(r["cantidades"])*0.01,
                     str(n), ha="center", va="bottom", fontsize=8, fontweight="bold")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

# Pie
st.divider()
st.caption("Modelo de volumen: V ≈ π · W · H · (2·r_rin + H)  ·  Optimización basada en la utilidad U(f) = -(f-0.85)²")
