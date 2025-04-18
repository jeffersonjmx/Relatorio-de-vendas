
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Relatório de Vendas por Modelo", layout="wide")

st.title("📊 Relatório de Vendas com Custo por Modelo")

# Upload dos arquivos
vendas_file = st.file_uploader("📁 Envie a Planilha de Vendas (.xlsx)", type=["xlsx"])
custos_file = st.file_uploader("📁 Envie a Planilha de Custos com Modelo (.xlsx)", type=["xlsx"])

if vendas_file and custos_file:
    # Carregar dados
    df_vendas = pd.read_excel(vendas_file)
    df_custos = pd.read_excel(custos_file)

    # Garantir consistência nos formatos
    df_vendas["ID do Anúncios"] = df_vendas["ID do Anúncios"].astype(str)
    df_custos["ID do Anúncios"] = df_custos["ID do Anúncios"].astype(str)
    df_custos["Custo Unitário (R$)"] = pd.to_numeric(df_custos["Custo Unitário (R$)"], errors="coerce")

    # Juntar os dados
    df = pd.merge(df_vendas, df_custos[["ID do Anúncios", "Modelo", "Custo Unitário (R$)"]], on="ID do Anúncios", how="left")
    df["Unidades Vendidas"] = pd.to_numeric(df["Unidades Vendidas"], errors="coerce")
    df["Custo Total Produto"] = df["Unidades Vendidas"] * df["Custo Unitário (R$)"]

    # Agrupar por modelo
    df_custo_total = df.groupby("Modelo", as_index=False).agg({
        "Custo Total Produto": "sum",
        "Custo Unitário (R$)": "mean"
    }).rename(columns={
        "Custo Total Produto": "Custo Total por Modelo (R$)",
        "Custo Unitário (R$)": "Custo Unitário Médio (R$)"
    })

    # Calcular unidades estimadas
    df_custo_total["Unidades Vendidas (Estimado)"] = df_custo_total["Custo Total por Modelo (R$)"] / df_custo_total["Custo Unitário Médio (R$)"]
    df_custo_total["Unidades Vendidas (Estimado)"] = df_custo_total["Unidades Vendidas (Estimado)"].round(0).astype("Int64")

    st.success("✅ Relatório Gerado com Sucesso!")
    st.dataframe(df_custo_total)

    # Exportar
    export = st.download_button(
        label="📥 Baixar Relatório em Excel",
        data=df_custo_total.to_excel(index=False, engine='openpyxl'),
        file_name="relatorio_vendas_modelo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
