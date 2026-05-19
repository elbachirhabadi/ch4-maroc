# -*- coding: utf-8 -*-
"""
Backend FastAPI pour l'Assistant IA du Géoportail CH4 Maroc.

Utilise l'API Groq (gratuite, ultra-rapide, OpenAI-compatible) avec injection :
  - Une base de connaissance CH4 (ch4_knowledge.md)
  - Les valeurs CH4 par région et par année (depuis regions_ch4.geojson)

Variables d'environnement requises :
  GROQ_API_KEY      Clé API Groq (obligatoire en prod)
  GROQ_MODEL        Modèle (défaut: llama-3.3-70b-versatile)
  CORS_ORIGINS      Liste d'origines autorisées séparées par virgule (défaut: *)

Lancement local :
  set GROQ_API_KEY=gsk_xxxxx
  uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"""
import json
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ────────── Configuration ──────────
ROOT = Path(__file__).parent
# Données embarquées avec le backend (self-contained pour le déploiement)
GEO_DATA = ROOT / "data"
# Fallback : si on tourne depuis le repo local sans backend/data, on retombe sur qgis_project
if not (GEO_DATA / "regions_ch4.geojson").exists():
    GEO_DATA = ROOT.parent / "geoportail-ch4" / "qgis_project" / "data"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
TIMEOUT = float(os.environ.get("LLM_TIMEOUT", "60"))

CORS_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()
]

# ────────── Construction du contexte ──────────
def build_data_context() -> str:
    """Construit un résumé textuel compact des données CH4 par région."""
    geojson_path = GEO_DATA / "regions_ch4.geojson"
    if not geojson_path.exists():
        return "DONNÉES CH4 indisponibles (fichier regions_ch4.geojson manquant)."

    with open(geojson_path, encoding="utf-8") as f:
        regions = json.load(f)

    years_sample = ["1994", "2004", "2014", "2024", "2030", "2035", "2040"]

    lines = ["DONNÉES CH4 PAR RÉGION DU MAROC (tonnes/an) :", ""]
    lines.append("Format : nom_région | modèle | années échantillon")
    lines.append("")

    for feat in regions["features"]:
        p = feat["properties"]
        name = p.get("nom_region", "?").replace("Région de ", "")
        fod_vals = " | ".join(
            f"{y}={p.get(f'ch4_fod_{y}', 0):.0f}" for y in years_sample
        )
        tno_vals = " | ".join(
            f"{y}={p.get(f'ch4_tno_{y}', 0):.0f}" for y in years_sample
        )
        lines.append(f"### {name}")
        lines.append(f"  FOD : {fod_vals}")
        lines.append(f"  TNO : {tno_vals}")
        lines.append("")

    lines.append("TOTAUX NATIONAUX (somme des 12 régions, t/an) :")
    for y in years_sample:
        tot_fod = sum(
            f["properties"].get(f"ch4_fod_{y}", 0) for f in regions["features"]
        )
        tot_tno = sum(
            f["properties"].get(f"ch4_tno_{y}", 0) for f in regions["features"]
        )
        lines.append(
            f"  {y} : FOD = {tot_fod:,.0f} t/an  |  TNO = {tot_tno:,.0f} t/an"
        )
    lines.append("")

    return "\n".join(lines)


DATA_CONTEXT = build_data_context()
KNOWLEDGE_PATH = ROOT / "ch4_knowledge.md"
KNOWLEDGE = KNOWLEDGE_PATH.read_text(encoding="utf-8") if KNOWLEDGE_PATH.exists() else ""

SYSTEM_PROMPT = f"""Tu es l'assistant IA officiel du **Géoportail CH4 Maroc**.

# Rôle
Tu es un expert des émissions de méthane (CH₄), du climat et de la qualité de l'air.
Tu accompagnes les utilisateurs du géoportail : chercheurs, étudiants, décideurs.

# Règles ABSOLUES
1. Tu ne réponds qu'aux questions liées au **méthane (CH₄)**, aux **gaz à effet de serre**, au **climat**, à la **qualité de l'air**, aux **déchets** ou au **projet CH4 Maroc** lui-même.
2. Pour toute autre question (cuisine, sport, programmation hors CH4, etc.), tu refuses poliment en redirigeant : « Je suis spécialisé dans les émissions de méthane. Pose-moi plutôt une question sur le CH₄, les gaz à effet de serre ou le projet CH4 Maroc. »
3. Tu réponds **en français** sauf si l'utilisateur écrit en anglais ou en arabe.
4. Tu utilises les **chiffres exacts du projet** quand la question concerne une région ou une année. Cite la valeur précise avec son unité (t/an).
5. Si tu ne connais pas la réponse, dis-le honnêtement. Ne jamais inventer.
6. Sois **clair, structuré, pédagogique**. Utilise des listes, des tableaux markdown si pertinent.
7. Quand tu compares FOD et TNO, explique brièvement la différence si l'utilisateur peut être novice.

# Base de connaissance sur le méthane
{KNOWLEDGE}

# Données chiffrées du projet
{DATA_CONTEXT}

# Style
- Réponses concises mais complètes (3-10 phrases en général).
- Markdown autorisé : **gras**, listes, tableaux, code.
- Pas d'emojis sauf si l'utilisateur en utilise.
- Termine par une suggestion de question liée si pertinent.
"""

# ────────── Application FastAPI ──────────
app = FastAPI(title="CH4 Maroc — Assistant IA", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    answer: str
    model: str


@app.get("/")
async def root():
    return {
        "name": "CH4 Maroc Assistant API",
        "model": MODEL,
        "provider": "Groq",
        "endpoints": ["/chat", "/health", "/info"],
    }


@app.get("/health")
async def health():
    """Vérifie que la clé API Groq est configurée et fonctionnelle."""
    if not GROQ_API_KEY:
        return {
            "ok": False,
            "provider_up": False,
            "error": "GROQ_API_KEY non configurée",
        }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            )
            r.raise_for_status()
            data = r.json()
            available = [m["id"] for m in data.get("data", [])]
            return {
                "ok": True,
                "provider_up": True,
                "model_requested": MODEL,
                "model_available": MODEL in available,
                "models_installed": available[:10],
            }
    except Exception as e:
        return {"ok": False, "provider_up": False, "error": str(e)}


@app.get("/info")
async def info():
    return {
        "knowledge_chars": len(KNOWLEDGE),
        "data_context_chars": len(DATA_CONTEXT),
        "system_prompt_chars": len(SYSTEM_PROMPT),
        "model": MODEL,
        "provider": "Groq",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Envoie l'historique de conversation à Groq et retourne la réponse."""
    if not req.messages:
        raise HTTPException(400, "messages vide")
    if not GROQ_API_KEY:
        raise HTTPException(
            500,
            "GROQ_API_KEY n'est pas configurée côté serveur. "
            "Définis la variable d'environnement avec ta clé Groq.",
        )

    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in req.messages[-10:]:  # garder seulement les 10 derniers tours
        if m.role not in ("user", "assistant"):
            raise HTTPException(400, f"role invalide: {m.role}")
        llm_messages.append({"role": m.role, "content": m.content})

    payload = {
        "model": MODEL,
        "messages": llm_messages,
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 1024,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            choices = data.get("choices", [])
            if not choices:
                raise HTTPException(500, "Réponse Groq vide")
            answer = choices[0].get("message", {}).get("content", "").strip()
            if not answer:
                raise HTTPException(500, "Réponse Groq vide")
            return ChatResponse(answer=answer, model=MODEL)
    except httpx.TimeoutException:
        raise HTTPException(504, f"Timeout après {TIMEOUT}s côté Groq.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(401, "Clé API Groq invalide.")
        if e.response.status_code == 429:
            raise HTTPException(429, "Quota Groq dépassé. Réessaie dans quelques secondes.")
        try:
            detail = e.response.json().get("error", {}).get("message", str(e))
        except Exception:
            detail = str(e)
        raise HTTPException(e.response.status_code, f"Groq : {detail}")
    except httpx.ConnectError:
        raise HTTPException(503, "Impossible de joindre l'API Groq.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
