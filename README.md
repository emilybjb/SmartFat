# SmartFat

Sistema de gestao para academia com backend Flask, frontend estatico e banco MySQL.

## Estrutura

```text
SmartFat/
├── app.py                    # Atalho para executar o backend localmente
├── backend/
│   ├── app.py                # Aplicacao Flask e registro das rotas
│   ├── controllers/          # Regras/controladores
│   ├── routes/               # Blueprints da API
│   └── utils/                # Utilitarios compartilhados
├── database/
│   └── init.sql              # Script inicial do banco
├── docker/
│   ├── Dockerfile            # Imagem do backend
│   ├── docker-compose.yml    # Backend, MySQL e Nginx
│   └── nginx.conf            # Configuracao do frontend/proxy
├── frontend/
│   ├── css/
│   │   └── main.css
│   ├── js/
│   └── pages/
└── requirements.txt
```

## Como rodar

Com Docker:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Frontend: http://localhost
Backend direto: http://localhost:5001

Localmente:

```bash
pip install -r requirements.txt
python3 app.py
```
