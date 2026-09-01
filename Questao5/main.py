import csv
import psycopg2
import matplotlib.pyplot as plt

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lighthouse",
    "user": "postgres",
    "password": "lighthouse123",
}

# Ordem "natural" da semana para exibir o gráfico e a tabela de forma legível
ORDEM_DIAS = [
    "Domingo",
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
]

QUERY_DETALHE_DIARIO = """
WITH limites AS (
    SELECT
        MIN(placed_at)::date AS data_min,
        MAX(placed_at)::date AS data_max
    FROM orders
    WHERE channel = 'pos'
),

dim_calendario AS (
    SELECT
        gs::date AS data,
        CASE EXTRACT(DOW FROM gs)
            WHEN 0 THEN 'Domingo'
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
        END AS dia_semana
    FROM limites, generate_series(data_min, data_max, interval '1 day') AS gs
),

vendas_diarias AS (
    SELECT
        placed_at::date AS data,
        SUM(total) AS valor_vendido
    FROM orders
    WHERE channel = 'pos'
    GROUP BY placed_at::date
)

SELECT
    dc.data,
    dc.dia_semana,
    COALESCE(vd.valor_vendido, 0) AS vendas_diarias
FROM dim_calendario dc
LEFT JOIN vendas_diarias vd ON vd.data = dc.data
ORDER BY dc.data;
"""

QUERY_MEDIA_POR_DIA = """
WITH limites AS (
    SELECT
        MIN(placed_at)::date AS data_min,
        MAX(placed_at)::date AS data_max
    FROM orders
    WHERE channel = 'pos'
),

dim_calendario AS (
    SELECT
        gs::date AS data,
        CASE EXTRACT(DOW FROM gs)
            WHEN 0 THEN 'Domingo'
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
        END AS dia_semana
    FROM limites, generate_series(data_min, data_max, interval '1 day') AS gs
),

vendas_diarias AS (
    SELECT
        placed_at::date AS data,
        SUM(total) AS valor_vendido
    FROM orders
    WHERE channel = 'pos'
    GROUP BY placed_at::date
)

SELECT
    dc.dia_semana,
    ROUND(AVG(COALESCE(vd.valor_vendido, 0)), 2) AS media_vendas
FROM dim_calendario dc
LEFT JOIN vendas_diarias vd ON vd.data = dc.data
GROUP BY dc.dia_semana;
"""


def buscar_media_por_dia(cur):
    cur.execute(QUERY_MEDIA_POR_DIA)
    resultado = dict(cur.fetchall()) 
    return [(dia, float(resultado[dia])) for dia in ORDEM_DIAS if dia in resultado]


def exportar_detalhe_diario(cur, caminho="detalhe_diario.csv"):
    cur.execute(QUERY_DETALHE_DIARIO)
    linhas = cur.fetchall()

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["data", "dia_semana", "vendas_diarias"])
        for data, dia_semana, vendas in linhas:
            writer.writerow([data, dia_semana, float(vendas)])

    print(f"Detalhe diário exportado para '{caminho}' ({len(linhas)} dias).")


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        media_por_dia = buscar_media_por_dia(cur)
        exportar_detalhe_diario(cur)
    finally:
        cur.close()
        conn.close()

    print("Média de vendas por dia da semana (lojas físicas, calendário completo):\n")
    for dia, media in sorted(media_por_dia, key=lambda x: x[1]):
        print(f"  {dia:<15} R$ {media:,.2f}")

    pior_dia, pior_valor = min(media_por_dia, key=lambda x: x[1])
    print(f"\nPior dia da semana: {pior_dia} (média de R$ {pior_valor:,.2f})")

    # Gráfico
    dias = [d for d, _ in media_por_dia]
    valores = [v for _, v in media_por_dia]

    cores = ["crimson" if d == pior_dia else "steelblue" for d in dias]

    plt.figure(figsize=(10, 6))
    plt.bar(dias, valores, color=cores)
    plt.ylabel("Média de vendas (R$)")
    plt.title("Vendas médias por dia da semana (considerando dias sem venda)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("media_vendas_dia_semana.png")
    plt.show()


if __name__ == "__main__":
    main()