# zumda_backend_mvp

Minimal Django + Django REST Framework backend for the zumda MVP.

## Endpoints
- POST /api/requests/
- GET /api/requests/
- GET /api/requests/{id}/
- PATCH /api/requests/{id}/status/

## Sample create request
```bash
curl -X POST http://127.0.0.1:8000/api/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "halal_food",
    "latitude": 35.712300,
    "longitude": 139.777100,
    "area": "ueno",
    "note": "Need something nearby tonight",
    "estimated_price": 1500,
    "language": "en"
  }'
```

## Sample status update
```bash
curl -X PATCH http://127.0.0.1:8000/api/requests/1/status/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "assigned"
  }'
```

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
