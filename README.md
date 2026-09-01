# Desafio_LightHouse
Resolução do desafio de dados e IA proposto pela Lighthouse, usando como base uma empresa fictícia do setor náutico (LH Nautical). O desafio é dividido em 7 questões, cobrindo desde exploração de dados até um sistema de recomendação por similaridade de compra.

# Cenário

A LH Nautical forneceu sua base operacional em CSV (24 tabelas, sem acesso direto ao banco de dados). O objetivo é validar a confiabilidade dos dados, modelar e carregar essa base num banco relacional, e a partir dela responder perguntas de negócio feitas pela diretoria — identificação de clientes fiéis, correção de uma métrica calculada incorretamente, previsão de demanda para evitar rupturas de estoque, e recomendação de produtos.

# Estrutura do repositório
```
├── docker-compose.yml       # Sobe o PostgreSQL usado pelas Questões 3 a 7
├── Questao1/
│   └── analise.py           # Análise exploratória inicial (EDA)
├── Questao2/
│   ├── schema.py            # Gera o schema.sql a partir dos CSVs
│   └── schema.sql           # DDL gerado (CREATE TABLE de cada tabela)
├── Questao3/
│   └── carregamento.py      # Carrega os CSVs no PostgreSQL
├── Questao4/
│   ├── main.py               # Ranking de clientes de elite
│   └── top10_ticket_medio.png
├── Questao5/
│   ├── main.py               # Dimensão de calendário + vendas por dia da semana
│   └── media_vendas_dia_semana.png
├── Questao6/
│   ├── main.py               # Previsão de demanda (baseline de média móvel)
│   └── previsao_demanda.png
└── Questao7/
    └── main.py               # Sistema de recomendação (similaridade de cosseno)
````