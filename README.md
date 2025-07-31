# Otimização de Portfólio com Algoritmo Genético

![Tests](https://github.com/robsoncalixto/wallet_optimization_ag/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12.2-brightgreen)
![pytest](https://img.shields.io/badge/pytest-8.4.1-blue)
![Coverage](https://codecov.io/gh/robsoncalixto/wallet_optimization_ag/branch/master/graph/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

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
- ⚙️ Visualização dos parâmetros do algoritmo genético
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

### Como Executar os Testes

```bash
# Executar todos os testes na raiz do projeto
pytest test/ -v
```

#### Executar Testes de Arquivos Específicos
```bash
# Testes do Portfolio
pytest test/test_portfolio.py -v

# Testes do Algoritmo Genético
pytest test/test_genetic_algorithm.py -v

# Testes do Coletor de Dados
pytest test/test_data_collector.py -v
```

## Equipe

Este projeto foi desenvolvido pelo **Grupo 89** como parte do Tech Challenge FIAP Pós-Tech fase 2:

- **Araguacy Bezerra Pereira**   - araguacybp@yahoo.com.br
- **Robson Carvalho Calixto**    - robsoncaliixto@gmail.com
- **Vinicius Fernando M. Costa** - mcostavini98@gmail.com   

## Licença

Este projeto está licenciado sob os termos especificados no arquivo LICENSE.
