# Otimização de Portfólio com Algoritmo Genético

![Tests](https://github.com/robsoncalixto/wallet_optimization_ag/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12.2-brightgreen)
![Status](https://img.shields.io/badge/Status-Concluído-success)

## Descrição

Este projeto implementa um sistema de otimização de portfólio de investimentos utilizando **Algoritmos Genéticos (AG)** para encontrar a alocação ideal de capital entre diferentes ativos da Bolsa de Valores Brasileira (B3). O objetivo é maximizar o retorno ajustado ao risco, considerando métricas de risco como o **Conditional Value at Risk (CVaR)**.

A aplicação foi desenvolvida como parte do **Tech Challenge da FIAP - Módulo 2** pelo **Grupo 89**, demonstrando a aplicação prática de metaheurísticas evolutivas em problemas de otimização, especificamente na construção de portfólios eficientes que equilibrem retorno e risco.

## Índice

1. [Descrição](#descrição)
2. [Documentação Complementar](#documentação-complementar)
3. [Arquitetura do Projeto](#arquitetura-do-projeto)
4. [Pré-requisitos](#pré-requisitos)
5. [Como Executar](#como-executar)
6. [Dados e Fonte](#dados-e-fonte)
7. [Testes](#testes)
8. [Equipe](#equipe)
9. [Licença](#licença)

## Documentação Complementar

O diretório `/doc` contém documentação técnica detalhada:

- [**Otimização de Carteira de Investimentos Utilizando Algoritmo Genético.pdf**](./doc/Otimização%20de%20Carteira%20de%20Investimentos%20Utilizando%20Algoritmo%20Genético.pdf) : Relatório produzido durante o desenvolvimento da solução, além de ser uma documentação técnica
- [**Tech Challenge - 5IADT - Fase 2.pdf**](./doc/Tech%20Challenge%20-%205IADT%20-%20Fase%202.pdf) : Especificação oficial do desafio técnico da FIAP

## Arquitetura do Projeto

### Componentes Principais

- **`genetic_algorithm.py`**: Implementação genérica do Algoritmo Genético com suporte a diferentes métodos de seleção, crossover e mutação
- **`chromosome.py`**: Classe abstrata que define a interface para representação de cromossomos
- **`portfolio.py`**: Implementação específica de um cromossomo representando um portfólio de investimentos
- **`data_collector.py`**: Módulo otimizado para coleta e processamento de dados históricos com sistema de cache inteligente
- **`app.py`**: Interface web interativa com otimizações de performance e conformidade técnica

### Fluxo de Execução

1. **Coleta de Dados**: Obtenção de dados históricos das ações brasileiras através da API do Yahoo Finance
2. **Seleção de Ativos**: Filtragem das melhores ações baseada em critérios de retorno médio
3. **Inicialização**: Criação de população inicial com distribuição aleatória de pesos
4. **Evolução**: Aplicação iterativa dos operadores genéticos (seleção, crossover, mutação)
5. **Avaliação**: Cálculo da função de fitness considerando retorno e risco (CVaR)
6. **Convergência**: Execução até atingir critério de parada (número máximo de gerações ou fitness alvo)

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter os seguintes requisitos instalados:

- **Python 3.7 ou superior**: Linguagem de programação principal
- **pip**: Gerenciador de pacotes do Python
- **Ambiente virtual**: Recomendado para isolamento de dependências
- **Git**: Para clonagem do repositório (opcional)
- **Conexão com a internet**: Necessária para coleta de dados financeiros via Yahoo Finance

## Como Executar

### 1. Clonagem do Repositório (se aplicável)

```bash
git clone <url-do-repositorio>
cd wallet-optimization_ag
```

### 2. Criação do Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv env

# Ativar ambiente virtual
# Windows:
env\Scripts\activate.bat

# WSL/Linux:
source env/Scripts/activate
```

### 3. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 4. Execução da Aplicação

#### Interface Web (Recomendado)

```bash
streamlit run app.py
```

A interface web oferece:
- 📊 Seleção interativa de ações da B3
- ⚙️ Configuração de parâmetros do algoritmo genético
- 📉 Gráficos de convergência e composição do portfólio
- 📊 Comparação com benchmarks (Bovespa)

### Exemplo de Configuração no Windows

```bash
# Ativar ambiente virtual
env\Scripts\activate.bat

# Executar aplicação
streamlit run app.py
```

## Dados e Fonte

### Dataset
- **Fonte**: Arquivo `data/empresas_br_bovespa.csv`
- **Conteúdo**: Lista de empresas brasileiras listadas na B3
- **Campos**: Ticker, nome da empresa, setor

### Coleta de Dados Históricos
- **API**: Yahoo Finance (biblioteca yfinance)
- **Período**: Configurável (padrão: últimos 2 anos)
- **Frequência**: Diária
- **Processamento**: Cálculo automático de retornos percentuais

## Testes

O projeto inclui uma suíte abrangente de **121 testes unitários** para validar todos os módulos principais. Todos os testes estão passando e são executados automaticamente no CI/CD.

### Estrutura dos Testes

- **`test/test_chromosome.py`**: Testes para a classe abstrata Chromosome (15 testes)
- **`test/test_data_collector.py`**: Testes para coleta e processamento de dados (21 testes)
- **`test/test_portfolio.py`**: Testes para funcionalidade de portfólio (46 testes)  
- **`test/test_genetic_algorithm.py`**: Testes para o algoritmo genético (39 testes)

### Como Executar os Testes

#### Executar Todos os Testes (Recomendado)
```bash
# Da raiz do projeto
python -m unittest discover test -v
```

#### Executar Testes de um Módulo Específico
```bash
# Testes do módulo Portfolio
python -m unittest test.test_portfolio -v

# Testes do Algoritmo Genético
python -m unittest test.test_genetic_algorithm -v

# Testes do Coletor de Dados
python -m unittest test.test_data_collector -v

# Testes do Chromosome
python -m unittest test.test_chromosome -v
```

#### Executar Teste Individual
```bash
# Executar uma classe de teste específica
python -m unittest test.test_portfolio.TestPortfolioFitness -v

# Executar um método de teste específico
python -m unittest test.test_portfolio.TestPortfolioFitness.test_fitness_returns_float -v
```

#### Saída Silenciosa (Apenas Resultados)
```bash
python -m unittest discover test
```

### Cobertura dos Testes

Os testes cobrem:
- ✅ **Funcionalidades básicas** de todos os módulos
- ✅ **Casos extremos** (edge cases) e validação de parâmetros
- ✅ **Testes de integração** entre componentes
- ✅ **Comportamento com dados mockados** para isolar dependências
- ✅ **Tratamento de erros** e validação de tipos
- ✅ **Operações matemáticas** (fitness, crossover, mutação)
- ✅ **Manipulação de dados** financeiros

### Integração Contínua

Os testes são executados automaticamente no **GitHub Actions** em múltiplas versões do Python:
- Python 3.10
- Python 3.11  
- Python 3.12.2

O status dos testes pode ser verificado pelo badge no topo deste README.

## Equipe

Este projeto foi desenvolvido pelo **Grupo 89** como parte do Tech Challenge FIAP Pós-Tech fase 2:

- **Araguacy Bezerra Pereira**   - araguacybp@yahoo.com.br
- **Robson Carvalho Calixto**    - robsoncaliixto@gmail.com
- **Vinicius Fernando M. Costa** - mcostavini98@gmail.com   

## Licença

Este projeto está licenciado sob os termos especificados no arquivo LICENSE.
