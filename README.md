# SmartFat

Sistema de gestao para academia com backend Flask, frontend estatico, Nginx e banco MySQL.

## Estrutura

```text
SmartFat/
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

## Como Rodar Com Docker

Na raiz do projeto, execute:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Depois acesse:

- Frontend: http://localhost
- Backend direto: http://localhost:5001

## Usuarios De Teste

- Administrador: `admin@smartfat.com` / `admin123`
- Treinador: `treinador@smartfat.com` / `treinador123`
- Aluno: `aluno@smartfat.com` / `aluno123`
