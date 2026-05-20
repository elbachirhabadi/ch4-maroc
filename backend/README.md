---
title: CH4 Maroc Backend
emoji: 🌍
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Assistant IA pour le geoportail des emissions CH4 du Maroc
---

# CH4 Maroc — Backend Assistant IA

API FastAPI alimentant l'assistant IA du géoportail CH4 Maroc, utilisant
**Groq (Llama 3.3 70B)** avec injection de la base de connaissance CH4 et
des données chiffrées par région.

Frontend : https://github.com/elbachirhabadi/ch4-maroc

## Endpoints

- `GET /` — Info sur l'API
- `GET /health` — Statut Groq + modèle disponible
- `GET /info` — Tailles du prompt et de la base de connaissance
- `POST /chat` — Envoyer une conversation, recevoir la réponse

## Variables d'environnement requises

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Clé API Groq (obligatoire) — à configurer dans **Settings → Variables and secrets** |
| `GROQ_MODEL` | Modèle Groq (défaut: `llama-3.3-70b-versatile`) |
| `CORS_ORIGINS` | Origines autorisées (défaut: `*`) |

## Local dev

```bash
pip install -r requirements.txt
export GROQ_API_KEY=gsk_xxxxx
uvicorn app:app --port 8000
```
