# Assistant IA — Backend CH4 Maroc

Backend Python (FastAPI) qui connecte la page **`assistant.html`** du géoportail à un LLM **local** (Ollama).

L'agent répond à toutes les questions liées au méthane, aux émissions, au climat, et au projet CH4 Maroc — avec les chiffres exacts par région et par année.

## 📋 Prérequis

- **Windows 10/11** (ou Mac/Linux)
- **Python 3.10+**
- **8 Go RAM minimum** (16 Go recommandé pour le modèle 7B)
- **5 Go d'espace disque** pour le modèle

## 🚀 Installation (1 fois)

### Étape 1 — Installer Ollama

1. Va sur **https://ollama.com/download**
2. Télécharge la version Windows et installe-la
3. Ollama démarre automatiquement et tourne en arrière-plan (icône système)

### Étape 2 — Télécharger un modèle

Ouvre **PowerShell** ou **CMD** et lance :

```powershell
ollama pull qwen2.5:7b
```

(téléchargement : ~4.7 Go, prendre un café ☕)

> 💡 **Hardware modeste ?** Utilise un modèle plus léger :
> ```powershell
> ollama pull qwen2.5:3b
> ```
> Puis avant de lancer le backend : `set OLLAMA_MODEL=qwen2.5:3b`

### Étape 3 — Installer les dépendances Python

Depuis le dossier `backend\` :

```powershell
cd "c:\PFE\CARTE THEMATIQUE\backend"
pip install -r requirements.txt
```

## ▶️ Lancement (à chaque session)

Tu as besoin de **2 terminaux ouverts**, ou de lancer Ollama en arrière-plan.

### Terminal 1 — Ollama

S'il ne tourne pas déjà :

```powershell
ollama serve
```

Laisse ce terminal ouvert. Sur Windows, Ollama démarre souvent automatiquement après install — vérifie avec :

```powershell
curl http://localhost:11434
```

### Terminal 2 — Backend FastAPI

```powershell
cd "c:\PFE\CARTE THEMATIQUE\backend"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Tu dois voir :

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Étape finale — Ouvrir la page

Ouvre dans un navigateur :

```
file:///c:/PFE/CARTE%20THEMATIQUE/geoportail-ch4/assistant.html
```

ou via un serveur HTTP local :

```powershell
cd "c:\PFE\CARTE THEMATIQUE\geoportail-ch4"
python -m http.server 8080
# puis ouvrir http://localhost:8080/assistant.html
```

## ✅ Vérification

1. Pastille **vert "En ligne"** en haut à droite → tout fonctionne
2. Pastille **rouge "Backend arrêté"** → relance `uvicorn`
3. Pastille **rouge "Ollama arrêté"** → relance Ollama
4. Pastille **rouge "Modèle manquant"** → `ollama pull qwen2.5:7b`

Tu peux aussi tester l'API directement :

```powershell
curl http://localhost:8000/health
```

## ⚙️ Configuration (variables d'env)

| Variable | Défaut | Description |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | URL de l'API Ollama |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Nom du modèle Ollama |
| `OLLAMA_TIMEOUT` | `180` | Timeout requête en secondes |

Exemple pour changer de modèle :

```powershell
set OLLAMA_MODEL=mistral:7b
uvicorn app:app --port 8000 --reload
```

## 🧠 Modèles recommandés

| Modèle | Taille | RAM min | Qualité FR | Vitesse |
|---|---|---|---|---|
| `qwen2.5:3b` | 1.9 GB | 8 GB | ★★★☆☆ | ⚡ Rapide |
| `qwen2.5:7b` ⭐ | 4.7 GB | 16 GB | ★★★★☆ | Normal |
| `mistral:7b` | 4.1 GB | 16 GB | ★★★★★ | Normal |
| `llama3.1:8b` | 4.7 GB | 16 GB | ★★★★☆ | Normal |

## 🐛 Dépannage

### "Ollama indisponible"
- Ouvre l'app Ollama (Windows) ou lance `ollama serve`
- Vérifie : `curl http://localhost:11434`

### "Timeout après 180s"
- Modèle trop lourd pour ta RAM → bascule sur `qwen2.5:3b`
- Première requête plus longue (chargement du modèle en RAM)

### "Modèle non installé"
- `ollama list` → vérifie les modèles présents
- `ollama pull <nom>` pour télécharger

### Le frontend dit "Backend arrêté"
- Le serveur uvicorn n'est pas lancé
- Mauvais port (doit être 8000)
- CORS : déjà configuré pour accepter toutes les origines

### Le frontend dit "CORS error"
- C'est normal si tu ouvres la page en `file://` sur certains navigateurs
- Solution : lance un serveur HTTP local (voir Étape finale ci-dessus)

## 📂 Structure des fichiers

```
backend/
├── app.py                Backend FastAPI
├── ch4_knowledge.md      Base de connaissance CH4 (injectée à chaque requête)
├── requirements.txt      Dépendances Python
└── README.md             Ce fichier
```

L'agent lit automatiquement :
- `ch4_knowledge.md` (concepts généraux)
- `../geoportail-ch4/qgis_project/data/regions_ch4.geojson` (données chiffrées du projet)

## 🔧 Personnaliser le comportement de l'agent

Édite **`app.py`** pour modifier :
- **`SYSTEM_PROMPT`** : rôle, ton, contraintes, règles
- **`build_data_context()`** : quelles années/régions injecter
- **`options.temperature`** : 0.0 = déterministe, 1.0 = créatif (défaut 0.3)
- **`options.num_ctx`** : taille du contexte (défaut 8192)

Édite **`ch4_knowledge.md`** pour enrichir la base de connaissance.

## 🌐 Accès depuis un autre PC

Si tu veux y accéder depuis un autre poste sur le même réseau :

1. Backend lancé avec `--host 0.0.0.0` (déjà le cas)
2. Pare-feu Windows : autoriser Python sur le port 8000
3. Sur le frontend (`assistant.html`), remplacer :
   ```js
   const API_BASE = "http://localhost:8000";
   ```
   par :
   ```js
   const API_BASE = "http://192.168.1.X:8000";  // IP du PC backend
   ```
