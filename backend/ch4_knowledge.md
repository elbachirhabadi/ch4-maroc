# Base de connaissances — Méthane (CH₄)

## 1. Qu'est-ce que le méthane (CH₄) ?

Le méthane est un hydrocarbure de formule chimique **CH₄** : 1 atome de carbone lié à 4 atomes d'hydrogène. C'est le composant principal du gaz naturel. À température ambiante, il est gazeux, incolore et inodore. Il est inflammable.

C'est aussi le **deuxième gaz à effet de serre (GES) anthropique le plus important** après le CO₂, contribuant à environ **30% du réchauffement climatique observé depuis l'ère préindustrielle**.

## 2. Pouvoir de réchauffement global (PRG / GWP)

Le méthane a un PRG **80 fois supérieur** à celui du CO₂ sur 20 ans, et **environ 28 fois** sur 100 ans (rapport GIEC AR6, 2021). Sa durée de vie atmosphérique est courte (~12 ans), ce qui fait qu'agir sur le CH₄ a un **impact rapide** sur le climat.

| Horizon | PRG du CH₄ vs CO₂ |
|---|---|
| 20 ans | ~84 |
| 100 ans | ~28 |
| 500 ans | ~7,6 |

## 3. Sources d'émission

### Sources anthropiques (~60% du total)
1. **Élevage et agriculture** (~40% des émissions anthropiques) — fermentation entérique des ruminants, rizières inondées
2. **Énergie fossile** (~35%) — fuites lors de l'extraction et du transport de gaz naturel, pétrole, charbon
3. **Déchets** (~20%) — décharges, eaux usées, traitement des effluents
4. **Combustion de biomasse** (~5%)

### Sources naturelles (~40% du total)
- Zones humides (~80% des sources naturelles)
- Termites
- Hydrates de méthane (océans, pergélisol)
- Volcans, sources géologiques

## 4. Méthodologies de calcul des émissions

### Méthode FOD (First Order Decay) — méthode IPCC pour les déchets

C'est la **méthode officielle du GIEC** pour estimer les émissions de CH₄ des décharges de déchets solides municipaux (DSM).

**Principe** : la matière organique enfouie se dégrade dans le temps de manière exponentielle. Une décharge émet du CH₄ pendant des décennies après l'enfouissement.

**Formule simplifiée** :
```
E(t) = MSW × DOC × DOCf × MCF × F × (16/12) × (1 - e^(-k))
```
- `MSW` : Masse de déchets enfouis (tonnes)
- `DOC` : Carbone organique dégradable (fraction)
- `DOCf` : Fraction effectivement dégradée (généralement 0,5-0,6)
- `MCF` : Facteur de correction du méthane (selon type de décharge)
- `F` : Fraction de CH₄ dans le biogaz (~0,5)
- `k` : Constante de décroissance (selon climat et type de déchet)

**Avantages** : précis pour les déchets, recommandé internationalement.
**Limites** : nécessite des séries historiques d'enfouissement.

### Méthode TNO (Inventaire d'émissions néerlandais)

TNO (organisation néerlandaise de recherche appliquée) développe une approche d'**inventaire bottom-up** basée sur les facteurs d'émission par secteur d'activité. Utilisée notamment dans le cadre du programme européen Copernicus / CAMS.

**Différence avec FOD** : TNO couvre TOUS les secteurs (énergie, agriculture, déchets, industrie) alors que FOD se limite aux déchets.

**Format** : maillage géographique fin (typiquement 0,1° × 0,1°), agrégation par région possible.

### Comparaison FOD vs TNO

| Aspect | FOD | TNO |
|---|---|---|
| Champ | Déchets uniquement | Tous secteurs |
| Méthode | Décroissance exponentielle | Facteurs d'émission par activité |
| Données entrée | Historique d'enfouissement | Activités sectorielles |
| Résolution | Par site/commune | Maillage régulier |
| Usage | Inventaires nationaux GIEC | Modèles atmosphériques |

Dans le projet CH4 Maroc, FOD et TNO sont **deux estimations indépendantes** des mêmes émissions, permettant une comparaison croisée.

## 5. Unités de mesure

| Unité | Équivalent | Usage |
|---|---|---|
| 1 g CH₄ | — | Mesure ponctuelle |
| 1 kg CH₄ | 1 000 g | Émission unitaire |
| 1 t CH₄ (tonne) | 1 000 kg | **Unité du projet** |
| 1 kt CH₄ (kilotonne) | 1 000 t | Régional |
| 1 Mt CH₄ (mégatonne) | 1 000 kt | National / mondial |
| 1 Gg CH₄ | = 1 kt | Notation alternative |
| ppm.m | — | Concentration intégrée (imagerie satellite) |
| t CH₄/an | tonne par an | **Flux annuel — unité de la carte** |

Conversion en équivalent CO₂ (CO₂eq) sur 100 ans : `1 t CH₄ ≈ 28 t CO₂eq`.

## 6. Impacts du méthane

### Climatique
- Forçage radiatif puissant
- Effet rapide (durée de vie courte)
- Cible prioritaire dans le **Global Methane Pledge** (COP26, 2021) : -30% des émissions mondiales d'ici 2030

### Sanitaire et environnemental
- Précurseur d'**ozone troposphérique** (polluant pour la santé respiratoire et les cultures)
- Risque d'explosion en concentration élevée (4-15% dans l'air)
- Pollution de l'eau souterraine près des décharges

## 7. Stratégies de réduction

| Secteur | Mesure |
|---|---|
| Décharges | Captage du biogaz, valorisation énergétique, tri à la source |
| Élevage | Additifs alimentaires (algues, 3-NOP), changement de régime |
| Énergie fossile | Détection des fuites (LDAR), interdiction du torchage |
| Agriculture | Drainage alterné des rizières, gestion du lisier |

## 8. Le projet CH4 Maroc

### Contexte
Le Maroc s'est engagé à respecter ses contributions déterminées au niveau national (NDC) dans le cadre de l'Accord de Paris. Le suivi des émissions de CH₄ est une composante clé de cette démarche.

### Périmètre
- **12 régions** administratives + **1541 communes**
- Modèles : **FOD** (déchets) et **TNO** (multi-secteurs)
- Historique : 1994, 2004, 2014, 2024
- Projections (régions) : 2025 → 2040

### Régions du Maroc

| Code | Région |
|---|---|
| 1 | Tanger-Tétouan-Al Hoceima |
| 2 | L'Oriental |
| 3 | Fès-Meknès |
| 4 | Rabat-Salé-Kénitra |
| 5 | Béni Mellal-Khénifra |
| 6 | Casablanca-Settat |
| 7 | Marrakech-Safi |
| 8 | Drâa-Tafilalet |
| 9 | Souss-Massa |
| 10 | Guelmim-Oued Noun |
| 11 | Laâyoune-Sakia El Hamra |
| 12 | Dakhla-Oued Ed-Dahab |

### Approches du projet
1. **Approche statistique** (FOD/TNO) — ce portail
2. **Approche imagerie satellitaire** — détection de panaches CH₄ via instruments EMIT (NASA JPL) et TROPOMI (ESA), sur les 6 grandes décharges contrôlées du Maroc

### Sites majeurs de décharges contrôlées (CDC)
- Oum Azza (Rabat)
- Médiouna (Casablanca)
- Drarga (Agadir)
- Tanamart (Marrakech)
- Aïn Chkef (Fès)
- Gzenaya (Tanger)
