import pandas as pd 

orders = pd.read_csv('1-lh_nautical_csv/orders.csv')

#PARTE 1
#Quantidade total de linhas 
print("Quantidade total de linhas:", orders.shape[0])

#Quantidade total de colunas 
print("Quantidade total de colunas:", orders.shape[1])
orders["created_at"] = pd.to_datetime(orders["created_at"])
data_minima = orders["created_at"].min()
data_maxima = orders["created_at"].max()

intervalo_dias = (data_maxima - data_minima).days
print("Intervalo de dias:", intervalo_dias)

#PARTE 2 

#VALOR MINIMO DA COLUNA "TOTAL"

valor_minimo = orders["total"].min()
print("Valor mínimo da coluna 'total':", valor_minimo)

#VALOR MAXIMO DA COLUNA "TOTAL"
valor_maximo = orders["total"].max()
print("Valor máximo da coluna 'total':", valor_maximo)


#VALOR MAXIMO DA COLUNA "TOTAL"
valor_medio = orders["total"].mean()
print("Valor médio da coluna 'total':", valor_medio)

print("Resumo estatístico da coluna 'total':")
print(orders["total"].describe())

# Compare a média com a mediana — se forem muito diferentes, há outliers puxando a média
print("Mediana:", orders["total"].median())

# Olhe os quartis pra ver o "salto" entre Q3 e o máximo
print(orders["total"].quantile([0.25, 0.5, 0.75, 0.95, 0.99]))

print(orders.isnull().sum())          
print((orders["total"] < 0).sum())    
print(orders.duplicated().sum())      
print(orders["status"].unique())     