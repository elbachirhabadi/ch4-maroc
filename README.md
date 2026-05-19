# CH4 Maroc — Géoportail thématique des émissions de méthane

Projet de Fin d'Études — Géoportail interactif pour visualiser les émissions de
méthane (CH₄) au Maroc selon les modèles **FOD (IPCC)** et **TNO (Pays-Bas)** par
**région** et **commune**, sur la période **1994–2040**.

## Architecture

```
.
├── geoportail-ch4/        ← Frontend statique (HTML/CSS/JS, Leaflet, Chart.js)
│   ├── accueil.html
│   ├── carte_interactive.html
│   ├── statistiques.html
│   ├── articles.html
│   ├── assistant.html     ← Chat IA
│   ├── data/              ← GeoJSON + JSON CH4 par année
│   ├── js/                ← Logique métier + i18n FR/EN
│   └── css/
│
├── backend/               ← API FastAPI pour l'Assistant IA (Groq)
│   ├── app.py
│   ├── ch4_knowledge.md   ← Base de connaissance injectée dans le prompt
│   ├── data/              ← regions_ch4.geojson (chiffres exacts)
│   └── requirements.txt
│
├── render.yaml            ← Config déploiement Render.com (backend)
└── .gitignore
```

## Déploiement (production)

### 1) Backend — Render.com

1. Crée un compte sur [render.com](https://render.com) (gratuit, login GitHub).
2. **New +** → **Web Service** → connecte ce repo.
3. Render détecte automatiquement `render.yaml`.
4. Dans **Environment**, ajoute la variable `GROQ_API_KEY` avec ta clé Groq
   (à créer sur [console.groq.com](https://console.groq.com)).
5. Clique **Deploy**. Au bout de 2–3 min, ton API est en ligne :
   `https://ch4-maroc-backend.onrender.com`
6. Vérifie la santé : `https://ch4-maroc-backend.onrender.com/health`

> ℹ️ Le tier gratuit Render **endort** le service après 15 min d'inactivité.
> La 1ʳᵉ requête après endormissement met ~30 s ; les suivantes sont rapides.

### 2) Frontend — Netlify

1. Crée un compte sur [netlify.com](https://netlify.com) (login GitHub).
2. **Add new site** → **Import from Git** → choisis ce repo.
3. Configure :
   - **Base directory** : `geoportail-ch4`
   - **Build command** : *(vide — site 100% statique)*
   - **Publish directory** : `.`
4. Clique **Deploy**. URL : `https://ch4-maroc.netlify.app`

### 3) Lier le frontend au backend

Dans `geoportail-ch4/assistant.html`, l'URL de l'API est lue depuis
`window.CH4_API_BASE` si défini, sinon depuis le `<meta name="ch4-api">`.
Modifie cette ligne dans `assistant.html` (cherche `<meta name="ch4-api"`) :

```html
<meta name="ch4-api" content="https://ch4-maroc-backend.onrender.com">
```

Commit + push → Netlify redéploie automatiquement.

## Développement local

### Frontend
```powershell
cd geoportail-ch4
python -m http.server 5500
# ouvrir http://localhost:5500/accueil.html
```

### Backend
```powershell
cd backend
pip install -r requirements.txt
$env:GROQ_API_KEY = "gsk_xxxxx"
uvicorn app:app --port 8000 --reload
```

## Stack technique

- **Frontend** : HTML5, CSS3, JavaScript vanilla, Leaflet 1.9, Chart.js, marked.js
- **Backend** : Python 3.11, FastAPI, httpx, Pydantic
- **LLM** : Llama 3.3 70B via Groq API (gratuit, ultra-rapide)
- **Hébergement** : Netlify (frontend) + Render.com (backend)
- **Données** : GeoJSON / Shapefile / Excel sources

## Licence

Projet académique — usage éducatif uniquement.
