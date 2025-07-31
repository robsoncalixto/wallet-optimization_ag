"""
Script para executar todos os testes do projeto wallet_optimization_ag.

Este script executa todos os testes unitários criados para validar o comportamento
dos módulos do sistema de otimização de carteiras usando algoritmos genéticos.

Uso:
    python run_all_tests.py [--verbose] [--module MODULE_NAME]

Argumentos:
    --verbose: Executa os testes com saída detalhada
    --module: Executa apenas os testes de um módulo específico
              Opções: chromosome, data_collector, portfolio, genetic_algorithm
"""

import unittest
import sys
import os
import argparse
from io import StringIO

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa todos os módulos de teste
from test_chromosome import TestChromosome, TestChromosomeEdgeCases
from test_data_collector import (
    TestUtilityFunctions, TestDataCollectorInitialization, 
    TestDataCollectorDownload, TestDownloadDataCached,
    TestDataCollectorIntegration, TestEdgeCases as TestDataCollectorEdgeCases
)
from test_portfolio import (
    TestPortfolioInitialization, TestPortfolioWeightsProperty,
    TestPortfolioFitness, TestPortfolioCrossover, TestPortfolioMutate,
    TestPortfolioRandomInstance, TestPortfolioRepr,
    TestPortfolioEdgeCases
)
from test_genetic_algorithm import (
    TestGeneticAlgorithmInitialization, TestSelectionType,
    TestTournamentSelection, TestReduceReplace, TestElitism,
    TestMutation, TestGeneticAlgorithmRun, TestShowResults,
    TestGeneticAlgorithmIntegration, TestEdgeCases as TestGeneticAlgorithmEdgeCases
)


class TestResult:
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.failures = []
        self.errors = []
    
    def add_result(self, result):
        self.total_tests += result.testsRun
        self.failed_tests += len(result.failures)
        self.error_tests += len(result.errors)
        self.skipped_tests += len(result.skipped)
        self.passed_tests = self.total_tests - self.failed_tests - self.error_tests - self.skipped_tests
        
        self.failures.extend(result.failures)
        self.errors.extend(result.errors)
    
    def print_summary(self):
        print("\n" + "="*80)
        print("RESUMO DOS TESTES")
        print("="*80)
        print(f"Total de testes executados: {self.total_tests}")
        print(f"Testes aprovados: {self.passed_tests}")
        print(f"Testes falharam: {self.failed_tests}")
        print(f"Testes com erro: {self.error_tests}")
        print(f"Testes ignorados: {self.skipped_tests}")
        
        if self.failed_tests == 0 and self.error_tests == 0:
            print("\n[OK] TODOS OS TESTES PASSARAM!")
        else:
            print(f"\n[FALHA] {self.failed_tests + self.error_tests} TESTES FALHARAM")
            
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        print("="*80)


def create_test_suite(module_name=None):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if module_name is None or module_name == 'chromosome':
        # Testes do módulo chromosome
        suite.addTest(loader.loadTestsFromTestCase(TestChromosome))
        suite.addTest(loader.loadTestsFromTestCase(TestChromosomeEdgeCases))
        
    if module_name is None or module_name == 'data_collector':
        # Testes do módulo data_collector
        suite.addTest(loader.loadTestsFromTestCase(TestUtilityFunctions))
        suite.addTest(loader.loadTestsFromTestCase(TestDataCollectorInitialization))
        suite.addTest(loader.loadTestsFromTestCase(TestDataCollectorDownload))
        suite.addTest(loader.loadTestsFromTestCase(TestDownloadDataCached))
        suite.addTest(loader.loadTestsFromTestCase(TestDataCollectorIntegration))
        suite.addTest(loader.loadTestsFromTestCase(TestDataCollectorEdgeCases))
        
    if module_name is None or module_name == 'portfolio':
        # Testes do módulo portfolio
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioInitialization))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioWeightsProperty))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioFitness))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioCrossover))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioMutate))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioRandomInstance))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioRepr))
        suite.addTest(loader.loadTestsFromTestCase(TestPortfolioEdgeCases))
        
    if module_name is None or module_name == 'genetic_algorithm':
        # Testes do módulo genetic_algorithm
        suite.addTest(loader.loadTestsFromTestCase(TestGeneticAlgorithmInitialization))
        suite.addTest(loader.loadTestsFromTestCase(TestSelectionType))
        suite.addTest(loader.loadTestsFromTestCase(TestTournamentSelection))
        suite.addTest(loader.loadTestsFromTestCase(TestReduceReplace))
        suite.addTest(loader.loadTestsFromTestCase(TestElitism))
        suite.addTest(loader.loadTestsFromTestCase(TestMutation))
        suite.addTest(loader.loadTestsFromTestCase(TestGeneticAlgorithmRun))
        suite.addTest(loader.loadTestsFromTestCase(TestShowResults))
        suite.addTest(loader.loadTestsFromTestCase(TestGeneticAlgorithmIntegration))
        suite.addTest(loader.loadTestsFromTestCase(TestGeneticAlgorithmEdgeCases))
    
    return suite


def run_tests_for_module(module_name, verbose=False):
    print(f"\n{'='*60}")
    print(f"EXECUTANDO TESTES PARA: {module_name.upper()}")
    print(f"{'='*60}")
    
    suite = create_test_suite(module_name)
    
    if verbose:
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    else:
        # Captura saída para mostrar apenas resumo
        stream = StringIO()
        runner = unittest.TextTestRunner(verbosity=1, stream=stream)
    
    result = runner.run(suite)
    
    if not verbose:
        # Mostra apenas falhas e erros
        if result.failures:
            print("\nFALHAS:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nERROS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Executa testes do projeto wallet_optimization_ag',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
    python run_all_tests.py                    # Executa todos os testes
    python run_all_tests.py --verbose          # Executa com saída detalhada
    python run_all_tests.py --module portfolio # Executa apenas testes do portfolio
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Executa testes com saída detalhada'
    )
    
    parser.add_argument(
        '--module', '-m',
        choices=['chromosome', 'data_collector', 'portfolio', 'genetic_algorithm'],
        help='Executa testes apenas para o módulo especificado'
    )
    
    args = parser.parse_args()
    
    print("SISTEMA DE TESTES - WALLET OPTIMIZATION AG")
    print("="*80)
    
    test_result = TestResult()
    
    if args.module:
        # Executa testes para módulo específico
        result = run_tests_for_module(args.module, args.verbose)
        test_result.add_result(result)
    else:
        # Executa todos os testes
        modules = ['chromosome', 'data_collector', 'portfolio', 'genetic_algorithm']
        
        for module in modules:
            result = run_tests_for_module(module, args.verbose)
            test_result.add_result(result)
    
    # Mostra resumo final
    test_result.print_summary()
    
    # Retorna código de saída apropriado
    if test_result.failed_tests > 0 or test_result.error_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
