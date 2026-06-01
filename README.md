# Arbitralis Webhook PoC

PoC de um webhook assíncrono para receber mensagens, enfileirar o processamento e simular uma resposta gerada por LLM sem bloquear a requisição original.

> This is a challenge by [Coodesh](https://coodesh.com/)

## Tecnologias usadas

* Python 3.13
* FastAPI
* asyncio.Queue
* Pydantic
* Uvicorn
* Pytest
* Pytest Asyncio
* HTTPX
* Ruff
* mypy
* GitHub Actions

## Visão geral

O objetivo do projeto é demonstrar uma arquitetura simples para processar mensagens recebidas por webhook sem deixar o cliente aguardando uma operação lenta, como uma chamada para um LLM.

O fluxo implementado é:

```text
POST /webhook
    -> valida o payload
    -> adiciona a mensagem em uma fila em memória
    -> retorna 202 Accepted

Background worker
    -> consome a fila
    -> simula chamada lenta ao LLM
    -> simula envio da resposta para uma API externa
    -> registra logs estruturados
    -> aplica retry em caso de falha
    -> envia mensagens com falha para uma Dead Letter Queue em memória
```

## Decisões técnicas

### Webhook com resposta rápida

O endpoint `/webhook` não processa a mensagem diretamente. Ele apenas valida o payload, adiciona a mensagem na fila e retorna `202 Accepted`.

Essa decisão evita que o webhook fique bloqueado esperando uma operação lenta, como uma chamada para um LLM ou para uma API externa.

### Fila em memória

A fila foi implementada com `asyncio.Queue` por se tratar de uma PoC. Isso reduz a necessidade de infraestrutura externa e deixa o projeto simples de executar localmente.

Em produção, essa fila poderia ser substituída por Redis, RabbitMQ, AWS SQS ou outra solução equivalente, permitindo persistência, múltiplos workers, escalabilidade horizontal e uma Dead Letter Queue real.

### Worker em background

O processamento das mensagens acontece em um worker assíncrono iniciado junto com a aplicação.

Esse worker consome a fila, chama o serviço que simula o LLM e depois chama o serviço que simula o envio da resposta para uma API externa.

### Retry e Dead Letter Queue

Mensagens com erro são processadas novamente até o limite configurado de tentativas.

Caso a mensagem continue falhando, ela é enviada para uma Dead Letter Queue em memória. Isso evita que uma mensagem problemática trave o processamento das próximas mensagens ou desapareça sem rastreabilidade.

### Logs estruturados

Os logs são emitidos em formato JSON para facilitar observabilidade em ambientes distribuídos.

Eles incluem campos como:

* `event`
* `conversation_id`
* `message_id`
* `attempt`
* `level`
* `timestamp`

Dados sensíveis, como telefone do cliente e conteúdo da mensagem, não são registrados nos logs.

### Qualidade de código

O projeto possui validações automatizadas com:

* Ruff para lint
* mypy para checagem estática de tipos
* Pytest para testes automatizados
* GitHub Actions para rodar os checks no CI

## Como instalar

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/arbitralis-webhook-poc.git
cd arbitralis-webhook-poc
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como executar

Inicie a aplicação:

```bash
uvicorn app.main:app --reload
```

A documentação interativa ficará disponível em:

```text
http://127.0.0.1:8000/docs
```

## Como testar o webhook

Envie uma requisição `POST` para:

```text
http://127.0.0.1:8000/webhook
```

Payload de exemplo:

```json
{
  "conversation_id": "conv_123",
  "message_id": "msg_456",
  "customer_phone": "+5521999999999",
  "text": "Quero negociar minha dívida"
}
```

Resposta esperada:

```json
{
  "status": "accepted",
  "message_id": "msg_456"
}
```

Status HTTP esperado:

```text
202 Accepted
```

## Como simular falha no LLM

Para simular uma falha no processamento, envie uma mensagem contendo `force_llm_error` no campo `text`.

Exemplo:

```json
{
  "conversation_id": "conv_error",
  "message_id": "msg_error",
  "customer_phone": "+5521999999999",
  "text": "force_llm_error"
}
```

Nesse caso, o worker fará novas tentativas de processamento. Após exceder o limite de retries, a mensagem será enviada para a Dead Letter Queue em memória.

## Como rodar os testes

```bash
pytest
```

## Como rodar as validações de qualidade

```bash
ruff check .
mypy .
pytest
```

## CI

O projeto possui um workflow de GitHub Actions que executa automaticamente:

```text
ruff check .
mypy .
pytest
```

Esse pipeline roda em pushes e pull requests.

## Estrutura do projeto

```text
app/
├── main.py
├── schemas.py
├── queue.py
├── worker.py
├── logging_config.py
└── services/
    ├── llm_service.py
    └── outbound_service.py

tests/
├── test_webhook.py
└── test_worker.py

.github/
└── workflows/
    └── ci.yml
```

## Uso de AI Coding

Ferramentas de AI Coding foram usadas como apoio para acelerar a implementação, principalmente em tarefas repetitivas e revisão de alternativas.

As decisões de arquitetura, separação de responsabilidades, tratamento de erro, logs, testes e validações foram revisadas manualmente antes da entrega.

## Possíveis evoluções para produção

* Substituir `asyncio.Queue` por uma fila persistente, como Redis, RabbitMQ ou AWS SQS
* Implementar DLQ persistente
* Adicionar autenticação ou assinatura do webhook
* Adicionar idempotência por `message_id`
* Adicionar métricas de fila, tempo de processamento e taxa de erro
* Integrar com um LLM real
* Integrar com uma API real de envio de mensagens
* Adicionar tracing distribuído
* Configurar múltiplos workers