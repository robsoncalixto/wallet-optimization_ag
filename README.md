# Otimização de Portfólio com Algoritmo Genético

> Tech Challenge - Fase 2 - Grupo 89
**Autores:**  Grupo 89
- **Araguacy Pereira** - araguacybp@yahoo.com.br
- **Robson Calixto** - robsoncaliixto@gmail.com
- **Vinícius Costa** - mcostavini98@gmail.com

## Descrição

Este projeto implementa um sistema de otimização de portfólio de investimentos utilizando **Algoritmos Genéticos (AG)** para encontrar a alocação ideal de capital entre diferentes ativos da Bolsa de Valores Brasileira (B3). O objetivo é maximizar o retorno ajustado ao risco, considerando métricas de risco como o **Conditional Value at Risk (CVaR)**.

A aplicação foi desenvolvida como parte do **Tech Challenge da FIAP - Módulo 2** pelo **Grupo 89**, demonstrando a aplicação prática de metaheurísticas evolutivas em problemas de otimização financeira, especificamente na construção de portfólios eficientes que equilibrem retorno e risco.

## Índice

1. [Descrição](#descrição)
2. [Documentação Complementar](#documentação-complementar)
3. [Arquitetura do Projeto](#arquitetura-do-projeto)
4. [Pré-requisitos](#pré-requisitos)
5. [Como Executar](#como-executar)
6. [Dados e Fonte](#dados-e-fonte)
7. [Parâmetros de Configuração](#parâmetros-de-configuração)
8. [Resultados e Análise](#resultados-e-análise)
9. [Licença](#licença)

## Documentação Complementar

O diretório `/doc` contém documentação técnica detalhada:

- **`Otimização de Carteira de Investimentos Utilizando Algoritmo Genético.pdf`**: Relatório produzido durante o desenvolvimento da solução, além de ser uma documentação técnica
- **`Tech Challenge - 5IADT - Fase 2.pdf`**: Especificação oficial do desafio técnico da FIAP

## Arquitetura do Projeto

### Componentes Principais

- **`geneticAlgorithm.py`**: Implementação genérica do Algoritmo Genético com suporte a diferentes métodos de seleção, crossover e mutação
- **`chromossome.py`**: Classe abstrata que define a interface para representação de cromossomos
- **`portfolio.py`**: Implementação específica de um cromossomo representando um portfólio de investimentos
- **`dados.py`**: Módulo otimizado para coleta e processamento de dados históricos com sistema de cache inteligente
- **`app.py`**: Interface web interativa com otimizações de performance e conformidade técnica

### Otimizações Técnicas Implementadas

- **Sistema de Cache**: Implementação de `@st.cache_data` para operações custosas de I/O
- **Arquitetura de Cache Distribuído**: Função `_baixar_dados_cached()` para otimização do yfinance
- **Tratamento Robusto de Exceções**: Mensagens específicas e tipificadas para diferentes cenários de erro
- **Documentação Padronizada**: Docstrings completas seguindo convenções Python
- **Validação de Dados**: Verificação robusta de arquivos CSV e parâmetros de entrada
- **Gerenciamento de Memória**: Fechamento adequado de figuras matplotlib

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

### Verificação dos Pré-requisitos

```bash
# Verificar versão do Python
python --version

# Verificar se pip está instalado
pip --version
```

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

**Bibliotecas utilizadas:**
- `pandas`: Manipulação e análise de dados financeiros com validação robusta
- `numpy`: Computação numérica e operações matriciais otimizadas
- `yfinance`: Coleta de dados financeiros com sistema de cache inteligente
- `matplotlib`: Visualização de gráficos com gerenciamento adequado de memória
- `streamlit`: Interface web interativa com cache de operações custosas

### 4. Execução da Aplicação

#### Interface Web (Recomendado)

```bash
streamlit run app.py
```

A interface web oferece:
- 📊 Seleção interativa de ações da B3
- ⚙️ Configuração de parâmetros do algoritmo genético
- 📈 Visualização em tempo real da evolução
- 📊 Análise detalhada dos resultados
- 📉 Gráficos de convergência e composição do portfólio
- 📊 Comparação com benchmarks (Bovespa e carteira aleatória)

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

## Resultados e Análise

### Visualizações

- **Gráfico de Convergência**: Evolução do fitness ao longo das gerações
- **Composição do Portfólio**: Distribuição visual dos pesos dos ativos
- **Comparação**: Fitness médio vs. melhor fitness por geração

## Licença

Este projeto está licenciado sob os termos especificados no arquivo LICENSE.
