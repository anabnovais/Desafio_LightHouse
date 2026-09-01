import psycopg2
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lighthouse",
    "user": "postgres",
    "password": "lighthouse123",
}

PRODUTO_REFERENCIA = "Motor de Popa 1949"
TOP_N = 5


QUERY_INTERACOES = """
SELECT DISTINCT
    o.customer_id,
    p.id AS product_id,
    p.name AS product_name
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN product_variants pv ON pv.id = oi.product_variant_id
JOIN products p ON p.id = pv.product_id;
"""


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(QUERY_INTERACOES, conn)
    conn.close()

    matriz = pd.crosstab(df["customer_id"], df["product_id"])
    matriz = (matriz > 0).astype(int)

    print(f"Matriz de interação: {matriz.shape[0]} clientes x {matriz.shape[1]} produtos")

   
    similaridade = cosine_similarity(matriz.T)
    produtos_ids = matriz.columns.tolist()

    sim_df = pd.DataFrame(similaridade, index=produtos_ids, columns=produtos_ids)

    id_para_nome = df.drop_duplicates("product_id").set_index("product_id")["product_name"]

    ref_id = id_para_nome[id_para_nome == PRODUTO_REFERENCIA].index
    if len(ref_id) == 0:
        raise ValueError(f"Produto '{PRODUTO_REFERENCIA}' não encontrado.")
    if len(ref_id) > 1:
        print(f"Aviso: mais de um product_id encontrado para '{PRODUTO_REFERENCIA}': {list(ref_id)}. Usando o primeiro.")
    ref_id = ref_id[0]

    ranking = (
        sim_df[ref_id]
        .drop(index=ref_id)  
        .sort_values(ascending=False)
        .head(TOP_N)
    )

    print(f"\nTop {TOP_N} produtos mais similares a '{PRODUTO_REFERENCIA}':\n")
    for product_id, score in ranking.items():
        nome = id_para_nome[product_id]
        print(f"  {nome:<30} similaridade = {score:.4f}")


if __name__ == "__main__":
    main()