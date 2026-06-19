# Couponify

Simulador de carrinho de compras de um marketplace com **descontos dinâmicos**,
construído para evidenciar como os testes de software sustentam a manutenção do
sistema diante de mudanças constantes nas regras de negócio.

## Membros

* Luiz Fernando Gonçalves Rocha
* Lucas Almeida Amaral
* Thales Augusto Rocha Fernandes

## Explicação do Sistema

O sistema simula o carrinho de compras de um marketplace. Ele é composto por:

* **Cadastro de itens:** cada item possui um valor e propriedades como
  categoria, vendedor, margem de lucro e marca.
* **Cadastro de cupons:** cada cupom possui uma regra de aplicação e um desconto
  (em porcentagem ou valor) que incide sobre o valor total da compra ou sobre um
  conjunto específico de itens do carrinho.

Esse tipo de sistema é ideal para evidenciar a importância dos testes, pois está
constantemente sujeito a mudanças (lógica de aplicação dos cupons, porcentagens
de desconto, limites etc.). Os **testes de regressão** evitam a introdução de
bugs em funcionalidades existentes a cada alteração.

### Conceitos principais

* **Item / CartItem:** um produto e sua quantidade no carrinho.
* **Cupom (`Coupon`):** tipo de desconto (`percentage`/`fixed`), valor, escopo
  (carrinho inteiro ou itens de uma categoria), regras de elegibilidade e um
  limite máximo de desconto opcional (`max_discount`).
* **Regras (`rules`):** condições que liberam o cupom (compra mínima, presença de
  categoria/marca/vendedor). Todas precisam ser satisfeitas (E lógico).
* **Motor de desconto (`discounts`):** função pura que calcula o desconto de um
  cupom sobre um carrinho. O total nunca fica negativo e o desconto nunca excede
  o subtotal.

## Tecnologias Utilizadas

| Tecnologia        | Uso                                              |
|-------------------|--------------------------------------------------|
| **Python 3.12**   | Linguagem principal (apenas biblioteca padrão)   |
| **SQLite**        | Persistência local de itens, cupons e carrinho   |
| **Pytest**        | Testes de unidade, integração e e2e              |
| **Coverage.py**   | Medição de cobertura de testes                   |
| **Hypothesis**    | Testes baseados em propriedades                  |
| **mutmut**        | Testes de mutação                                |
| **GitHub Actions**| Integração contínua (Linux, macOS e Windows)     |

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

## Uso da CLI

A aplicação é controlada por linha de comando. Use `--db` para escolher o banco
(o padrão é `couponify.db` no diretório atual).

```bash
# Cadastrar itens
python -m couponify add-item --name "Notebook" --price 3500 --category tech --seller techstore --brand dell
python -m couponify add-item --name "Mouse" --price 120 --category tech --seller techstore

# Cadastrar um cupom de 10% para compras acima de 1000
python -m couponify add-coupon --code TECH10 --type percentage --value 10 --min-purchase 1000

# Montar o carrinho e aplicar o cupom
python -m couponify add-to-cart --item-id 1
python -m couponify add-to-cart --item-id 2 --quantity 2
python -m couponify apply-coupon --code TECH10

# Ver subtotal, desconto e total
python -m couponify checkout
```

Após instalar o pacote, o comando `couponify` também fica disponível diretamente.

## Como Rodar os Testes

```bash
# Suíte completa
pytest

# Com relatório de cobertura (falha se ficar abaixo de 80%)
pytest --cov=couponify --cov-report=term-missing --cov-fail-under=80
```

## Estrutura do Projeto

```
couponify/        # código da aplicação (em inglês)
  money.py        # valores monetários com Decimal
  models.py       # Item, CartItem, Coupon
  rules.py        # regras de elegibilidade dos cupons
  discounts.py    # motor de cálculo de desconto
  cart.py         # agregado do carrinho
  database.py     # conexão e schema SQLite
  repository.py   # persistência de itens e cupons
  service.py      # serviço de aplicação (fachada da CLI)
  cli.py          # interface de linha de comando
tests/
  unit/           # testes de unidade e de propriedade
  integration/    # testes de integração / e2e da CLI
.github/workflows/ci.yml
```

## Integração Contínua (CI/CD)

A cada `push` ou `pull request`, o **GitHub Actions** executa toda a suíte de
testes em **Linux, macOS e Windows** e mede a cobertura. O relatório de cobertura
é enviado ao **Codecov**.
