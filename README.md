# 🛡️ IOC Manager - Gestor de Indicadores de Compromiso

Sistema centralizado para equipos de **Blue Team / SOC** que permite gestionar Indicadores de Compromiso (IOCs) mediante una API REST documentada con Swagger.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Características

- ✅ **API REST** documentada automáticamente con Swagger/OpenAPI
- ✅ **Registro de IOCs** desde scripts o herramientas externas
- ✅ **Dashboard web** para visualización de amenazas
- ✅ **Filtros** por tipo y severidad
- ✅ **Estadísticas** en tiempo real
- ✅ **Despliegue** con Docker (un solo comando)

## 🏗️ Arquitectura

```
┌─────────────────┐     POST /api/threats     ┌──────────────────┐
│  Scripts/SIEM   │ ────────────────────────► │                  │
│  (Detectores)   │                           │   FastAPI API    │
└─────────────────┘                           │                  │
                                              │  Swagger UI      │
┌─────────────────┐     GET /api/threats      │  (/docs)         │
│  Dashboard Web  │ ◄────────────────────────►│                  │
│  (Analistas)    │                           └────────┬─────────┘
└─────────────────┘                                    │
                                                       ▼
                                              ┌──────────────────┐
                                              │  SQLite /        │
                                              │  PostgreSQL      │
                                              └──────────────────┘
```

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar el repositorio
git clone <repo-url>
cd ioc-manager

# Levantar servicios
docker-compose up --build

# Acceder a:
# - Dashboard: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Opción 2: Ejecución Local (Desarrollo)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend: Abrir frontend/index.html en el navegador
# O servir con: python -m http.server 8080 -d frontend
```

## 📡 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/threats` | Lista todos los IOCs |
| `POST` | `/api/threats` | Registra nuevo IOC |
| `GET` | `/api/threats/{id}` | Obtiene IOC por ID |
| `DELETE` | `/api/threats/{id}` | Elimina IOC |
| `GET` | `/api/threats/stats/summary` | Estadísticas |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

### Ejemplo: Registrar un IOC

```bash
curl -X POST "http://localhost:8000/api/threats" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "IP",
    "value": "192.168.1.50",
    "severity": "High",
    "source": "Firewall-01"
  }'
```

### Ejemplo: Consultar IOCs

```bash
# Todos los IOCs
curl "http://localhost:8000/api/threats"

# Filtrar por tipo y severidad
curl "http://localhost:8000/api/threats?type=IP&severity=High"
```

## 📊 Modelo de Datos

### Tabla `threats`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Identificador único (PK) |
| `type` | String | Tipo: `IP`, `Hash`, `URL`, `Domain` |
| `value` | String | Valor del indicador (único) |
| `severity` | String | Severidad: `High`, `Medium`, `Low` |
| `date_detected` | DateTime | Fecha de registro |
| `source` | String | Fuente del IOC (opcional) |

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a BD | `sqlite:///./ioc_manager.db` |

### Usar PostgreSQL

```bash
# En docker-compose.yml o como variable de entorno:
DATABASE_URL=postgresql://user:password@host:5432/ioc_manager
```

## 📦 Despliegue en Producción (Gratuito)

### Render.com

1. Crear cuenta en [render.com](https://render.com)
2. Nuevo Web Service → Conectar repositorio
3. Build Command: `pip install -r backend/requirements.txt`
4. Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Agregar variable `DATABASE_URL` (usar PostgreSQL de Render)

### Railway

1. Crear cuenta en [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Agregar PostgreSQL desde el marketplace
4. El deploy es automático

## 🛠️ Desarrollo

### Estructura del Proyecto

```
ioc-manager/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   └── database.py      # DB connection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── docker-compose.yml
└── README.md
```

### Scripts de Ejemplo para Integración

```python
# script_detector.py - Ejemplo de envío automático de IOCs
import requests

API_URL = "http://localhost:8000/api/threats"

def report_ioc(ioc_type, value, severity, source="AutoDetector"):
    response = requests.post(API_URL, json={
        "type": ioc_type,
        "value": value,
        "severity": severity,
        "source": source
    })
    return response.json()

# Uso:
report_ioc("IP", "10.0.0.100", "High", "IDS-Suricata")
report_ioc("Hash", "a1b2c3d4e5f6...", "Medium", "VirusTotal")
```

## 📄 Licencia

MIT License - Libre para uso y modificación.

---

**Desarrollado para equipos de Blue Team / SOC** 🔒
