
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Relatório de Vendas por Modelo", layout="wide")

st.title("📊 Relatório de Vendas com Custo, Lucro e Margem")
st.markdown("Este aplicativo analisa suas vendas a partir de planilhas de vendas e custos.")
st.markdown("👉 **Passo 1:** Envie a planilha de vendas (.xlsx)")
st.markdown("👉 **Passo 2:** Envie a planilha de custos com `ID do Anúncios`, `Modelo`, `Custo Unitário (R$)`")
st.markdown("👉 **Passo 3:** Clique em **Gerar Relatório** para visualizar e baixar os resultados")
st.divider()

# Exemplo para download
exemplo = pd.DataFrame({
    "ID do Anúncios": ["MLB1234567890", "MLB0987654321"],
    "Modelo": ["Gola Polo", "Saia Jeans"],
    "Produtos": ["Tshirt Gola Polo Feminina", "Saia Jeans Secretária"],
    "Custo Unitário (R$)": [25.0, 35.0]
})
buffer = io.BytesIO()
exemplo.to_excel(buffer, index=False, engine='openpyxl')
st.download_button(
    label="📥 Baixar Exemplo de Planilha de Custo",
    data=buffer.getvalue(),
    file_name="exemplo_planilha_custo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# Uploads
vendas_file = st.file_uploader("📁 Planilha de Vendas", type=["xlsx"])
custos_file = st.file_uploader("📁 Planilha de Custos", type=["xlsx"])

if vendas_file and custos_file:
    try:
        df_vendas = pd.read_excel(vendas_file)
        df_custos = pd.read_excel(custos_file)

        df_vendas["ID do Anúncios"] = df_vendas["ID do Anúncios"].astype(str)
        df_custos["ID do Anúncios"] = df_custos["ID do Anúncios"].astype(str)
        df_custos["Custo Unitário (R$)"] = pd.to_numeric(df_custos["Custo Unitário (R$)"], errors="coerce")

        df = pd.merge(df_vendas, df_custos[["ID do Anúncios", "Modelo", "Custo Unitário (R$)"]], on="ID do Anúncios", how="left")
        df["Unidades Vendidas"] = pd.to_numeric(df["Unidades Vendidas"], errors="coerce")
        df["Pagamentos Recebidos"] = pd.to_numeric(df["Pagamentos Recebidos"], errors="coerce")
        df["Custo Total Produto"] = df["Unidades Vendidas"] * df["Custo Unitário (R$)"]

        # Agrupar por modelo
        df_relatorio = df.groupby("Modelo", as_index=False).agg({
            "Unidades Vendidas": "sum",
            "Pagamentos Recebidos": "sum",
            "Custo Total Produto": "sum",
            "Custo Unitário (R$)": "mean"
        }).rename(columns={
            "Unidades Vendidas": "Unidades Vendidas",
            "Pagamentos Recebidos": "Total Vendido (R$)",
            "Custo Total Produto": "Custo Total (R$)",
            "Custo Unitário (R$)": "Custo Unitário Médio (R$)"
        })

        # Calcular lucro e margem
        df_relatorio["Lucro (R$)"] = df_relatorio["Total Vendido (R$)"] - df_relatorio["Custo Total (R$)"]
        df_relatorio["Margem (%)"] = (df_relatorio["Lucro (R$)"] / df_relatorio["Total Vendido (R$)"] * 100).round(2)

        st.success("✅ Relatório Gerado com Sucesso!")
        st.dataframe(df_relatorio)

        # Exportar
        output = io.BytesIO()
        df_relatorio.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Baixar Relatório em Excel",
            data=output.getvalue(),
            file_name="relatorio_vendas_modelo_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar os arquivos: {e}")
else:
    st.info("⏳ Aguarde o envio das planilhas para gerar o relatório.")
