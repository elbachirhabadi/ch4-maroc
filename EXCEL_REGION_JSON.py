import pandas as pd
import unicodedata
import json

def norm(s):
    s = str(s).lower().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")
    s = s.replace(" ", "-")
    s = s.replace("'", "-")
    return s

df = pd.read_excel("ch4_tno_2040_region.xlsx")

data = {}

for _, row in df.iterrows():
    key = norm(row["nom_region"])
    data[key] = float(row["CH4_net_tonnes"])

with open("ch4_tno_2040_region.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("JSON normalisé créé")