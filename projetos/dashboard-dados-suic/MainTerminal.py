import pandas as pd
import sqlite3

caminho_bd = r"caminho-arquivo.csv"
df = pd.read_csv(caminho_bd)

def conectar_bd(caminho):
    # cria um bd temporario na RAM e transfere o dataframe pro sql
    conexao = sqlite3.connect(":memory:")
    df.to_sql("db_suic", conexao, index = False)
    cursor = conexao.cursor()
    return conexao, cursor


def ler_filtros():
    filtros={}

    print("\n" + "="*40)
    #   .strip() --> remove os espaços antes e depois das entradas
    filtros["Dim1"] = input("Filtrar por genero? ('Female/Male/Both sexes' ou enter para pular): ").strip()
    filtros["ano_inicio"] = input("Ano inicio (ou enter para pular): ").strip()
    filtros["ano_final"] = input("Ano final (ou enter para pular): ").strip()
    filtros["Location"] = input("Filtrar por regiao? (nome do país em ingles ou enter para pular): ").strip()
    filtros["ParentLocation"] = input("Filtrar por continente? (nome do continente em ingles ou enter para pular): ").strip()

    return filtros

def montar_query(filtros):
    query = "SELECT ParentLocation, Location, Period, Dim1, FactValueNumeric FROM db_suic WHERE 1 = 1"
    parametros = []

    if filtros["Dim1"]:
        query += " AND LOWER(Dim1) = ?"
        parametros.append(filtros["Dim1"].lower())
    if filtros["ano_inicio"] and filtros["ano_final"]:
        query += " AND Period BETWEEN ? AND ?"
        parametros.append(filtros["ano_inicio"])
        parametros.append(filtros["ano_final"])
    if filtros["Location"]:
        query += " AND LOWER(Location) = ?"
        parametros.append(filtros["Location"].lower())
    if filtros.get("ParentLocation") and filtros["ParentLocation"] != "Todos":
        query += " AND LOWER(ParentLocation) = ?"
        parametros.append(filtros["ParentLocation"].lower())

    return query, parametros
'''
def executar_busca(cursor, query, parametros):
    cursor.execute(query, parametros) #executa a consulta passando por cada parametro usado
    resultado = cursor.fetchall() #pega os resultados vindos do banco
    return resultado
'''
def main():
    conexao, cursor = conectar_bd(caminho_bd)

    while True:

        filtros = ler_filtros()
        query, parametros = montar_query(filtros)

        print("\nExecutando busca...")
        resultados_sql = pd.read_sql_query(query, conexao, params=parametros)
        # conecta no SQL, roda a busca e já organiza as colunas para você.

        '''
        if resultados_sql:
            for linha in resultados_sql:
                print(linha)
        '''
        if not resultados_sql.empty:
            print("\n==========TABELA DE RESULTADOS==========\n")
            print(resultados_sql.to_string(index=False))
        else:
            print("Nenhum resultado foi encontrado.")

        escolha = input("\nDeseja fazer outra pesquisa? (s/n): ").strip().lower()
        if escolha != "s":
            print("Encerrando.")
            break

    conexao.close()

if __name__ == "__main__":
    main()