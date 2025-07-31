"""
Testes para o módulo chromosome.py

Este módulo contém testes abrangentes para a classe abstrata Chromosome,
incluindo testes de implementação concreta para validar o comportamento esperado.
"""

import unittest
from abc import ABC
import sys
import os

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chromosome import Chromosome
from typing import Tuple


class ConcreteChromosome(Chromosome):
    
    def __init__(self, value: float = 0.0):
        self.value = value
        self._fitness_value = None
    
    def fitness(self) -> float:
        if self._fitness_value is None:
            self._fitness_value = self.value
        return self._fitness_value
    
    def mutate(self) -> None:
        self.value += 0.1
        self._fitness_value = None  # Reset fitness cache
    
    def crossover(self, other: 'ConcreteChromosome') -> Tuple['ConcreteChromosome', 'ConcreteChromosome']:
        child1_value = (self.value + other.value) / 2 + 0.1
        child2_value = (self.value + other.value) / 2 - 0.1
        return ConcreteChromosome(child1_value), ConcreteChromosome(child2_value)
    
    @classmethod
    def random_instance(cls) -> 'ConcreteChromosome':
        import random
        return cls(random.uniform(0, 100))
    
    def __eq__(self, other):
        if not isinstance(other, ConcreteChromosome):
            return False
        return abs(self.value - other.value) < 1e-10


class TestChromosome(unittest.TestCase):
        
    def setUp(self):
        self.chromosome1 = ConcreteChromosome(10.0)
        self.chromosome2 = ConcreteChromosome(20.0)
    
    def test_chromosome_is_abstract(self):
        self.assertTrue(issubclass(Chromosome, ABC))
        
        # Verifica se não é possível instanciar diretamente
        with self.assertRaises(TypeError):
            Chromosome()
    
    def test_abstract_methods_exist(self):
        abstract_methods = Chromosome.__abstractmethods__
        expected_methods = {'fitness', 'mutate', 'crossover', 'random_instance'}
        self.assertEqual(abstract_methods, expected_methods)
    
    def test_concrete_implementation_fitness(self):
        self.assertEqual(self.chromosome1.fitness(), 10.0)
        self.assertEqual(self.chromosome2.fitness(), 20.0)
        
        # Testa se o fitness é consistente
        self.assertEqual(self.chromosome1.fitness(), self.chromosome1.fitness())
    
    def test_concrete_implementation_mutate(self):
        original_value = self.chromosome1.value
        self.chromosome1.mutate()
        
        # Verifica se o valor foi modificado
        self.assertNotEqual(self.chromosome1.value, original_value)
        self.assertEqual(self.chromosome1.value, original_value + 0.1)
        
        # Verifica se o fitness foi resetado
        self.assertEqual(self.chromosome1.fitness(), self.chromosome1.value)
    
    def test_concrete_implementation_crossover(self):
        child1, child2 = self.chromosome1.crossover(self.chromosome2)
        
        # Verifica se retorna uma tupla com dois elementos
        self.assertIsInstance((child1, child2), tuple)
        self.assertEqual(len((child1, child2)), 2)
        
        # Verifica se os filhos são instâncias da classe correta
        self.assertIsInstance(child1, ConcreteChromosome)
        self.assertIsInstance(child2, ConcreteChromosome)
        
        # Verifica se os valores dos filhos são baseados nos pais
        expected_avg = (self.chromosome1.value + self.chromosome2.value) / 2
        self.assertEqual(child1.value, expected_avg + 0.1)
        self.assertEqual(child2.value, expected_avg - 0.1)
    
    def test_concrete_implementation_random_instance(self):
        random_chromosome = ConcreteChromosome.random_instance()
        
        # Verifica se é uma instância da classe correta
        self.assertIsInstance(random_chromosome, ConcreteChromosome)
        
        # Verifica se o valor está no range esperado
        self.assertGreaterEqual(random_chromosome.value, 0)
        self.assertLessEqual(random_chromosome.value, 100)
        
        # Verifica se instâncias diferentes têm valores diferentes (probabilisticamente)
        random_chromosome2 = ConcreteChromosome.random_instance()
        self.assertNotEqual(random_chromosome.value, random_chromosome2.value)
    
    def test_type_hints(self):
            # Verifica se o crossover retorna o tipo correto
        child1, child2 = self.chromosome1.crossover(self.chromosome2)
        self.assertIsInstance(child1, type(self.chromosome1))
        self.assertIsInstance(child2, type(self.chromosome1))
        
        # Verifica se random_instance retorna o tipo correto
        random_instance = ConcreteChromosome.random_instance()
        self.assertIsInstance(random_instance, ConcreteChromosome)
    
    def test_fitness_return_type(self):
        fitness_value = self.chromosome1.fitness()
        self.assertIsInstance(fitness_value, (int, float))
    
    def test_mutate_modifies_in_place(self):
        original_id = id(self.chromosome1)
        self.chromosome1.mutate()
        
        # Verifica se é o mesmo objeto
        self.assertEqual(id(self.chromosome1), original_id)
    
    def test_crossover_creates_new_instances(self):
        child1, child2 = self.chromosome1.crossover(self.chromosome2)
        
        # Verifica se são objetos diferentes dos pais
        self.assertNotEqual(id(child1), id(self.chromosome1))
        self.assertNotEqual(id(child1), id(self.chromosome2))
        self.assertNotEqual(id(child2), id(self.chromosome1))
        self.assertNotEqual(id(child2), id(self.chromosome2))
        
        # Verifica se os filhos são diferentes entre si
        self.assertNotEqual(id(child1), id(child2))


class TestChromosomeEdgeCases(unittest.TestCase):
        
    def test_zero_fitness(self):
        chromosome = ConcreteChromosome(0.0)
        self.assertEqual(chromosome.fitness(), 0.0)
    
    def test_negative_fitness(self):
        chromosome = ConcreteChromosome(-10.0)
        self.assertEqual(chromosome.fitness(), -10.0)
    
    def test_large_fitness_values(self):
        chromosome = ConcreteChromosome(1e6)
        self.assertEqual(chromosome.fitness(), 1e6)
    
    def test_multiple_mutations(self):
        chromosome = ConcreteChromosome(10.0)
        original_value = chromosome.value
        
        for i in range(5):
            chromosome.mutate()
        
        expected_value = original_value + (5 * 0.1)
        self.assertAlmostEqual(chromosome.value, expected_value, places=10)
    
    def test_crossover_with_same_values(self):
        chromosome1 = ConcreteChromosome(15.0)
        chromosome2 = ConcreteChromosome(15.0)
        
        child1, child2 = chromosome1.crossover(chromosome2)
        
        self.assertEqual(child1.value, 15.1)
        self.assertEqual(child2.value, 14.9)


if __name__ == '__main__':
    # Configuração para executar os testes
    unittest.main(verbosity=2)
