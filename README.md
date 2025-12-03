# To-Do-RESTful-api-jwt

# Anwendungsübersicht

<img width="1028" height="916" alt="image" src="https://github.com/user-attachments/assets/4f61046b-31a8-4160-aa24-a8d96db23387" />
<img width="1100" height="911" alt="image" src="https://github.com/user-attachments/assets/dfd8554e-4410-44aa-b024-7351c5ed73a0" />
<img width="1040" height="864" alt="image" src="https://github.com/user-attachments/assets/3fc18f01-325c-4e92-82d9-6f6535c0f891" />


# Hauptmerkmale
JWT-basierte Authentifizierung mit sicheren Zugangstokens
Vollständige CRUD-Operationen für To-Do-Einträge
SQLite-Datenbank mit SQLAlchemy ORM
RESTful API-Design mit korrekten HTTP-Statuscodes
Interaktive Web-Oberfläche zum Testen der API
Umfassende Fehlerbehandlung und Validierung
Unit-Tests mit pytest

# Stack
Python, Flask
Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt
SQLite (produktionsbereit für PostgreSQL/MySQL)
HTML, CSS, JavaScript für die Web-Oberfläche
pytest für Testing

# Projektstruktur
app.py: Hauptanwendung mit allen API-Endpunkten
requirements.txt: Python-Abhängigkeiten
.env.example: Vorlage für Umgebungsvariablen
.gitignore: Git-Ignore-Datei
templates/index.html: Web-Oberfläche
tests/test_api.py: Unit-Tests

# API-Endpunkte
POST /api/auth/register: Registrierung eines neuen Benutzers
POST /api/auth/login: Anmeldung und Erhalt eines JWT-Tokens
GET /api/todos: Abruf aller To-Dos des Benutzers (authentifiziert)
POST /api/todos: Erstellen eines neuen To-Dos (authentifiziert)
GET, PUT, DELETE /api/todos/<id>: Operationen für ein bestimmtes To-Do (authentifiziert)


