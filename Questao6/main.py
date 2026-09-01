import psycopg2
import matplotlib.pyplot as plt

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "lighthouse",
    "user": "postgres",
    "password": "lighthouse123",
}

PRODUCT_NAME = "Bússola de Bordo 702"

QUERY_VENDAS_MENSAIS = """
SELECT
    TO_CHAR(o.placed_at, 'YYYY-MM') AS mes,
    SUM(oi.quantity) AS unidades_vendidas
FROM products p
JOIN product_variants pv ON pv.product_id = p.id
JOIN order_items oi ON oi.product_variant_id = pv.id
JOIN orders o ON o.id = oi.order_id
WHERE p.name = %s
  AND o.status <> 'cancelled'
GROUP BY TO_CHAR(o.placed_at, 'YYYY-MM')
ORDER BY mes;
"""

TREINO_ATE = "2025-12"
MESES_TESTE = ["2026-01", "2026-02", "2026-03"]


def mes_seguinte(mes_str):
    ano, mes = map(int, mes_str.split("-"))
    if mes == 12:
        return f"{ano + 1}-01"
    return f"{ano}-{mes + 1:02d}"


def montar_serie_continua(vendas_mensais):
    meses_ordenados = sorted(vendas_mensais)
    primeiro, ultimo = meses_ordenados[0], meses_ordenados[-1]

    serie = {}
    m = primeiro
    while True:
        serie[m] = vendas_mensais.get(m, 0)
        if m == ultimo:
            break
        m = mes_seguinte(m)
    return serie


def calcular_baseline_media_movel(serie, meses_teste, janela=3):
    meses = sorted(serie)
    previsoes = {}

    for mes_previsto in meses_teste:
        idx = meses.index(mes_previsto)
        janela_meses = meses[idx - janela: idx]
        valores = [serie[m] for m in janela_meses]
        previsoes[mes_previsto] = sum(valores) / len(valores)

    return previsoes

def calcular_mae(serie, previsoes, meses_teste):
    erros = [abs(serie[m] - previsoes[m]) for m in meses_teste]
    return sum(erros) / len(erros)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute(QUERY_VENDAS_MENSAIS, (PRODUCT_NAME,))
        linhas = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    vendas_mensais = {mes: int(qtd) for mes, qtd in linhas}
    serie = montar_serie_continua(vendas_mensais)

    previsoes = calcular_baseline_media_movel(serie, MESES_TESTE, janela=3)
    mae = calcular_mae(serie, previsoes, MESES_TESTE)

    print(f"Baseline: média móvel dos últimos 3 meses (walk-forward)\n")
    print(f"{'Mês':<10}{'Real':>8}{'Previsto':>12}{'Erro Abs':>12}")
    for mes in MESES_TESTE:
        real = serie[mes]
        previsto = previsoes[mes]
        print(f"{mes:<10}{real:>8}{previsto:>12.2f}{abs(real - previsto):>12.2f}")

    print(f"\nMAE (1º trimestre 2026): {mae:.2f} unidades")

    reais = [serie[m] for m in MESES_TESTE]
    previstos = [previsoes[m] for m in MESES_TESTE]

    x = range(len(MESES_TESTE))
    largura = 0.35

    plt.figure(figsize=(9, 6))
    plt.bar([i - largura / 2 for i in x], reais, width=largura, label="Real", color="steelblue")
    plt.bar([i + largura / 2 for i in x], previstos, width=largura, label="Previsto (média móvel 3m)", color="darkorange")
    plt.xticks(list(x), MESES_TESTE)
    plt.ylabel("Unidades vendidas")
    plt.title(f"Previsão de demanda — {PRODUCT_NAME}\nReal vs. Baseline (MAE = {mae:.2f})")
    plt.legend()
    plt.tight_layout()
    plt.savefig("previsao_demanda.png")
    plt.show()


if __name__ == "__main__":
    main()