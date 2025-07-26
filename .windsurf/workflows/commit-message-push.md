---
description: Criar mensagem de commit a partir das alterações realizadas no repositório, seguindo um conjunto de regras avançadas com MCP
---

# Workflow: Commit Message Push

Workflow automatizado para criação de mensagens de commit padronizadas usando MCP (Model Context Protocol).

## Execução:

### 1. **Análise das Alterações**
- Verificar branch atual: `git status`
- Analisar mudanças: `git diff HEAD`
- Identificar escopo e impacto das alterações

### 2. **Padrão de Mensagem**
```
<tipo>(<escopo>): <descrição>

[corpo opcional]
```

### 3. **Tipos Permitidos**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção
- `perf`: Performance
- `data`: Dados/datasets
- `analysis`: Análises acadêmicas

### 4. **Escopos do Projeto**
- `genetic-algorithm`: Algoritmo genético
- `portfolio`: Lógica de portfólio
- `interface`: Interface Streamlit
- `visualization`: Gráficos
- `docs`: Documentação
- `config`: Configurações

### 5. **Execução Git**

// turbo
```bash
git add -A
```

// turbo
```bash
git commit -m "<mensagem_gerada>"
```

// turbo
```bash
git push
```

### 6. **Exemplos**

```
feat(genetic-algorithm): implementa seleção por torneio

- Adiciona método de seleção adaptativo
- Melhora convergência em 15%
- Adiciona parâmetros configuráveis
```

```
fix(portfolio): corrige normalização de pesos

- Resolve divisão por zero
- Adiciona validação de entrada
```

**IMPORTANTE:** O MCP analisa automaticamente as alterações e gera mensagens contextuais para o projeto acadêmico de algoritmos genéticos.
