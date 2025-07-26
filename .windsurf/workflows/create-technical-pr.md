---
description: Criar Pull Request técnico com análise detalhada das alterações
---

# Workflow: Create Technical Pull Request

// turbo-all

Workflow automatizado para criação de Pull Requests técnicos com análise detalhada das alterações implementadas.

## Execução:

### 1. **Análise do Repositório**
- Verificar repositório remoto: `git remote -v`
- Identificar branch atual: `git branch --show-current`
- Listar branches disponíveis: `git branch -a`

### 2. **Análise das Alterações**
- Verificar status: `git status`
- Analisar diferenças: `git diff --stat`
- Listar arquivos modificados: `git diff --name-only`
- Obter commits do branch: `git log --oneline HEAD ^master`

### 3. **Estrutura do PR Técnico**

```
# <tipo>: <descrição técnica concisa>

## Objetivo

Descrição clara do problema técnico resolvido e justificativa das alterações implementadas.

## Descrição

Detalhamento técnico das modificações realizadas:

- **Componente 1:** Descrição específica da alteração
- **Componente 2:** Impacto técnico e implementação
- **Componente 3:** Melhorias de arquitetura aplicadas

## Arquivos Modificados

### `arquivo1.py`
- Alteração específica 1
- Alteração específica 2

### `arquivo2.py`
- Modificação técnica 1
- Implementação de padrão 2

## Impacto Técnico

- Performance: Descrição de melhorias
- Manutenibilidade: Aspectos de código limpo
- Arquitetura: Padrões implementados

## Testes e Validação

- Cenários testados
- Validações realizadas
- Casos de uso verificados
```

### 4. **Tipos de PR Técnico**
- `feat`: Nova funcionalidade implementada
- `fix`: Correção de bug ou problema
- `refactor`: Refatoração de código
- `perf`: Otimização de performance
- `docs`: Atualização de documentação
- `test`: Implementação de testes
- `chore`: Manutenção e configuração

### 5. **Criação do Pull Request**

Após análise das alterações, o sistema criará automaticamente um PR técnico seguindo o padrão estabelecido, incluindo:

- Título técnico conciso
- Análise detalhada das modificações
- Impacto nos componentes do sistema
- Justificativas técnicas das decisões
- Validações realizadas

### 6. **Exemplo de Uso**

```
fix: Implementa cache e otimizações de performance no sistema de dados

## Objetivo

Resolver problemas de performance relacionados ao carregamento repetitivo de dados e implementar padrões de cache para otimizar operações custosas do sistema.

## Descrição

Para melhorar a performance do sistema, as seguintes alterações técnicas foram implementadas:

- **Sistema de Cache:** Implementação de decorador @st.cache_data para operações de I/O custosas
- **Tratamento de Exceções:** Refatoração do sistema de tratamento de erros com mensagens específicas
- **Documentação Técnica:** Padronização de docstrings seguindo convenções Python
```

**IMPORTANTE:** Este workflow gera PRs técnicos focados em aspectos de implementação, arquitetura e impacto no sistema, sem uso de emojis ou linguagem informal.
