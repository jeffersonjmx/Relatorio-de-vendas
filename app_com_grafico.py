
import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="Relatório de Vendas por Modelo", layout="wide")

st.title("📊 Relatório de Vendas com Gráfico de Participação por Modelo")
st.markdown("Este aplicativo analisa suas vendas a partir de planilhas de vendas e custos.")
st.markdown("👉 **Passo 1:** Envie a planilha de vendas (.xlsx)")
st.markdown("👉 **Passo 2:** Envie a planilha de custos com `ID do Anúncios`, `Modelo`, `Custo Unitário (R$)`")
st.markdown("👉 **Passo 3:** Clique em **Gerar Relatório** para visualizar e baixar os resultados")
st.divider()

# Exemplo de planilha de custos
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

# Upload dos arquivos
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
        df["Pagamentos Recebidos"] = pd.to_numeric(df["Pagamentos Recebidos"], errors="coerce")
        df["Custo Total Produto"] = df["Custo Unitário (R$)"] * pd.to_numeric(df["Unidades Vendidas"], errors="coerce")

        # Agrupar por modelo
        df_grouped = df.groupby("Modelo", as_index=False).agg({
            "Custo Total Produto": "sum",
            "Pagamentos Recebidos": "sum",
            "Custo Unitário (R$)": "first"
        }).rename(columns={
            "Custo Total Produto": "Custo Total (R$)",
            "Pagamentos Recebidos": "Total Vendido (R$)",
            "Custo Unitário (R$)": "Custo Unitário (R$)"
        })

        df_grouped["Unidades Vendidas"] = df_grouped["Custo Total (R$)"] / df_grouped["Custo Unitário (R$)"]
        df_grouped["Unidades Vendidas"] = df_grouped["Unidades Vendidas"].round(0).astype("Int64")

        df_grouped["Lucro (R$)"] = df_grouped["Total Vendido (R$)"] - df_grouped["Custo Total (R$)"]
        df_grouped["Margem (%)"] = (df_grouped["Lucro (R$)"] / df_grouped["Total Vendido (R$)"] * 100).round(2)

        st.success("✅ Relatório Gerado com Sucesso!")
        st.dataframe(df_grouped)

        # Gráfico de pizza
        st.markdown("### 📈 Participação no Total Vendido")
        fig, ax = plt.subplots()
        ax.pie(df_grouped["Total Vendido (R$)"], labels=df_grouped["Modelo"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # Exportar Excel
        output = io.BytesIO()
        df_grouped.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Baixar Relatório em Excel",
            data=output.getvalue(),
            file_name="relatorio_com_grafico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar os arquivos: {e}")
else:
    st.info("⏳ Aguarde o envio das planilhas para gerar o relatório.")
