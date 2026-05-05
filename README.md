## Membros

* Luiz Fernando Gonçalves Rocha
* Lucas Almeida Amaral
* Thales Augusto Rocha Fernandes

## Explicação do Sistema

O sistema consiste em um simulador de carrinho de compras de um marketplace com descontos dinâmicos. Ele será composto por uma funcionalidade de cadastro de itens, cada um com seu valor e uma série de propriedades (como categoria, vendedor, margem de lucro, marca), além de uma funcionalidade de cadastro de cupons, cada um com uma regra de aplicação e desconto (em porcentagem ou valor) sobre o valor da compra ou associado a um item específico do carrinho.

Esse tipo de sistema permite evidenciar a importância dos testes de software à medida que ele está constantemente sujeito a mudanças nas regras de negócio (mudança na lógica de aplicação dos cupons, alterações na porcentagem de desconto, etc.). Nesse sentido, a utilização de testes de regressão tem um papel fundamental para evitar a introdução de bugs nas funcionalidades que já existiam e reforçar os requisitos da implementação em cada alteração feita.

Para evidenciar a importância dos testes, serão implementados fluxos de CI/CD no Github Actions e serão simuladas refatorações e mudanças de regras de negócio, além de mudanças na interface do usuário.

## Explicação das Possíveis Tecnologias Utilizadas

* **Python:** Linguagem principal da aplicação
* **Github Actions:** Para implementar fluxos de CI/CD
* **Pytest:** Para implementação de testes
* **SQLite:** Banco de dados simples para a aplicação
* **mutmut:** Para testes de mutação
* **Hypothesis:** Para testes usando entradas aleatórias de domínios de valores
