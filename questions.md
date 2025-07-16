# Perguntas relevantes - Algoritmo Genético para Otimização de Portfólio

## 1. O que você está otimizando? Qual é a variável que quer maximizar ou minimizar?

**Objetivo de Otimização:** Este projeto visa otimizar a composição de um portfólio de investimentos utilizando algoritmos genéticos para encontrar a alocação ótima de pesos entre os ativos selecionados.

**Variável a Maximizar:** A função de fitness que equilibra retorno esperado e controle de risco, conforme implementada em `portfolio.py:31-56`:

```
fitness = (1 - risk_free_rate) * retorno_médio_ponderado - risk_free_rate * CVaR
```

**Justificativa Acadêmica:** Esta formulação segue a abordagem da Teoria Moderna de Portfólio (Markowitz, 1952), mas incorpora medidas de risco mais robustas que a variância tradicional. A função balanceou duas métricas fundamentais:

1. **Retorno Esperado Ajustado:** `(1 - risk_free_rate) * mean_return.dot(weights)` - representa o excesso de retorno sobre a taxa livre de risco, ponderado pelos pesos do portfólio
2. **Penalização por Risco:** `risk_free_rate * CVaR` - penaliza o portfólio baseado na medida de risco de cauda (tail risk)

## 2. Qual é a representação da solução (genoma)?

**Estrutura do Genoma:** A solução é representada como um dicionário Python que mapeia cada ticker de ativo para seu respectivo peso no portfólio:

```python
genoma = {
    'PDGR3.SA': 0.4430,
    'CASH3.SA': 0.0365,
    'ONCO3.SA': 0.0207,
    # ... outros ativos
}
```

**Características do Genoma:**
- **Tipo:** Representação real (float) para cada peso
- **Restrições:** Pesos não-negativos (≥ 0)
- **Normalização:** Os pesos são automaticamente normalizados para somar 1.0 através da propriedade `weights` (`portfolio.py:19-29`)
- **Dimensionalidade:** Variável, dependente do número de ativos selecionados (20 ativos no caso atual)

**Justificativa da Escolha:** A representação em ponto flutuante permite exploração contínua do espaço de soluções, oferecendo maior granularidade que representações binárias. A normalização automática garante que a restrição fundamental de portfólio (soma dos pesos = 1) seja sempre mantida.

## 3. Qual é a função de fitness?

**Implementação:** Localizada em `portfolio.py:31-56`, a função de fitness combina retorno esperado com medida de risco CVaR:

```python
def fitness(self, alpha=0.95) -> float:
    weights_array = np.array(list(self.weights.values()))
    mean_return = self.returns.mean()
    portfolio_returns = self.returns.dot(weights_array)
    self.ExpReturn = portfolio_returns.mean()
    
    # VaR com 95% de confiança
    portfolio_var = np.percentile(portfolio_returns, (1-alpha)*100)
    
    # CVaR - média dos retornos abaixo do VaR
    self.cvar = portfolio_returns[portfolio_returns <= portfolio_var].mean()
    
    # Função de fitness final
    return (1 - self.risk_free_rate) * mean_return.dot(weights_array) - self.risk_free_rate * self.cvar
```

**Justificativa da Escolha do CVaR:**

O Conditional Value at Risk (CVaR) foi escolhido como medida de risco por várias razões acadêmicas e práticas fundamentais:

1. **Coerência de Risco:** CVaR é uma medida de risco coerente que satisfaz todas as propriedades axiomáticas de Artzner et al. (1999): monotonicidade, invariância translacional, homogeneidade positiva e subaditividade.

2. **Sensibilidade a Eventos Extremos:** Diferentemente da variância (usada por Markowitz), CVaR captura especificamente o risco de cauda (tail risk), sendo mais sensível a perdas extremas que podem devastar portfólios.

3. **Interpretabilidade Prática:** CVaR representa a perda média esperada nos piores cenários (percentil 5% no caso), oferecendo uma interpretação intuitiva para gestores de risco.

4. **Otimização Convexa:** CVaR é uma função convexa, facilitando a convergência de algoritmos de otimização e evitando mínimos locais problemáticos.

5. **Regulamentação Financeira:** CVaR é amplamente aceito por reguladores financeiros (Basel III) e é padrão na indústria para mensuração de risco de mercado.

6. **Robustez Estatística:** CVaR é menos sensível a outliers que medidas baseadas em momentos superiores, oferecendo maior estabilidade em dados financeiros ruidosos.

## 4. Qual é o método de seleção?

**Método Implementado:** Tournament Selection configurado em `main.py:86` e implementado em `geneticAlgorithm.py:45-48`.

**Algoritmo:**
```python
def _pick_tournament(self, competitors: int = 3) -> Tuple[C, C]:
    participants = choices(self._population, k=competitors)
    return tuple(sorted(participants, key=self._fitness_key, reverse=True)[:2])
```

**Parâmetros:**
- **Tamanho do Torneio:** 3 indivíduos
- **Pressão Seletiva:** Moderada
- **Retorno:** 2 melhores indivíduos do torneio

**Justificativa Acadêmica:**
1. **Controle de Pressão Seletiva:** Tournament selection permite controle fino da pressão seletiva através do tamanho do torneio, evitando convergência prematura
2. **Eficiência Computacional:** O(1) em complexidade, mais eficiente que métodos baseados em fitness proporcional
3. **Robustez:** Funciona bem independentemente da distribuição de fitness, sem necessidade de reescalonamento
4. **Diversidade:** Mantém diversidade populacional melhor que seleção elitista pura

## 5. Qual método de crossover você vai implementar?

**Método:** Single-Point Crossover implementado em `portfolio.py:58-83`.

**Algoritmo:**
```python
def crossover(self, other: T) -> Tuple[T, T]:
    w1 = self.weights
    w2 = other.weights
    mid = len(w1) // 2
    
    # Primeiro filho: primeira metade de w1 + segunda metade de w2
    new_w1 = {k: w1[k] for k in list(w1.keys())[:mid]}
    new_w1.update({k: w2[k] for k in list(w2.keys())[mid:]})
    
    # Segundo filho: primeira metade de w2 + segunda metade de w1
    new_w2 = {k: w2[k] for k in list(w2.keys())[:mid]}
    new_w2.update({k: w1[k] for k in list(w1.keys())[mid:]})
    
    return Portfolio(new_w1, ...), Portfolio(new_w2, ...)
```

**Características:**
- **Ponto de Corte:** Meio do vetor de pesos
- **Hereditariedade:** Cada filho herda características de ambos os pais
- **Preservação:** Mantém a estrutura do dicionário de pesos

**Justificativa:**
1. **Simplicidade e Eficiência:** Implementação direta e computacionalmente eficiente
2. **Exploração Balanceada:** Combina características dos pais de forma sistemática
3. **Compatibilidade:** Funciona bem com representação de ponto flutuante
4. **Building Block Hypothesis:** Preserva blocos de genes adjacentes que podem representar estratégias de alocação eficazes

## 6. Qual será o método de inicialização?

**Método:** Inicialização aleatória uniforme implementada em `Portfolio.random_instance()` (`portfolio.py:97-100`).

**Algoritmo:**
```python
@classmethod
def random_instance(cls, weights, returns, risk_free_rate=0.2):
    random_weights = {k: uniform(0, 1) for k in weights}
    return Portfolio(weights=random_weights, returns=returns, risk_free_rate=risk_free_rate)
```

**Processo:**
1. **Geração:** Cada peso recebe valor aleatório de distribuição uniforme U(0,1)
2. **Normalização:** Automática através da propriedade `weights`
3. **Diversidade:** Garante exploração inicial ampla do espaço de soluções

**Justificativa Acadêmica:**
1. **Diversidade Inicial:** Distribuição uniforme maximiza a diversidade inicial da população
2. **Ausência de Viés:** Não favorece nenhuma região específica do espaço de soluções
3. **Cobertura Espacial:** Garante representação adequada de diferentes estratégias de alocação
4. **Compatibilidade:** Funciona bem com operadores genéticos de ponto flutuante

## 7. Qual o critério de parada?

**Critérios Múltiplos:** O algoritmo implementa dois critérios de parada alternativos:

**Critério 1 - Threshold de Fitness:**
- **Valor:** 13.0 (configurado em `main.py:87`)
- **Lógica:** Para quando qualquer indivíduo atinge fitness ≥ 13.0

**Critério 2 - Máximo de Gerações:**
- **Valor:** 50 gerações (configurado em `main.py:13`)
- **Lógica:** Para quando atinge o limite máximo independentemente do fitness

**Implementação:** `geneticAlgorithm.py:88-114`
```python
for generation in range(self._max_generations):
    current_best_fitness = self._fitness_key(best)
    if current_best_fitness >= self._threshold:
        return best
    # ... resto do loop
```

**Justificativa dos Critérios:**
1. **Threshold de Fitness:** Permite parada antecipada quando solução satisfatória é encontrada, economizando recursos computacionais
2. **Limite de Gerações:** Garante término em tempo finito, evitando execução indefinida
3. **Flexibilidade:** Operador OR permite adaptação a diferentes cenários de otimização
4. **Monitoramento:** Logs de progresso permitem análise da convergência (`Generation: X, Best Fitness: Y`)

**Considerações Práticas:**
- **Threshold 13.0:** Baseado em análise empírica dos resultados esperados para o conjunto de dados
- **50 Gerações:** Balanceio entre tempo computacional e qualidade da solução
- **Possível Extensão:** Critérios adicionais como estagnação de fitness ou diversidade mínima podem ser incorporados