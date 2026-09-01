import psycopg2
import matplotlib.pyplot as plt

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lighthouse",
    "user": "postgres",
    "password": "lighthouse123",
}

QUERY_TOP10 = """
WITH cliente_metrica AS (
    SELECT
        o.customer_id,
        SUM(o.total) AS faturamento_total,
        COUNT(o.id) AS frequencia,
        SUM(o.total) / COUNT(o.id) AS ticket_medio
    FROM orders o
    GROUP BY o.customer_id
),
diversidade AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    JOIN product_variants pv ON pv.id = oi.product_variant_id
    JOIN products p ON p.id = pv.product_id
    GROUP BY o.customer_id
)
SELECT
    cm.customer_id,
    cm.ticket_medio,
    d.diversidade_categorias
FROM cliente_metrica cm
JOIN diversidade d ON d.customer_id = cm.customer_id
WHERE d.diversidade_categorias >= 13
ORDER BY cm.ticket_medio DESC, cm.customer_id ASC
LIMIT 10;
"""

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute(QUERY_TOP10)
resultado = cur.fetchall()
cur.close()
conn.close()

# resultado = [(customer_id, ticket_medio, diversidade), ...]
clientes = [f"Cliente {row[0]}" for row in resultado]
tickets = [float(row[1]) for row in resultado]

plt.figure(figsize=(10, 6))
plt.barh(clientes, tickets, color="steelblue")
plt.xlabel("Ticket Médio (R$)")
plt.title("Top 10 Clientes de Elite por Ticket Médio (13+ categorias)")
plt.gca().invert_yaxis()  # maior ticket no topo
plt.tight_layout()
plt.savefig("top10_ticket_medio.png")
plt.show()