from functools import reduce
from random import random, uniform
import numpy as np
import pandas as pd
from chromossome import Chromossome
from typing import TypeVar, Tuple

T = TypeVar('T', bound='Chromossome')

class Portfolio(Chromossome):
    """
        Classe que representa um portfolio de ativos.
    """
    def __init__(self, weights: dict, returns: pd.DataFrame, risk_free_rate: float = 0.2) -> None:
        self._weights = weights
        self.returns = returns
        self.risk_free_rate = risk_free_rate
    
    @property
    def weights(self) -> dict:
        """
        Retorna um dicionário com os pesos dos ativos.
        """
        total = sum(self._weights.values())
        if total == 0:
            raise ValueError("A soma dos valores no dicionário é zero. Não é possível normalizar os pesos.")
        
        normalized_weight = {k: v / total for k, v in self._weights.items()}
        return normalized_weight
    
    def fitness(self,alpha=0.95) -> float:
        """
        Retorna a medida de risco e de retorno do portfolio.
        Parameters
        ------
        alpha : float, optional
            Taxa de confiança para o cálculo, por padrão 0.95.

        Returns
        ------
        float: 
          Aptidão do portfolio.
        """        
        weights_array = np.array(list(self.weights.values())) # Converte os pesos do portfólio em um array numpy para cálculos vetorizados   
        mean_return = self.returns.mean() # Calcula o retorno médio de cada ativo no portfólio      
        portfolio_returns = self.returns.dot(weights_array) # Calcula os retornos do portfólio como um todo, usando produto escalar (média ponderada)
        self.ExpReturn = portfolio_returns.mean() # Calcula o retorno esperado como a média dos retornos do portfólio
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
        Parameters
        ------
        other : T
            Outro portfólio para realizar o crossover.
        Returns
        ------
        Tuple[T, T]:
            Dois portfólios resultantes do crossover.
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
        Parameters
        ------
        mutation_rate : float, optional
            Taxa de mutação, por padrão 0.2.
        """
        for key in self._weights:
            if random() < mutation_rate:
                self._weights[key] = max(0, self._weights[key] + uniform(-0.1, 0.1))
    
    @classmethod
    def random_instance(cls, weights, returns, risk_free_rate=0.2):
        random_weights = {k: uniform(0, 1) for k in weights}
        return Portfolio(weights=random_weights, returns=returns, risk_free_rate=risk_free_rate)
    
    def __repr__(self) -> str:
        return f"Portfolio({self.weights}, {self.returns}, {self.risk_free_rate})"
    
        
