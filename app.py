
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Relatório de Vendas por Modelo", layout="wide")

st.title("📊 Relatório de Vendas com Custo por Modelo")
st.markdown("Este aplicativo permite analisar suas vendas com base nas planilhas de vendas e de custos.")
st.markdown("👉 **Passo 1:** Envie a planilha de vendas (exportada da sua plataforma)")
st.markdown("👉 **Passo 2:** Envie a planilha de custos com os campos: `ID do Anúncios`, `Modelo`, `Custo Unitário (R$)`")
st.markdown("👉 **Passo 3:** Clique em **Gerar Relatório** para ver os resultados")
st.divider()

# Exemplo de planilha de custo em memória para download
exemplo_custo = pd.DataFrame({
    "ID do Anúncios": ["MLB1234567890", "MLB0987654321"],
    "Modelo": ["Gola Polo", "Saia Jeans"],
    "Produtos": ["Tshirt Gola Polo Feminina", "Saia Jeans Secretária Moda Evangélica"],
    "Custo Unitário (R$)": [25.0, 35.0]
})
buffer = io.BytesIO()
exemplo_custo.to_excel(buffer, index=False, engine='openpyxl')
st.download_button(
    label="📥 Baixar Exemplo de Planilha de Custo",
    data=buffer.getvalue(),
    file_name="exemplo_planilha_custo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# Upload dos arquivos
vendas_file = st.file_uploader("📁 Envie a Planilha de Vendas (.xlsx)", type=["xlsx"])
custos_file = st.file_uploader("📁 Envie a Planilha de Custos com Modelo (.xlsx)", type=["xlsx"])

if vendas_file and custos_file:
    try:
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
        output_buffer = io.BytesIO()
        df_custo_total.to_excel(output_buffer, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Baixar Relatório em Excel",
            data=output_buffer.getvalue(),
            file_name="relatorio_vendas_modelo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ Erro ao processar os arquivos: {e}")
else:
    st.info("⏳ Aguarde o envio das planilhas para gerar o relatório.")
