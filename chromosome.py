"""
Módulo contendo a classe base Chromosome para algoritmos genéticos.

Esta classe define a interface que todos os cromossomos devem implementar
para serem utilizados no algoritmo genético.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Tuple

T = TypeVar('T', bound='Chromosome')

class Chromosome(ABC):
    """
    Classe base para representar um cromossomo genético.
    
    Esta classe abstrata define os métodos que devem ser implementados
    por qualquer cromossomo utilizado no algoritmo genético.
    """
    
    @abstractmethod
    def fitness(self) -> float:
        """
        Calcula e retorna o valor de aptidão (fitness) do cromossomo.
        
        Returns:
            float: Valor de aptidão do cromossomo
        """
        pass

    @abstractmethod
    def mutate(self) -> None:
        """
        Realiza mutação no cromossomo.
        
        Este método deve modificar o cromossomo in-place.
        """
        pass

    @abstractmethod
    def crossover(self, other: T) -> Tuple[T, T]:
        """
        Realiza cruzamento com outro cromossomo.
        
        Args:
            other: Outro cromossomo para cruzamento
            
        Returns:
            Tuple[T, T]: Dois novos cromossomos resultantes do cruzamento
        """
        pass

    @classmethod
    @abstractmethod
    def random_instance(cls) -> T:
        """
        Cria uma instância aleatória do cromossomo.
        
        Returns:
            T: Nova instância aleatória do cromossomo
        """
        pass
