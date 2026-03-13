# LoveJob

Sistema di gestione presenze e consegne per magazzini. Permette ai responsabili di magazzino di inserire quotidianamente le presenze dei dipendenti e le consegne degli autisti e al personale HR di gestire e reportizzare i dati delle filiali.

---

## Stack

- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Auth:** dj-rest-auth (token based)
- **Deploy:** Docker Compose

---

## Struttura del progetto

```
lovejob-backend/
├── config/                  
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── app/                
│   ├── migrations/
│   ├── views/
│   │   └── presenze.py  
|   ├── admin.py
|   ├── apps.py
|   ├── authentication.py
│   ├── models.py
│   ├── permissions.py  
│   ├── serializers.py
│   ├── tests.py       
│   ├── urls.py         
│   └── utils.py
├── nginx/                
│   └─── nginx.conf
├── manage.py 
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

## Ruoli

| Ruolo | Permessi |
|---|---|
| `UP` | Gestione dipendenti, report presenze e consegne |
| `SUPER` | Visualizzazione presenze e consegne di tutte le filiali |
| `RESPONSABILE` | Inserimento presenze per la propria filiale |
| `RESPONSABILE_CONS` | Inserimento consegne autisti per la propria filiale |

---

## Deploy con Docker Compose

### 1. Clona il repository

```bash
git clone https://github.com/AleMeniconi18/lovejob-backend.git
cd lovejob-backend
```

### 2. Configura le variabili d'ambiente

```bash
cp .env.example .env
```

Modifica `.env` con i tuoi valori:

```env
DEBUG=False
SECRET_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=db
DB_PORT=
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Avvia i container

```bash
docker compose up -d --build
```

### 4. Crea superuser per accedere a Django Admin

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Accedi all'API

```
http://localhost:8000/api/
```

---

## Comandi utili

```bash
# Logs
docker compose logs -f web

# Shell Django
docker compose exec web python manage.py shell

# Ferma i container
docker compose down

# Ferma e rimuove i volumi 
docker compose down -v
```