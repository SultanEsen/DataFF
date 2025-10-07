import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO

# === Настройки ===
EXCEL_PATH = Path("Data.xlsx")  # Excel-файл должен быть в той же папке

st.set_page_config(page_title="Анализ данных FF", layout="wide")
st.title("📊 Анализ данных FF")

# === Загрузка данных ===
if not EXCEL_PATH.exists():
    st.error(f"Файл '{EXCEL_PATH}' не найден. Поместите Excel рядом с app.py.")
    st.stop()

df = pd.read_excel(EXCEL_PATH)

# --- Отображение исходных данных ---
# st.subheader("Исходные данные")
# st.dataframe(df, use_container_width=True)

# === Фильтрация ===
st.subheader("🔍 Фильтрация данных")

filters = {}
cols = st.columns(3)  # три фильтра в ряд
for i, col_name in enumerate(df.columns):
    unique_vals = df[col_name].dropna().unique()
    if len(unique_vals) <= 50:  # показываем фильтры только для "удобных" колонок
        with cols[i % 3]:
            selected = st.multiselect(f"{col_name}", unique_vals)
            if selected:
                filters[col_name] = selected

filtered_df = df.copy()
for col, vals in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(vals)]

st.write(f"**Отфильтровано строк:** {len(filtered_df)} из {len(df)}")

# # === Выбор отображаемых полей ===
# st.subheader("📋 Выбор колонок для отображения")
#
# columns_to_show = st.multiselect(
#     "Выберите поля для таблицы",
#     options=filtered_df.columns.tolist(),
#     default=filtered_df.columns.tolist()[:5]
# )

# st.dataframe(filtered_df[columns_to_show], use_container_width=True)

# === Сводная таблица ===
st.subheader("📈 Двумерная сводная таблица (Pivot Table)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    row_field = st.selectbox("Строки", filtered_df.columns)
with col2:
    col_field = st.selectbox("Столбцы", filtered_df.columns)
with col3:
    value_field = st.selectbox("Значения", filtered_df.columns)
with col4:
    agg_func = st.selectbox("Агрегация", ["count", "sum", "mean", "max", "min"])

pivot_table = pd.pivot_table(
    filtered_df,
    index=row_field,
    columns=col_field,
    values=value_field,
    aggfunc=agg_func,
    fill_value=0
)

st.dataframe(pivot_table, use_container_width=True)

# === Скачивание ===
def to_excel_bytes(df):
    output = BytesIO()
    df.to_excel(output, engine="openpyxl")
    return output.getvalue()

col_a, col_b = st.columns(2)
with col_a:
    st.download_button(
        "💾 Скачать отфильтрованные данные (Excel)",
        data=to_excel_bytes(filtered_df),
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with col_b:
    st.download_button(
        "📊 Скачать сводную таблицу (Excel)",
        data=to_excel_bytes(pivot_table),
        file_name="pivot_table.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
