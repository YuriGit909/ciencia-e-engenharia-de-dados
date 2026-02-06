import pandas as pd
import sqlite3

def conectar_bd(caminho_csv):
    """Lê o CSV e prepara o banco de dados em memória."""
    df = pd.read_csv(caminho_csv)
    # check_same_thread=False é vital para o SQLite funcionar com Streamlit
    conexao = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("db_suic", conexao, index=False)
    return conexao


def montar_query(filtros):
    """Constrói a query SQL baseada nos filtros recebidos do frontend."""
    query = "SELECT ParentLocation, Location, Period, Dim1, FactValueNumeric FROM db_suic WHERE 1 = 1"
    parametros = []

    # Filtro de Gênero
    if filtros.get("Dim1") and filtros["Dim1"] != "Both sexes":
        query += " AND Dim1 = ?"
        parametros.append(filtros["Dim1"])

    # Filtro de Período
    if filtros.get("ano_inicio") and filtros.get("ano_final"):
        query += " AND Period BETWEEN ? AND ?"
        parametros.append(filtros["ano_inicio"])
        parametros.append(filtros["ano_final"])

    # Filtro de País (Opcional)
    if filtros.get("Location"):
        query += " AND LOWER(Location) = ?"
        parametros.append(filtros["Location"].lower())

    # Filtro de Continente (Opcional)
    if filtros.get("ParentLocation") and filtros["ParentLocation"] != "Todos":
        query += " AND LOWER(ParentLocation) = ?"
        parametros.append(filtros["ParentLocation"].lower())

    return query, parametros