# SIFSM — Sistema Integrado de Futuro Sustentável em Marte

## Projeto Aurora Siger

O SIFSM é um sistema acadêmico desenvolvido em Python
para simular o gerenciamento inteligente de uma colônia
humana em Marte.

O projeto integra banco de dados, estruturas de dados,
lógica booleana, modelagem matemática, regressão linear,
simulação energética e agentes inteligentes.

## Objetivos

O sistema busca representar computacionalmente a
infraestrutura da Aurora Siger, permitindo:

- Gerenciar módulos da colônia;
- Armazenar informações em banco de dados;
- Consultar sensores simulados;
- Automatizar decisões operacionais;
- Organizar solicitações em filas;
- Priorizar alertas;
- Explorar conexões entre módulos;
- Simular geração e consumo energético;
- Estimar consumo futuro;
- Gerar recomendações de agentes especializados.

## Tecnologias

- Python 3
- SQLite
- SQL
- CSV

O projeto utiliza apenas bibliotecas padrão do Python.

## Gráficos e diagramas

Os gráficos e diagramas escritos em Mermaid, como o arquivo
`graficos/arquitetura_sistema.mmd`, podem ser renderizados
no [Mermaid Live Editor](https://mermaid.live/). Basta copiar o conteúdo
do arquivo e colá-lo no editor.

## Estruturas de dados

### Listas

Utilizadas para armazenar registros e resultados.

### Dicionários

Utilizados para representar a rede da colônia.

### Filas

Implementadas com deque para organizar solicitações
na ordem de chegada.

### Heap

Utilizado para priorizar alertas operacionais.

### Grafos

Utilizados para representar conexões entre módulos.

### BFS

Utilizada para encontrar caminhos com o menor número
de conexões entre módulos.

## Banco de dados

O banco SQLite possui três tabelas:

1. modulos
2. leituras_sensores
3. alertas

O sistema implementa operações CRUD:

- CREATE
- READ
- UPDATE
- DELETE

## Modelagem matemática

O saldo de potência é:

**P_saldo(t) = P_gerada(t) - P_consumida(t)**

A variação energética é:

**Delta_E = integral(P_saldo(t) dt)**

A integração numérica utiliza a regra dos trapézios.

A bateria possui capacidade simulada de 800 kWh,
reserva inicial de 400 kWh e eficiência de carga de 95%.

## Regressão linear

O modelo utilizado é:

**C(t) = a + bt**

O sistema ajusta a regressão a partir dos primeiros
registros e avalia o resultado nos dois últimos.

São calculadas as métricas:

- MAE
- MSE
- RMSE

## Agentes inteligentes

O sistema possui três agentes simulados:

### Agente de Energia

Analisa geração e consumo.

### Agente Ambiental

Analisa umidade e disponibilidade de água.

### Agente de Manutenção

Consulta alertas operacionais.

Um coordenador executa os agentes e apresenta
suas recomendações.

Não existe integração com API externa de IA.

## Regras booleanas

A irrigação depende das seguintes condições:

**I = A AND U AND R AND S**

Onde:

A = módulo ativo
U = umidade baixa
R = água disponível
S = sensores válidos

## Instalação

É necessário possuir Python 3 instalado.

Não são necessárias bibliotecas externas.

## Como executar

Mantenha os arquivos na mesma pasta.

Execute o sistema principal:

```bash
python codigo_fonte.py
```

Ou execute a simulação:

```bash
python simulacao_computacional.py
```

Na primeira execução, o sistema cria automaticamente
o arquivo aurora_siger.db.

## Exemplo de entrada e saída

Ao executar a opção de decisões automáticas,
o sistema utiliza os dados do último ciclo.

Entrada:

```text
Geração = 270 kW
Consumo = 325 kW
Umidade = 35%
Água = 55%
Sensores válidos = Sim
```

Saída:

```text
IRRIGAÇÃO AUTORIZADA NA SIMULAÇÃO.
ALERTA: consumo maior que geração.
```

## Sustentabilidade

O projeto considera:

- Eficiência energética;
- Uso sustentável da água;
- Redução de desperdícios;
- Monitoramento de sistemas críticos;
- Governança tecnológica;
- Supervisão humana.

## Limitações

Os dados utilizados são simulados.

O sistema não controla equipamentos reais.

As recomendações não substituem decisões humanas
nem representam validações de engenharia espacial.

## Autores

- Lucas Sousa — RM: 573029
- Dayse Borges de Sousa — RM: 573036
