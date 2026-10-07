# 🛞 Optimización de Llantas en Contenedor (39 m³)

Aplicación web para calcular el volumen de llantas (modelo de sección rectangular revolvida) y optimizar cuántas de cada medida caben en un contenedor de **39 000 litros**, manteniendo el llenado entre el **80 % y 90 %**.

Utiliza análisis de derivadas (1ª y 2ª) para encontrar el punto crítico de la función de utilidad.

## Cómo usar la aplicación en línea

1. Entra a la URL pública de Streamlit Community Cloud (se genera al desplegar).
2. Agrega las medidas de las llantas (Ancho mm, Perfil %, Rin pulgadas).
3. Haz clic en **Calcular optimización**.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run volumen_llantas_gui.py
```

## Archivos principales

| Archivo | Descripción |
|---------|-------------|
| `volumen_llantas_gui.py` | Interfaz visual (Streamlit) |
| `volumen_llantas_contenedor.py` | Versión de consola |
| `requirements.txt` | Dependencias |

## Modelo de volumen

\[
V \approx \pi \cdot W \cdot H \cdot (2 \cdot r_{\text{rin}} + H)
\]

donde \( H = W \times \frac{\text{perfil}}{100} \).

## Optimización

Función de utilidad del nivel de llenado \( f \):

\[
U(f) = -(f - 0.85)^2
\]

- \( U'(f) = 0 \) → punto crítico \( f^* = 0.85 \)
- \( U''(f) < 0 \) → máximo

El programa reparte el volumen de forma equitativa entre las medidas ingresadas para acercarse a ese 85 %.
