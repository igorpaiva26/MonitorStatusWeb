# 🌐 MonitorStatusWeb

Sistema de monitoramento e checagem de disponibilidade (uptime e latência) de URLs e serviços web em tempo real. Desenvolvido em **Python (Flask + Gunicorn)** com **Multithreading**, interface web interativa, API RESTful e suporte completo a **Docker**.

---

## 🚀 Funcionalidades

- **Monitoramento Contínuo:** Thread em segundo plano (*background worker*) checando periodicamente o status das URLs cadastradas.
- **Métricas em Tempo Real:**
  - Status do serviço (`online`, `offline`, `error`).
  - Código de status HTTP (ex: `200 OK`, `404 Not Found`, `500 Error`).
  - Latência e tempo de resposta em milissegundos (`response_time_ms`).
  - Histórico das últimas 10 checagens por URL.
- **Dashboard Web Interativo:** Interface amigável para visualizar o estado dos serviços e adicionar/remover URLs diretamente pelo navegador.
- **API RESTful:** Endpoints completos para integração programática com outros sistemas e automações.
- **Containerização Pronta para Produção:** Dockerfile configurado com usuário sem privilégios de root (`appuser`) e instrução de `HEALTHCHECK`.
- **Servidor WSGI:** Configuração pronta com **Gunicorn** para ambientes de alta concorrência.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework Web:** Flask 2.3+
- **Servidor de Produção:** Gunicorn 21.2+
- **Requisições & Rede:** Requests
- **Concorrência:** Python Threading nativo
- **Containerização:** Docker
- **Automação:** Shell Scripts (`deploy.sh`, `quick-deploy.sh`)

---

## 📂 Estrutura do Projeto

```text
MonitorStatusWeb/
├── app.py                # Aplicação Flask, thread de monitoramento e rotas
├── Dockerfile            # Imagem Docker com healthcheck e usuário não-root
├── gunicorn.conf.py      # Configuração de workers, timeout e logs do Gunicorn
├── requirements.txt      # Dependências Python (Flask, requests, gunicorn)
├── deploy.sh             # Script completo de deploy e validação em container
├── quick-deploy.sh       # Script rápido de reinicialização do container
├── .gitignore            # Arquivos ignorados pelo controle de versão
└── README.md             # Documentação do projeto
```

---

## 🔌 Endpoints da API REST

| Método | Endpoint | Descrição | Exemplo de Payload |
|---|---|---|---|
| `GET` | `/` | Interface Web com dashboard em tempo real | - |
| `GET` | `/health` | Verificação de integridade da própria aplicação | Resposta: `{"status": "healthy"}` |
| `GET` | `/api/urls` | Lista todas as URLs monitoradas e seus status | - |
| `POST` | `/api/urls` | Cadastra uma nova URL para monitoramento contínuo | `{"url": "https://google.com"}` |
| `DELETE` | `/api/urls/<url>` | Remove uma URL do monitoramento | - |

---

## ⚙️ Como Executar

### Pré-requisitos
- [Python 3.10+](https://www.python.org/) (para execução local)
- [Docker](https://www.docker.com/) (para execução em container)
- [Git](https://git-scm.com/)

---

### Opção 1: Executando com Docker (Recomendado)

#### Usando os Scripts de Automação:
```bash
# Permissão de execução
chmod +x deploy.sh quick-deploy.sh

# Deploy completo com validação de saúde:
./deploy.sh

# Ou reinicialização rápida:
./quick-deploy.sh
```

#### Manualmente via Docker CLI:
```bash
# 1. Build da imagem
docker build -t monitor-status-web:latest .

# 2. Executar o container na porta 5000
docker run -d -p 5000:5000 --name monitor-status-app monitor-status-web:latest
```

Acesse o painel web no navegador: **[http://localhost:5000](http://localhost:5000)**

---

### Opção 2: Executando Localmente (Python)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/igorpaiva26/MonitorStatusWeb.git
   cd MonitorStatusWeb
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   # No Linux/macOS:
   source venv/bin/activate
   # No Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor de desenvolvimento:**
   ```bash
   python app.py
   ```

5. **Ou inicie com Gunicorn (Produção - Linux/macOS):**
   ```bash
   gunicorn -c gunicorn.conf.py app:app
   ```

Acesse no navegador: **[http://localhost:5000](http://localhost:5000)**

---

## 👤 Autor

Desenvolvido por **[Igor Paiva](https://github.com/igorpaiva26)**.
