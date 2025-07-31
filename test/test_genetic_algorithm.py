"""
Testes para o módulo genetic_algorithm.py

Este módulo contém testes abrangentes para a classe GeneticAlgorithm,
incluindo testes de funcionalidade, convergência e diferentes estratégias
de seleção e otimização.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
import numpy as np
import sys
import os
from typing import Tuple

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from genetic_algorithm import GeneticAlgorithm
from chromosome import Chromosome


class MockChromosome(Chromosome):
    """
    Implementação mock da classe Chromosome para testes.
    
    Esta classe simula um cromossomo simples com valor numérico
    para testar o algoritmo genético.
    """
    
    def __init__(self, value: float = 0.0):
        self.value = value
        self._fitness_cache = None
    
    def fitness(self) -> float:
        if self._fitness_cache is None:
            self._fitness_cache = self.value
        return self._fitness_cache
    
    def mutate(self) -> None:
        import random
        self.value += random.uniform(-0.1, 0.1)
        self._fitness_cache = None
    
    def crossover(self, other: 'MockChromosome') -> Tuple['MockChromosome', 'MockChromosome']:
        avg = (self.value + other.value) / 2
        child1 = MockChromosome(avg + 0.05)
        child2 = MockChromosome(avg - 0.05)
        return child1, child2
    
    @classmethod
    def random_instance(cls) -> 'MockChromosome':
        import random
        return cls(random.uniform(0, 10))
    
    def __repr__(self):
        return f"MockChromosome({self.value:.3f})"


class TestGeneticAlgorithmInitialization:
    
    def setup_method(self):
        self.population = [MockChromosome(i) for i in range(10)]
        self.threshold = 9.0
        self.max_generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
    
    def test_inicializar_basico(self):
        ga = GeneticAlgorithm(
            population=self.population,
            threshold=self.threshold,
            max_generations=self.max_generations,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate
        )
        
        assert ga._population == self.population
        assert ga._threshold == self.threshold
        assert ga._max_generations == self.max_generations
        assert ga._mutation_rate == self.mutation_rate
        assert ga._crossover_rate == self.crossover_rate
        assert ga._selection_type == GeneticAlgorithm.SelectionType.TOURNAMENT
        assert ga._elitism
    
    def test_inicializar_com_tipo_selecao_customizado(self):
        ga = GeneticAlgorithm(
            population=self.population,
            threshold=self.threshold,
            max_generations=self.max_generations,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate,
            selection_type=GeneticAlgorithm.SelectionType.TOURNAMENT
        )
        
        assert ga._selection_type == GeneticAlgorithm.SelectionType.TOURNAMENT
    
    def test_inicializar_com_chave_fitness_customizada(self):
        def custom_fitness(chromosome):
            return chromosome.value * 2
        
        ga = GeneticAlgorithm(
            population=self.population,
            threshold=self.threshold,
            max_generations=self.max_generations,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate,
            fitness_key=custom_fitness
        )
        
        assert ga._fitness_key == custom_fitness
    
    def test_inicializar_sem_elitismo(self):
        ga = GeneticAlgorithm(
            population=self.population,
            threshold=self.threshold,
            max_generations=self.max_generations,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate,
            elitism=False
        )
        
        assert not ga._elitism
    
    def test_inicializar_com_populacao_vazia(self):
        empty_population = []
        ga = GeneticAlgorithm(
            population=empty_population,
            threshold=self.threshold,
            max_generations=self.max_generations,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate
        )
        
        assert ga._population == empty_population


class TestSelectionType:
    
    def test_enum_tipo_selecao(self):
        assert GeneticAlgorithm.SelectionType.TOURNAMENT.value == "tournament"
    
    def test_tipo_selecao_disponivel(self):
        selection_types = list(GeneticAlgorithm.SelectionType)
        assert GeneticAlgorithm.SelectionType.TOURNAMENT in selection_types


class TestTournamentSelection:
    
    def setup_method(self):
        # Cria população com fitness conhecidos
        self.population = [MockChromosome(i) for i in range(10)]  # fitness 0-9
        self.ga = GeneticAlgorithm(
            population=self.population,
            threshold=9.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
    
    def test_escolher_torneio_retorna_tupla(self):
        result = self.ga._pick_tournament()
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_escolher_torneio_retorna_cromossomos(self):
        parent1, parent2 = self.ga._pick_tournament()
        assert isinstance(parent1, MockChromosome)
        assert isinstance(parent2, MockChromosome)
    
    def test_escolher_torneio_seleciona_melhor(self):
        # Com população pequena e muitos competidores, deve selecionar os melhores
        parent1, parent2 = self.ga._pick_tournament(competitors=8)
        
        # Os pais devem ter fitness alto
        assert parent1.fitness() >= 5.0
        assert parent2.fitness() >= 5.0
    
    def test_escolher_torneio_com_competidores_diferentes(self):
        # Testa com 2 competidores
        result_2 = self.ga._pick_tournament(competitors=2)
        assert len(result_2) == 2
        
        # Testa com 5 competidores
        result_5 = self.ga._pick_tournament(competitors=5)
        assert len(result_5) == 2
    
    def test_escolher_torneio_com_competidor_unico(self):
        result = self.ga._pick_tournament(competitors=1)
        assert len(result) == 2
        # Com 1 competidor, pode retornar o mesmo cromossomo duas vezes


class TestReduceReplace:
    
    def setup_method(self):
        self.population = [MockChromosome(i) for i in range(6)]
        self.ga = GeneticAlgorithm(
            population=self.population,
            threshold=5.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=1.0  # 100% crossover para teste
        )
    
    def test_reduzir_substituir_mantem_tamanho_populacao(self):
        original_size = len(self.ga._population)
        self.ga._reduce_replace()
        
        assert len(self.ga._population) == original_size
    
    def test_reduzir_substituir_cria_nova_populacao(self):
        original_population = self.ga._population.copy()
        self.ga._reduce_replace()
        
        # A população deve ser diferente (novos objetos)
        for i, chromosome in enumerate(self.ga._population):
            assert id(chromosome) != id(original_population[i])
    
    @patch('random.random')
    def test_reduzir_substituir_sem_crossover(self, mock_random):
        # Força random() a retornar valor alto (sem crossover)
        mock_random.return_value = 0.9
        
        ga = GeneticAlgorithm(
            population=self.population,
            threshold=5.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.5  # 50% crossover
        )
        
        ga._reduce_replace()
        
        # População deve ter o mesmo tamanho
        assert len(ga._population) == len(self.population)
    
    @patch('random.random')
    def test_reduzir_substituir_com_crossover_completo(self, mock_random):
        # Força random() a retornar valor baixo (sempre crossover)
        mock_random.return_value = 0.1
        
        ga = GeneticAlgorithm(
            population=self.population,
            threshold=5.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.5  # 50% crossover
        )
        
        ga._reduce_replace()
        
        # População deve ter o mesmo tamanho
        assert len(ga._population) == len(self.population)


class TestElitism:
    
    def setup_method(self):
        self.population = [MockChromosome(i) for i in range(10)]
        self.ga = GeneticAlgorithm(
            population=self.population,
            threshold=9.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism=True
        )
    
    def test_aplicar_elitismo_com_elitismo_habilitado(self):
        new_population = [MockChromosome(i * 0.5) for i in range(10)]  # fitness 0-4.5
        
        result = self.ga._apply_elitism(new_population)
        
        # Resultado deve ter o mesmo tamanho
        assert len(result) == len(self.population)
        
        # Deve conter alguns dos melhores da população original
        best_original = max(self.population, key=lambda x: x.fitness())
        result_fitness = [x.fitness() for x in result]
        
        # O melhor da população original deve estar no resultado
        assert best_original.fitness() in result_fitness
    
    def test_aplicar_elitismo_com_elitismo_desabilitado(self):
        ga_no_elitism = GeneticAlgorithm(
            population=self.population,
            threshold=9.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism=False
        )
        
        new_population = [MockChromosome(i * 0.5) for i in range(10)]
        result = ga_no_elitism._apply_elitism(new_population)
        
        # Deve retornar a nova população sem modificações
        assert result == new_population
    
    def test_aplicar_elitismo_calculo_tamanho_elite(self):
        # Com população de 10, elite deve ser 1 (max(1, 10//10))
        new_population = [MockChromosome(0) for _ in range(10)]
        result = self.ga._apply_elitism(new_population)
        
        # Deve ter pelo menos 1 elite
        best_original_fitness = max(x.fitness() for x in self.population)
        result_fitness = [x.fitness() for x in result]
        
        assert best_original_fitness in result_fitness
    
    def test_aplicar_elitismo_com_populacao_pequena(self):
        small_population = [MockChromosome(5), MockChromosome(3)]
        ga_small = GeneticAlgorithm(
            population=small_population,
            threshold=5.0,
            max_generations=10,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism=True
        )
        
        new_population = [MockChromosome(1), MockChromosome(2)]
        result = ga_small._apply_elitism(new_population)
        
        assert len(result) == 2
        # Deve preservar pelo menos o melhor
        assert 5.0 in [x.fitness() for x in result]


class TestMutation:
    
    def setup_method(self):
        self.population = [MockChromosome(5.0) for _ in range(5)]
        self.ga = GeneticAlgorithm(
            population=self.population,
            threshold=9.0,
            max_generations=10,
            mutation_rate=1.0,  # 100% para garantir mutação
            crossover_rate=0.8
        )
    
    def test_mutacao_modifica_populacao(self):
        original_values = [x.value for x in self.ga._population]
        self.ga._mutation()
        
        new_values = [x.value for x in self.ga._population]
        
        # Pelo menos alguns valores devem ter mudado
        assert original_values != new_values
    
    def test_mutacao_com_taxa_zero(self):
        ga_no_mutation = GeneticAlgorithm(
            population=self.population,
            threshold=9.0,
            max_generations=10,
            mutation_rate=0.0,  # 0% mutação
            crossover_rate=0.8
        )
        
        original_values = [x.value for x in ga_no_mutation._population]
        ga_no_mutation._mutation()
        
        new_values = [x.value for x in ga_no_mutation._population]
        
        # Valores não devem ter mudado
        assert original_values == new_values
    
    @patch('random.uniform')
    @patch('random.random')
    def test_probabilidade_mutacao(self, mock_random, mock_uniform):
        # Força random() a retornar valores que impedem mutação
        mock_random.return_value = 0.9
        mock_uniform.return_value = 0.0  # Não altera o valor quando mutate é chamado
        
        ga_low_mutation = GeneticAlgorithm(
            population=self.population,
            threshold=9.0,
            max_generations=10,
            mutation_rate=0.5,  # 50% mutação
            crossover_rate=0.8
        )
        
        original_values = [x.value for x in ga_low_mutation._population]
        ga_low_mutation._mutation()
        
        new_values = [x.value for x in ga_low_mutation._population]
        
        # Com random() = 0.9 e mutation_rate = 0.5, não deve mutar
        assert original_values == new_values


class TestGeneticAlgorithmRun:
    
    def setup_method(self):
        # Cria população com fitness variados
        self.population = [MockChromosome(i) for i in range(5)]
        self.ga = GeneticAlgorithm(
            population=self.population,
            threshold=10.0,  # Threshold alto para testar gerações
            max_generations=5,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
    
    @patch('builtins.print')  # Mock print para evitar output durante testes
    def test_executar_retorna_cromossomo(self, mock_print):
        result = self.ga.run()
        assert isinstance(result, MockChromosome)
    
    @patch('builtins.print')
    def test_executar_retorna_melhor_cromossomo(self, mock_print):
        result = self.ga.run()
        
        # Deve retornar um cromossomo com fitness alto
        assert isinstance(result, MockChromosome)
        assert result.fitness() >= 0
    
    @patch('builtins.print')
    def test_executar_terminacao_antecipada(self, mock_print):
        # Cria população com um cromossomo que já atinge o threshold
        high_fitness_population = [MockChromosome(15.0)] + [MockChromosome(i) for i in range(4)]
        
        ga_early = GeneticAlgorithm(
            population=high_fitness_population,
            threshold=10.0,  # Threshold menor que o melhor fitness
            max_generations=100,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        result = ga_early.run()
        
        # Deve retornar rapidamente com o melhor cromossomo
        assert result.fitness() >= 10.0
    
    @patch('builtins.print')
    def test_executar_cria_dataframe_resultados(self, mock_print):
        self.ga.run()
        
        # Deve ter criado o atributo results
        assert hasattr(self.ga, 'results')
        assert isinstance(self.ga.results, pd.DataFrame)
        
        # DataFrame deve ter as colunas esperadas
        expected_columns = ['gens', 'best_fitness', 'mean_fitness']
        for col in expected_columns:
            assert col in self.ga.results.columns
    
    @patch('builtins.print')
    def test_executar_com_zero_geracoes(self, mock_print):
        ga_zero_gen = GeneticAlgorithm(
            population=self.population,
            threshold=10.0,
            max_generations=0,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        result = ga_zero_gen.run()
        
        # Deve retornar o melhor da população inicial
        assert isinstance(result, MockChromosome)
    
    @patch('builtins.print')
    def test_executar_com_elitismo_desabilitado(self, mock_print):
        ga_no_elitism = GeneticAlgorithm(
            population=self.population,
            threshold=10.0,
            max_generations=3,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elitism=False
        )
        
        result = ga_no_elitism.run()
        assert isinstance(result, MockChromosome)


class TestShowResults:
    
    def setup_method(self):
        self.population = [MockChromosome(i) for i in range(3)]
        self.ga = GeneticAlgorithm(
            population=self.population,
            threshold=10.0,
            max_generations=2,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.figure')
    @patch('builtins.print')
    def test_mostrar_resultados_com_resultados(self, mock_print, mock_figure, mock_plot, mock_show):
        # Executa o algoritmo para gerar resultados
        self.ga.run()
        
        # Chama show_results
        result = self.ga.show_results()
        
        # Verifica se matplotlib foi chamado
        assert mock_figure.called
        mock_show.assert_called_once()
        
        # Deve retornar o DataFrame de resultados
        assert isinstance(result, pd.DataFrame)
    
    @patch('builtins.print')
    def test_mostrar_resultados_sem_resultados(self, mock_print):
        result = self.ga.show_results()
        
        # Deve imprimir mensagem de erro
        mock_print.assert_called_with("Nenhum resultado disponível. Execute o algoritmo primeiro.")
        
        # Deve retornar None
        assert result is None
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.figure')
    @patch('builtins.print')
    def test_mostrar_resultados_chamadas_plot(self, mock_print, mock_figure, mock_plot, mock_show):
        # Executa o algoritmo
        self.ga.run()
        
        # Chama show_results
        self.ga.show_results()
        
        # Verifica se plot foi chamado duas vezes (best e mean fitness)
        assert mock_plot.call_count == 2


class TestGeneticAlgorithmIntegration:
    
    @patch('builtins.print')
    def test_fluxo_completo_otimizacao(self, mock_print):
        # Cria população inicial
        population = [MockChromosome(i) for i in range(10)]
        
        # Configura algoritmo genético
        ga = GeneticAlgorithm(
            population=population,
            threshold=8.0,
            max_generations=10,
            mutation_rate=0.2,
            crossover_rate=0.7,
            elitism=True
        )
        
        # Executa otimização
        best = ga.run()
        
        # Verificações
        assert isinstance(best, MockChromosome)
        assert hasattr(ga, 'results')
        
        # O melhor deve ter fitness razoável
        assert best.fitness() >= 0
        
        # Results deve ter dados de todas as gerações
        assert len(ga.results) > 0
    
    @patch('builtins.print')
    def test_comportamento_convergencia(self, mock_print):
        # Cria população com fitness baixos
        population = [MockChromosome(0.1 * i) for i in range(5)]
        
        ga = GeneticAlgorithm(
            population=population,
            threshold=2.0,
            max_generations=20,
            mutation_rate=0.3,
            crossover_rate=0.9,
            elitism=True
        )
        
        best = ga.run()
        
        # Verifica se houve melhoria
        initial_best = max(population, key=lambda x: x.fitness()).fitness()
        final_best = best.fitness()
        
        # O algoritmo deve ter mantido ou melhorado o fitness
        assert final_best >= initial_best - 0.5  # Tolerância para mutação


class TestEdgeCases:
    
    def test_algoritmo_genetico_com_cromossomo_unico(self):
        single_population = [MockChromosome(5.0)]
        
        ga = GeneticAlgorithm(
            population=single_population,
            threshold=10.0,
            max_generations=3,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        with patch('builtins.print'):
            result = ga.run()
        
        assert isinstance(result, MockChromosome)
    
    def test_algoritmo_genetico_com_cromossomos_identicos(self):
        identical_population = [MockChromosome(3.0) for _ in range(5)]
        
        ga = GeneticAlgorithm(
            population=identical_population,
            threshold=10.0,
            max_generations=3,
            mutation_rate=0.5,  # Alta mutação para criar diversidade
            crossover_rate=0.8
        )
        
        with patch('builtins.print'):
            result = ga.run()
        
        assert isinstance(result, MockChromosome)
    
    def test_algoritmo_genetico_com_parametros_extremos(self):
        population = [MockChromosome(i) for i in range(3)]
        
        # Parâmetros extremos
        ga = GeneticAlgorithm(
            population=population,
            threshold=1000.0,  # Threshold muito alto
            max_generations=1,  # Apenas 1 geração
            mutation_rate=1.0,  # 100% mutação
            crossover_rate=0.0  # 0% crossover
        )
        
        with patch('builtins.print'):
            result = ga.run()
        
        assert isinstance(result, MockChromosome)
    
    @patch('builtins.print')
    def test_algoritmo_genetico_com_fitness_negativo(self, mock_print):
        negative_population = [MockChromosome(-i) for i in range(1, 6)]  # -1 a -5
        
        ga = GeneticAlgorithm(
            population=negative_population,
            threshold=-0.5,  # Threshold negativo
            max_generations=5,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        result = ga.run()
        
        # Deve retornar o menos negativo (melhor fitness)
        assert isinstance(result, MockChromosome)
        assert result.fitness() <= 0


if __name__ == '__main__':
    # Configuração para executar os testes
    pytest.main([__file__, "-v"])
