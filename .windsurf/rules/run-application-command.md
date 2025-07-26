---
trigger: model_decision
description: Verificação do Ambiente Virtual
---

Você é um agente responsável por auxiliar no desenvolvimento de um projeto Python. Toda vez que for executar qualquer comando Python ou relacionado ao projeto (ex: `python`, `streamlit`, `pip`, etc.), **você deve obrigatoriamente verificar se o terminal está com o ambiente virtual do projeto ativado**.

### Regras obrigatórias:

- Antes de qualquer comando, verifique se o ambiente virtual está ativado:
  - No prompt do terminal deve aparecer algo como `(.env)` ou o nome do ambiente entre parênteses.
  - Se não estiver ativado, execute o comando adequado para ativá-lo:
    - Linux/macOS:
      ```bash
      source .env/bin/activate
      ```
    - Windows:
      ```bash
      .env\Scripts\activate
      ```
- **Nunca execute comandos Python fora do ambiente virtual**, mesmo que o sistema permita.
- Caso o ambiente ainda não exista, crie com:
  ```bash
  python -m venv .env
  ```