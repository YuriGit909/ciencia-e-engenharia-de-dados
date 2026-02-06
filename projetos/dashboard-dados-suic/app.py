# rode: streamlit run app.py
import streamlit as st
import plotly.express as px  # Biblioteca para o gráfico
import pandas as pd
from Main import conectar_bd, montar_query

# Configurações da página
st.set_page_config(page_title="Data Search", layout="wide")
CAMINHO_CSV = r"/home/maco/Documentos/dashboard_dados_suicidio/db_suic.csv"

# Inicialização do Banco de Dados
if 'conexao' not in st.session_state:
    try:
        st.session_state.conexao = conectar_bd(CAMINHO_CSV)
        # Busca os continentes existentes no CSV para preencher o selectbox automaticamente
        df_cont = pd.read_sql_query("SELECT DISTINCT ParentLocation FROM db_suic", st.session_state.conexao)
        st.session_state.lista_continentes = ["Todos"] + sorted(df_cont['ParentLocation'].dropna().tolist())
    except Exception as e:
        st.error(f"Erro ao carregar banco de dados: {e}")

st.title("📊 Consulta de Dados de Suicídio")
st.markdown("Preencha os filtros abaixo. Campos vazios serão ignorados na busca.")

# Layout de Filtros
col1, col2, col3 = st.columns(3)

with col1:
    gen = st.selectbox("Gênero", ["Both sexes", "Female", "Male"])
    # O filtro de continente agora é opcional, padrão "Todos"
    cont = st.selectbox("Filtrar por Continente", st.session_state.get('lista_continentes', ["Todos"]))

with col2:
    # O usuário pode digitar o país ou deixar em branco
    loc = st.text_input("Filtrar por País (Nome em Inglês)", placeholder="Ex: Brazil")
    st.caption("Deixe em branco para pesquisar em todos os países.")
    gerar_grafico = st.checkbox("Gerar gráfico de barras após a busca?")

with col3:
    ano_i = st.number_input("Ano Inicial", value=2000)
    ano_f = st.number_input("Ano Final", value=2020)

# Agrupamento dos filtros
filtros = {
    "Dim1": gen,
    "ano_inicio": ano_i,
    "ano_final": ano_f,
    "Location": loc.strip(),
    "ParentLocation": cont
}

if st.button("🔍 Executar Busca"):
    query, params = montar_query(filtros)
    df_res = pd.read_sql_query(query, st.session_state.conexao, params=params)

    if not df_res.empty:
        st.subheader(f"✅ Resultados Encontrados ({len(df_res)})")
        st.dataframe(df_res, use_container_width=True)

        # --- SEÇÃO DO GRÁFICO ---
        if gerar_grafico:
            st.divider()
            st.subheader("📈 Visualização dos Dados")

            # 1. Tradução e Preparação
            df_plot = df_res.rename(columns={
                'Location': 'País',
                'FactValueNumeric': 'Taxa de Suicídio',
                'Period': 'Ano',
                'Dim1': 'Gênero'
            })

            # 2. Lógica de exibição baseada no filtro de Gênero
            if gen == "Both sexes":
                # Se for "Both sexes", mostramos a comparação entre os países ao longo do tempo
                fig = px.line(
                    df_plot,
                    x="Ano",
                    y="Taxa de Suicídio",
                    color="País",
                    markers=True,
                    title="Evolução Temporal: Ambos os Sexos",
                    labels={"Taxa de Suicídio": "Taxa (por 100k hab.)"},
                    template="plotly_white"
                )
            else:
                # Se um sexo específico foi escolhido, podemos dar destaque a ele
                fig = px.line(
                    df_plot,
                    x="Ano",
                    y="Taxa de Suicídio",
                    color="País",
                    line_dash="País",  # Estilos de linha diferentes para ajudar na distinção
                    markers=True,
                    title=f"Evolução Temporal: Gênero {gen}",
                    labels={"Taxa de Suicídio": f"Taxa {gen} (por 100k hab.)"},
                    template="plotly_white"
                )

            # Ajustes finos para garantir que o gráfico fique legível
            fig.update_layout(
                hovermode="x unified",  # Mostra todos os valores ao passar o mouse em um ano
                yaxis_range=[0, df_plot['Taxa de Suicídio'].max() * 1.2]  # Dá uma folga no topo
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")