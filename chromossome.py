from abc import ABC, abstractmethod
from typing import TypeVar, Tuple

T = TypeVar('T', bound='Chromossome')
class Chromossome(ABC):
    """
    Classe base para representar um cromossomo genético.
    """
    @abstractmethod
    def fitness(self) -> float:
        pass

    @abstractmethod
    def mutate(self) -> T:
        pass

    @abstractmethod
    def crossover(self, other: T) -> Tuple[T, T]:
        pass

    @classmethod
    @abstractmethod
    def random_instance(cls) -> T:
        pass