import pandas as pd
import unicodedata
import json

# Fonction de normalisation (très importante pour la jointure Leaflet)
def norm(s):
    s = str(s).lower().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")
    s = s.replace(" ", "-")
    s = s.replace("'", "-")
    return s

# Lire ton fichier Excel
df = pd.read_excel("communes_ch4_tno_2024.xlsx")

data = {}

# Boucle sur les lignes
for _, row in df.iterrows():
    key = norm(row["nom_fr"])  # nom commune
    value = row["CH4_net_tonnes"]  # ⚠️ colonne correcte

    # Vérifier si valeur existe
    if pd.notna(value):
        data[key] = float(value)
    else:
        data[key] = 0

# Sauvegarde JSON
with open("ch4_tno_2024_commune.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ JSON normalisé créé avec succès")