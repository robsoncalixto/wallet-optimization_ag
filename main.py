import pandas as pd
import numpy as np
import os 
import sys
import matplotlib.pyplot as plt
from dados import ColetorDados
from portfolio import Portfolio
from geneticAlgorithm import GeneticAlgorithm
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))

POPULATION_SIZE = 10
GENERATIONS = 50
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.5
RISK_FREE_RATE = 0.5

def load_stocks():
    stocks = pd.read_csv("data/empresas_br_bovespa.csv")
    return stocks

def stocks_history(tickers):
    coletor = ColetorDados(tickers)
    returns = coletor.baixar_dados()
    return returns

def select_top_stocks_by_return(stocks_df, returns_df, top_n=20):
    """
    Seleciona as top N ações baseado no retorno médio
    """
    # Calcula retorno médio de cada ação
    mean_returns = returns_df.mean().sort_values(ascending=False)
    
    # Seleciona os top N tickers
    top_tickers = mean_returns.head(top_n).index.tolist()
    
    # Filtra o DataFrame de ações
    top_stocks = stocks_df[stocks_df['Ticker'].isin(top_tickers)]
    
    # Filtra os retornos para apenas as ações selecionadas
    top_returns = returns_df[top_tickers]
    
    print(f" TOP {top_n} AÇÕES POR RETORNO MÉDIO:")
    for i, (ticker, ret) in enumerate(mean_returns.head(top_n).items(), 1):
        print(f"{i:2d}. {ticker:<12} Retorno médio: {ret:.6f}")
    
    return top_stocks, top_returns

if __name__ == "__main__":
    print("=== OTIMIZAÇÃO DE PORTFÓLIO COM ALGORITMO GENÉTICO ===\n")
    
    # Carrega todas as ações e seus históricos
    cias = load_stocks()
    print(f" Total de ações disponíveis: {len(cias)}")
    
    # Obtém histórico de todas as ações
    all_stk_hist = stocks_history(cias["Ticker"])
    print(f"Dados históricos obtidos: {all_stk_hist.shape[0]} dias, {all_stk_hist.shape[1]} ativos")
    
    # Seleciona as top 20 ações por retorno
    top_stocks, stk_hist = select_top_stocks_by_return(cias, all_stk_hist, top_n=20)
    print(f"\n Otimização usando {stk_hist.shape[1]} melhores ações")
    print(f"Período: {stk_hist.shape[0]} dias de dados\n")

    # Aplica o mesmo peso para todos os ativos selecionados
    N = stk_hist.shape[1]
    weights = [1/N]*N
    weights_dict = dict(zip(stk_hist.columns, weights))

    # ========== ALGORITMO GENÉTICO CUSTOMIZADO ==========
    print(" EXECUTANDO ALGORITMO GENÉTICO CUSTOMIZADO...")
    start_time = time.time()
    
    # Cria o portfolio base
    portfolio = Portfolio(weights=weights_dict, returns=stk_hist, risk_free_rate=RISK_FREE_RATE)

    # Cria a população inicial
    population = [portfolio.random_instance(weights_dict, stk_hist, RISK_FREE_RATE) for _ in range(POPULATION_SIZE)]
    
    ga_custom = GeneticAlgorithm(
        population=population,
        fitness_key=lambda p: p.fitness(),
        max_generations=GENERATIONS,
        mutation_rate=MUTATION_RATE,
        crossover_rate=CROSSOVER_RATE,
        selection_type=GeneticAlgorithm.SelectionType.TOURNAMENT,
        threshold=13.0
    )

    result_custom = ga_custom.run()
    custom_time = time.time() - start_time
    custom_fitness = result_custom.fitness()
    custom_weights = result_custom.weights
    
    print(f"\n RESULTADO DA OTIMIZAÇÃO:")
    print(f"Tempo de execução: {custom_time:.2f}s")
    print(f"Melhor fitness: {custom_fitness:.6f}")
    print(f"Retorno esperado: {result_custom.ExpReturn:.6f}")
    print(f"CVaR (risco): {result_custom.cvar:.6f}")
    
    # Exibir pesos detalhados
    print(f"\n COMPOSIÇÃO DO PORTFÓLIO OTIMIZADO:")
    print(f"{'Ativo':<12} {'Peso':<8} {'%':<8}")
    print("-" * 28)
    for ativo, peso in custom_weights.items():
        print(f"{ativo:<12} {peso:<8.4f} {peso*100:<8.2f}%")
    
    ga_custom.show_results()