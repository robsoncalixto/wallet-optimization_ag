"""
Módulo contendo a classe Portfolio para otimização de carteiras.

Esta classe implementa um portfólio de investimentos como um cromossomo
para uso em algoritmos genéticos.
"""

from functools import reduce
from random import random, uniform
import numpy as np
import pandas as pd
from chromosome import Chromosome
from typing import TypeVar, Tuple

T = TypeVar('T', bound='Chromosome')

class Portfolio(Chromosome):
    """
    Classe que representa um portfólio de ativos como cromossomo genético.
    
    Esta classe implementa um portfólio de investimentos que pode ser
    otimizado usando algoritmos genéticos.
    """
    
    def __init__(self, weights: dict, returns: pd.DataFrame, risk_free_rate: float = 0.2) -> None:
        """
        Inicializa um portfólio.
        
        Args:
            weights: Dicionário com pesos dos ativos
            returns: DataFrame com retornos históricos dos ativos
            risk_free_rate: Taxa livre de risco
        """
        self._weights = weights
        self.returns = returns
        self.risk_free_rate = risk_free_rate
    
    @property
    def weights(self) -> dict:
        """Retorna um dicionário com os pesos normalizados dos ativos."""
        total = sum(self._weights.values())
        if total == 0:
            raise ValueError("A soma dos valores no dicionário é zero. Não é possível normalizar os pesos.")
        
        normalized_weight = {k: v / total for k, v in self._weights.items()}
        return normalized_weight
    
    def fitness(self, alpha: float = 0.95) -> float:
        """
        Calcula a aptidão do portfólio baseada em retorno e risco.
        
        Args:
            alpha: Taxa de confiança para cálculo do VaR
            
        Returns:
            float: Valor de aptidão do portfólio
        """        
        # Converte os pesos do portfólio em um array numpy para cálculos vetorizados   
        weights_array = np.array(list(self.weights.values()))
        # Calcula o retorno médio de cada ativo no portfólio      
        mean_return = self.returns.mean()
        # Calcula os retornos do portfólio como um todo, usando produto escalar (média ponderada)
        portfolio_returns = self.returns.dot(weights_array)
        # Calcula o retorno esperado como a média dos retornos do portfólio
        self.ExpReturn = portfolio_returns.mean()
        
        # Calcula o valor de risco (VaR) usando o percentil correto
        # Para VaR com confiança de 95%, usamos o percentil 5 (os piores 5% dos retornos)
        portfolio_var = np.percentile(portfolio_returns, (1-alpha)*100)
        
        # Calcula o Conditional Value at Risk (CVaR), que é a média dos retornos abaixo do VaR
        # Isso representa a perda média esperada nos piores cenários
        self.cvar = portfolio_returns[portfolio_returns <= portfolio_var].mean()
        
        # Retorna a função de aptidão final que equilibra retorno e risco
        # Maximiza o retorno ajustado pela taxa de aversão ao risco e penaliza pelo CVaR
        return (1 - self.risk_free_rate) * mean_return.dot(weights_array) - self.risk_free_rate * self.cvar

    def crossover(self, other: T) -> Tuple[T, T]:
        """
        Realiza o crossover entre dois portfólios.
        
        Args:
            other: Outro portfólio para realizar o crossover
            
        Returns:
            Tuple[T, T]: Dois portfólios resultantes do crossover
        """
        w1 = self.weights
        w2 = other.weights

        mid = len(w1) // 2

        new_w1 = {k: w1[k] for k in list(w1.keys())[:mid]}
        new_w1.update({k: w2[k] for k in list(w2.keys())[mid:]})

        new_w2 = {k: w2[k] for k in list(w2.keys())[:mid]}
        new_w2.update({k: w1[k] for k in list(w1.keys())[mid:]})

        child1 = Portfolio(weights=new_w1, returns=self.returns, risk_free_rate=self.risk_free_rate)
        child2 = Portfolio(weights=new_w2, returns=self.returns, risk_free_rate=self.risk_free_rate)
        return child1, child2

    def mutate(self, mutation_rate: float = 0.2) -> None:
        """
        Realiza a mutação em um portfólio.
        
        Args:
            mutation_rate: Taxa de mutação
        """
        for key in self._weights:
            if random() < mutation_rate:
                self._weights[key] = max(0, self._weights[key] + uniform(-0.1, 0.1))
    
    @classmethod
    def random_instance(cls, weights, returns, risk_free_rate=0.2):
        """
        Cria uma instância aleatória de portfólio.
        
        Args:
            weights: Dicionário base de pesos
            returns: DataFrame de retornos
            risk_free_rate: Taxa livre de risco
            
        Returns:
            Portfolio: Nova instância aleatória
        """
        random_weights = {k: uniform(0, 1) for k in weights}
        return Portfolio(weights=random_weights, returns=returns, risk_free_rate=risk_free_rate)
    
    def __repr__(self) -> str:
        return f"Portfolio({self.weights}, {self.returns}, {self.risk_free_rate})"
