#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un projet QGIS complet pour le portail CH4 Maroc.

Sorties dans geoportail-ch4/qgis_project/ :
  - CH4_Maroc.qgs              Projet QGIS (à ouvrir directement)
  - data/regions_ch4.geojson   Régions + colonnes ch4_{model}_{year}
  - data/communes_ch4.geojson  Communes + colonnes ch4_{model}_{year}
  - load_in_qgis.py            Script PyQGIS de secours
  - README.md                  Instructions

Usage :  python build_qgis_project.py
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent
SRC  = ROOT / "geoportail-ch4" / "data"
OUT  = ROOT / "geoportail-ch4" / "qgis_project"
DOUT = OUT / "data"
DOUT.mkdir(parents=True, exist_ok=True)

MODELS = ['fod', 'tno']
YEARS_REGIONS  = ['1994', '2004', '2014', '2024'] + [str(y) for y in range(2025, 2041)]
YEARS_COMMUNES = ['1994', '2004', '2014', '2024']

PALETTE = [
    "#FFFFE5", "#FFF7BC", "#FFEDA0", "#FED976", "#FEB24C",
    "#FD8D3C", "#FC4E2A", "#E31A1C", "#BD0026", "#800026"
]

# ────────── Helpers ──────────
def slug(s):
    s = s.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def region_key(name):
    c = re.sub(r"^r[ée]gion\s+de\s+", "", name, flags=re.IGNORECASE)
    c = re.sub(r"^l['‘’]\s*", "l", c, flags=re.IGNORECASE)
    c = re.sub(r"['‘’]", "", c)
    return "region-de-" + slug(c)

def lookup_region(ch4, name):
    c = re.sub(r"^r[ée]gion\s+de\s+", "", name, flags=re.IGNORECASE)
    # 4 conventions de clés rencontrées :
    #   "region-de-loriental"  (fichiers 1994-2024)
    #   "l-oriental"           (fichiers FOD 2025-2040)
    #   "loriental"            (variante sans apostrophe)
    #   "oriental"             (fichiers TNO 2025-2040, article supprimé)
    candidates = (
        region_key(name),
        slug(c),
        slug(re.sub(r"['‘’]", "", c)),
        slug(re.sub(r"^l['‘’\s]+", "", c, flags=re.IGNORECASE)),
    )
    for k in candidates:
        if k in ch4:
            return float(ch4[k])
    return 0.0

def lookup_commune(ch4, name):
    return float(ch4.get(slug(name), 0))

def quantile_breaks(values, k=10):
    """k-1 ruptures pour produire k classes."""
    vals = sorted(v for v in values if v > 0)
    if len(vals) < 2:
        return [0.0] * (k - 1)
    return [vals[int(len(vals) * (i / k))] for i in range(1, k)]

def hex_to_rgba(h, a=255):
    h = h.lstrip('#')
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a}"

def xml_escape(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                  .replace('"', '&quot;').replace("'", '&apos;'))

# ────────── Enrichissement GeoJSON ──────────
def enrich(src_name, mode, years, name_field, lookup_fn):
    with open(SRC / src_name, encoding='utf-8') as f:
        geo = json.load(f)
    breaks = {}
    suffix = 'region' if mode == 'regions' else 'commune'
    for model in MODELS:
        for year in years:
            jpath = SRC / f"ch4_{model}_{year}_{suffix}.json"
            if not jpath.exists():
                continue
            with open(jpath, encoding='utf-8') as f:
                ch4 = json.load(f)
            col = f"ch4_{model}_{year}"
            values = []
            for feat in geo['features']:
                name = feat['properties'].get(name_field, '') or ''
                v = lookup_fn(ch4, name)
                feat['properties'][col] = round(v, 4)
                values.append(v)
            breaks[f"{model}_{year}"] = quantile_breaks(values, k=10)
    return geo, breaks

print("=" * 60)
print("== Étape 1/3 : enrichissement des GeoJSON")
print("=" * 60)

regions, breaks_reg = enrich('regions.geojson', 'regions',
                              YEARS_REGIONS, 'nom_region', lookup_region)
ch4_cols_reg = sum(1 for k in regions['features'][0]['properties'] if k.startswith('ch4_'))
print(f"  Régions  : {len(regions['features'])} entités × {ch4_cols_reg} colonnes CH4")

communes, breaks_com = enrich('communes.geojson', 'communes',
                               YEARS_COMMUNES, 'nom_fr', lookup_commune)
ch4_cols_com = sum(1 for k in communes['features'][0]['properties'] if k.startswith('ch4_'))
print(f"  Communes : {len(communes['features'])} entités × {ch4_cols_com} colonnes CH4")

with open(DOUT / 'regions_ch4.geojson', 'w', encoding='utf-8') as f:
    json.dump(regions, f, ensure_ascii=False, separators=(',', ':'))
with open(DOUT / 'communes_ch4.geojson', 'w', encoding='utf-8') as f:
    json.dump(communes, f, ensure_ascii=False, separators=(',', ':'))

# Liste des champs présents dans chaque GeoJSON
def collect_fields(geo):
    fields = []
    for prop, val in geo['features'][0]['properties'].items():
        if isinstance(val, bool):
            t = "Bool"
        elif isinstance(val, int):
            t = "LongLong"
        elif isinstance(val, float):
            t = "Double"
        else:
            t = "String"
        fields.append((prop, t))
    return fields

REG_FIELDS = collect_fields(regions)
COM_FIELDS = collect_fields(communes)

# ────────── Génération XML QGIS ──────────
print("=" * 60)
print("== Étape 2/3 : construction du projet .qgs")
print("=" * 60)

WKT_4326 = ('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,'
            'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,'
            'AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,'
            'AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],'
            'AUTHORITY["EPSG","4326"]]')

CRS_BLOCK = f'''<spatialrefsys nativeFormat="Wkt">
      <wkt>{WKT_4326}</wkt>
      <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
      <srsid>3452</srsid>
      <srid>4326</srid>
      <authid>EPSG:4326</authid>
      <description>WGS 84</description>
      <projectionacronym>longlat</projectionacronym>
      <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
      <geographicflag>true</geographicflag>
    </spatialrefsys>'''

def fill_layer(color_hex):
    rgba = hex_to_rgba(color_hex)
    return f'''<layer pass="0" class="SimpleFill" enabled="1" locked="0">
        <prop k="color" v="{rgba}"/>
        <prop k="joinstyle" v="bevel"/>
        <prop k="offset" v="0,0"/>
        <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
        <prop k="offset_unit" v="MM"/>
        <prop k="outline_color" v="255,255,255,255"/>
        <prop k="outline_style" v="solid"/>
        <prop k="outline_width" v="0.2"/>
        <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
        <prop k="outline_width_unit" v="MM"/>
        <prop k="style" v="solid"/>
      </layer>'''

def symbol_xml(idx, color_hex):
    return f'''<symbol type="fill" name="{idx}" alpha="1" clip_to_extent="1" force_rhr="0">
      {fill_layer(color_hex)}
    </symbol>'''

def renderer_xml(attr, breaks):
    bounds = [0.0] + [float(b) for b in breaks] + [1e15]
    ranges, symbols = [], []
    for i in range(10):
        lo, hi = bounds[i], bounds[i + 1]
        if i < 9:
            lbl = f"{lo:.0f} – {hi:.0f}"
        else:
            lbl = f"> {bounds[9]:.0f}"
        ranges.append(f'<range lower="{lo}" upper="{hi}" symbol="{i}" '
                      f'label="{xml_escape(lbl)}" render="true"/>')
        symbols.append(symbol_xml(str(i), PALETTE[i]))
    return f'''<renderer-v2 type="graduatedSymbol" attr="{attr}" graduatedMethod="GraduatedColor" symbollevels="0" forceraster="0">
    <ranges>
      {"".join(ranges)}
    </ranges>
    <symbols>
      {"".join(symbols)}
    </symbols>
    <source-symbol>
      {symbol_xml("0", PALETTE[5])}
    </source-symbol>
  </renderer-v2>'''

def fields_xml(fields):
    return ''.join(
        f'<field configurationFlags="None" name="{xml_escape(name)}"><editWidget type="TextEdit"><config><Option/></config></editWidget></field>'
        for name, _ in fields
    )

def vector_maplayer_xml(layer_id, name, source, fields, attr, breaks):
    return f'''<maplayer styleCategories="AllStyleCategories" type="vector" wkbType="MultiPolygon" geometry="Polygon" hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="100000000" simplifyDrawingHints="1" simplifyDrawingTol="1" simplifyAlgorithm="0" simplifyLocal="1" simplifyMaxScale="1" autoRefreshEnabled="0" autoRefreshTime="0" labelsEnabled="0" readOnly="0" refreshOnNotifyEnabled="0" refreshOnNotifyMessage="">
  <extent>
    <xmin>-17.5</xmin><ymin>20.5</ymin><xmax>-1.0</xmax><ymax>36.0</ymax>
  </extent>
  <id>{layer_id}</id>
  <datasource>{xml_escape(source)}</datasource>
  <provider encoding="UTF-8">ogr</provider>
  <layername>{xml_escape(name)}</layername>
  <srs>
    {CRS_BLOCK}
  </srs>
  <fieldConfiguration>{fields_xml(fields)}</fieldConfiguration>
  <aliases/>
  <defaults/>
  <constraints/>
  <constraintExpressions/>
  <expressionfields/>
  {renderer_xml(attr, breaks)}
  <labeling type="simple"><settings/></labeling>
  <customproperties><Option/></customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldDependencies/>
</maplayer>'''

def raster_maplayer_xml(layer_id, name, datasource):
    return f'''<maplayer styleCategories="AllStyleCategories" type="raster" hasScaleBasedVisibilityFlag="0" maxScale="0" minScale="1e+08" autoRefreshEnabled="0" autoRefreshTime="0" refreshOnNotifyEnabled="0" refreshOnNotifyMessage="">
  <extent>
    <xmin>-20037508.34</xmin><ymin>-20037508.34</ymin><xmax>20037508.34</xmax><ymax>20037508.34</ymax>
  </extent>
  <id>{layer_id}</id>
  <datasource>{xml_escape(datasource)}</datasource>
  <provider>wms</provider>
  <layername>{xml_escape(name)}</layername>
  <srs>
    {CRS_BLOCK}
  </srs>
  <customproperties><Option/></customproperties>
  <pipe>
    <provider><resampling enabled="false" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2"/></provider>
    <rasterrenderer opacity="1" alphaBand="-1" type="multibandcolor" redBand="1" greenBand="2" blueBand="3" nodataColor="">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation saturation="0" colorizeOn="0" colorizeRed="255" colorizeGreen="128" colorizeBlue="128" colorizeStrength="100" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</maplayer>'''

# ────────── Sources de fonds de carte ──────────
SAT = 'type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0'
LAB = 'type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0'
OSM = 'type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0'

# ────────── Construction des couches ──────────
LAYERS = []  # (id, name, xml, kind)

LAYERS.append(('bm_satellite', 'Satellite (Esri)',
               raster_maplayer_xml('bm_satellite', 'Satellite (Esri)', SAT), 'raster'))
LAYERS.append(('bm_labels', 'Labels (Esri)',
               raster_maplayer_xml('bm_labels', 'Labels (Esri)', LAB), 'raster'))
LAYERS.append(('bm_osm', 'OpenStreetMap',
               raster_maplayer_xml('bm_osm', 'OpenStreetMap', OSM), 'raster'))

regions_source  = "./data/regions_ch4.geojson|layername=regions_ch4"
communes_source = "./data/communes_ch4.geojson|layername=communes_ch4"

for model in MODELS:
    for year in YEARS_REGIONS:
        col = f"ch4_{model}_{year}"
        if col not in regions['features'][0]['properties']:
            continue
        lid = f"reg_{model}_{year}"
        name = f"{model.upper()} {year}"
        xml = vector_maplayer_xml(lid, name, regions_source, REG_FIELDS, col,
                                   breaks_reg[f"{model}_{year}"])
        LAYERS.append((lid, name, xml, 'vector'))

for model in MODELS:
    for year in YEARS_COMMUNES:
        col = f"ch4_{model}_{year}"
        if col not in communes['features'][0]['properties']:
            continue
        lid = f"com_{model}_{year}"
        name = f"{model.upper()} {year}"
        xml = vector_maplayer_xml(lid, name, communes_source, COM_FIELDS, col,
                                   breaks_com[f"{model}_{year}"])
        LAYERS.append((lid, name, xml, 'vector'))

# ────────── Arbre des couches ──────────
def tlayer(lid, name, visible, provider='ogr'):
    chk = "Qt::Checked" if visible else "Qt::Unchecked"
    return (f'<layer-tree-layer expanded="0" name="{xml_escape(name)}" id="{lid}" '
            f'checked="{chk}" providerKey="{provider}"><customproperties/></layer-tree-layer>')

def tgroup(name, children, expanded=True, checked=True):
    chk = "Qt::Checked" if checked else "Qt::Unchecked"
    exp = "1" if expanded else "0"
    return (f'<layer-tree-group expanded="{exp}" name="{xml_escape(name)}" checked="{chk}">'
            f'<customproperties/>{children}</layer-tree-group>')

# Régions
reg_fod_kids = "".join(
    tlayer(f"reg_fod_{y}", y, (y == "2024"))
    for y in YEARS_REGIONS if f"ch4_fod_{y}" in regions['features'][0]['properties']
)
reg_tno_kids = "".join(
    tlayer(f"reg_tno_{y}", y, False)
    for y in YEARS_REGIONS if f"ch4_tno_{y}" in regions['features'][0]['properties']
)
grp_reg = tgroup("Régions",
                 tgroup("FOD", reg_fod_kids, expanded=True) +
                 tgroup("TNO", reg_tno_kids, expanded=False))

# Communes
com_fod_kids = "".join(
    tlayer(f"com_fod_{y}", y, False)
    for y in YEARS_COMMUNES if f"ch4_fod_{y}" in communes['features'][0]['properties']
)
com_tno_kids = "".join(
    tlayer(f"com_tno_{y}", y, False)
    for y in YEARS_COMMUNES if f"ch4_tno_{y}" in communes['features'][0]['properties']
)
grp_com = tgroup("Communes",
                 tgroup("FOD", com_fod_kids, expanded=False) +
                 tgroup("TNO", com_tno_kids, expanded=False),
                 expanded=False)

# Fonds de carte
grp_bm = tgroup("Fonds de carte",
                tlayer("bm_satellite", "Satellite (Esri)", True, 'wms') +
                tlayer("bm_labels",    "Labels (Esri)",    True, 'wms') +
                tlayer("bm_osm",       "OpenStreetMap",    False, 'wms'))

LAYER_TREE = f'''<layer-tree-group>
  <customproperties/>
  {grp_reg}
  {grp_com}
  {grp_bm}
</layer-tree-group>'''

# Ordre de dessin : vecteurs au-dessus, raster (fond) en bas
vec_ids = [lid for lid, _, _, k in LAYERS if k == 'vector']
ras_ids = [lid for lid, _, _, k in LAYERS if k == 'raster']
LAYER_ORDER = "".join(f'<layer id="{i}"/>' for i in vec_ids + ras_ids)

PROJECTLAYERS = "".join(xml for _, _, xml, _ in LAYERS)

# ────────── Assemblage du fichier .qgs ──────────
QGS = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0-Prizren" projectname="CH4 Maroc" saveUser="" saveUserFull="" saveDateTime="">
  <homePath path=""/>
  <title>CH4 Maroc — Émissions de méthane par région et commune</title>
  <transaction mode="Disabled"/>
  <projectFlags set=""/>
  <autotransaction active="0"/>
  <evaluateDefaultValues active="0"/>
  <trust active="0"/>
  <projectCrs>
    {CRS_BLOCK}
  </projectCrs>
  {LAYER_TREE}
  <snapping-settings tolerance="12" unit="1" type="1" mode="2" intersection-snapping="0" enabled="0">
    <individual-layer-settings/>
  </snapping-settings>
  <relations/>
  <polymorphicRelations/>
  <mapcanvas name="theMapCanvas" annotationsVisible="1">
    <units>degrees</units>
    <extent>
      <xmin>-17.5</xmin><ymin>20.5</ymin><xmax>-1.0</xmax><ymax>36.0</ymax>
    </extent>
    <rotation>0</rotation>
    <destinationsrs>
      {CRS_BLOCK}
    </destinationsrs>
    <rendermaptile>0</rendermaptile>
    <expressionContextScope/>
  </mapcanvas>
  <projectModels/>
  <legend updateDrawingOrder="true"/>
  <mapViewDocks/>
  <mapViewDocks3D/>
  <main-annotation-layer type="annotation"/>
  <projectlayers>
    {PROJECTLAYERS}
  </projectlayers>
  <layerorder>
    {LAYER_ORDER}
  </layerorder>
  <properties>
    <Gui>
      <CanvasColorBluePart type="int">255</CanvasColorBluePart>
      <CanvasColorGreenPart type="int">255</CanvasColorGreenPart>
      <CanvasColorRedPart type="int">255</CanvasColorRedPart>
      <SelectionColorAlphaPart type="int">255</SelectionColorAlphaPart>
      <SelectionColorBluePart type="int">0</SelectionColorBluePart>
      <SelectionColorGreenPart type="int">255</SelectionColorGreenPart>
      <SelectionColorRedPart type="int">255</SelectionColorRedPart>
    </Gui>
    <Measure>
      <Ellipsoid type="QString">EPSG:7030</Ellipsoid>
    </Measure>
    <PAL>
      <CandidatesLine type="int">50</CandidatesLine>
      <CandidatesPolygon type="int">30</CandidatesPolygon>
      <DrawRectOnly type="bool">false</DrawRectOnly>
      <DrawUnplaced type="bool">false</DrawUnplaced>
      <SearchMethod type="int">0</SearchMethod>
      <ShowingAllLabels type="bool">false</ShowingAllLabels>
      <ShowingCandidates type="bool">false</ShowingCandidates>
      <ShowingShadowRects type="bool">false</ShowingShadowRects>
    </PAL>
  </properties>
  <visibility-presets/>
  <transformContext/>
  <projectMetadata>
    <identifier></identifier>
    <parentidentifier></parentidentifier>
    <language>FR</language>
    <type>dataset</type>
    <title>CH4 Maroc</title>
    <abstract>Émissions de méthane (CH4) par région et commune du Maroc — modèles FOD et TNO, années 1994 à 2040.</abstract>
    <links/>
    <author>CH4 Maroc — Géoportail national</author>
    <creation></creation>
  </projectMetadata>
  <Annotations/>
  <Layouts/>
  <Bookmarks/>
  <ProjectViewSettings UseProjectScales="0">
    <Scales/>
  </ProjectViewSettings>
  <ProjectDisplaySettings>
    <BearingFormat id="bearing">
      <Option type="Map">
        <Option name="decimal_separator" value="" type="QChar"/>
        <Option name="decimals" value="6" type="int"/>
      </Option>
    </BearingFormat>
  </ProjectDisplaySettings>
</qgis>
'''

with open(OUT / 'CH4_Maroc.qgs', 'w', encoding='utf-8') as f:
    f.write(QGS)

print(f"  Couches totales      : {len(LAYERS)} ({len(vec_ids)} vecteurs + {len(ras_ids)} fonds)")
print(f"  Projet écrit         : {OUT / 'CH4_Maroc.qgs'}")

# ────────── Script PyQGIS de secours ──────────
print("=" * 60)
print("== Étape 3/3 : génération du script de secours PyQGIS")
print("=" * 60)

LOADER = '''# -*- coding: utf-8 -*-
"""
PyQGIS — Script de secours pour reconstruire le projet CH4 Maroc.

À utiliser si CH4_Maroc.qgs ne s\\'ouvre pas correctement.

Étapes :
  1. Lancer QGIS
  2. Plugins -> Console Python (Ctrl+Alt+P)
  3. Bouton "Show Editor" -> Open Script -> sélectionner ce fichier
  4. Cliquer sur "Run Script" (flèche verte)
  5. Une fois chargé : Projet -> Enregistrer sous... -> CH4_Maroc.qgs
"""
from qgis.core import (QgsProject, QgsVectorLayer, QgsRasterLayer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsFillSymbol, QgsCoordinateReferenceSystem,
                       QgsRectangle, QgsLayerTreeGroup)
from qgis.utils import iface
from pathlib import Path
import json

HERE = Path(__file__).parent if "__file__" in dir() else Path.cwd()
DATA = HERE / "data"

PALETTE = ''' + json.dumps(PALETTE) + '''
MODELS = ''' + json.dumps(MODELS) + '''
YEARS_REGIONS = ''' + json.dumps(YEARS_REGIONS) + '''
YEARS_COMMUNES = ''' + json.dumps(YEARS_COMMUNES) + '''
BREAKS_REG = ''' + json.dumps(breaks_reg) + '''
BREAKS_COM = ''' + json.dumps(breaks_com) + '''

def make_renderer(attr, breaks):
    bounds = [0.0] + [float(b) for b in breaks] + [1e15]
    ranges = []
    for i in range(10):
        lo, hi = bounds[i], bounds[i+1]
        sym = QgsFillSymbol.createSimple({
            "color": PALETTE[i],
            "outline_color": "#ffffff",
            "outline_width": "0.2",
        })
        lbl = f"{lo:.0f} - {hi:.0f}" if i < 9 else f"> {bounds[9]:.0f}"
        ranges.append(QgsRendererRange(lo, hi, sym, lbl))
    return QgsGraduatedSymbolRenderer(attr, ranges)

project = QgsProject.instance()
project.clear()
project.setTitle("CH4 Maroc")
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
root = project.layerTreeRoot()

def add_vector(geojson, mode, model, year, group, visible=False):
    attr = f"ch4_{model}_{year}"
    layer = QgsVectorLayer(str(geojson), f"{model.upper()} {year}", "ogr")
    if not layer.isValid():
        print("!! Invalide :", geojson)
        return
    brks = (BREAKS_REG if mode == "regions" else BREAKS_COM).get(f"{model}_{year}")
    if brks:
        layer.setRenderer(make_renderer(attr, brks))
    project.addMapLayer(layer, False)
    node = group.addLayer(layer)
    node.setItemVisibilityChecked(visible)

g_reg = root.addGroup("Régions")
g_reg_fod = g_reg.addGroup("FOD")
g_reg_tno = g_reg.addGroup("TNO")
g_com = root.addGroup("Communes")
g_com_fod = g_com.addGroup("FOD")
g_com_tno = g_com.addGroup("TNO")
g_bm = root.addGroup("Fonds de carte")

for y in YEARS_REGIONS:
    if f"fod_{y}" in BREAKS_REG:
        add_vector(DATA / "regions_ch4.geojson", "regions", "fod", y, g_reg_fod, visible=(y=="2024"))
    if f"tno_{y}" in BREAKS_REG:
        add_vector(DATA / "regions_ch4.geojson", "regions", "tno", y, g_reg_tno)

for y in YEARS_COMMUNES:
    if f"fod_{y}" in BREAKS_COM:
        add_vector(DATA / "communes_ch4.geojson", "communes", "fod", y, g_com_fod)
    if f"tno_{y}" in BREAKS_COM:
        add_vector(DATA / "communes_ch4.geojson", "communes", "tno", y, g_com_tno)

SAT = "type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0"
LAB = "type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0"
OSM = "type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0"

for url, name, vis in [(SAT, "Satellite (Esri)", True),
                        (LAB, "Labels (Esri)", True),
                        (OSM, "OpenStreetMap", False)]:
    r = QgsRasterLayer(url, name, "wms")
    if r.isValid():
        project.addMapLayer(r, False)
        node = g_bm.addLayer(r)
        node.setItemVisibilityChecked(vis)
    else:
        print("!! Raster invalide :", name)

iface.mapCanvas().setExtent(QgsRectangle(-17.5, 20.5, -1.0, 36.0))
iface.mapCanvas().refresh()

print("OK — projet construit. Faites maintenant : Projet -> Enregistrer sous... -> CH4_Maroc.qgs")
'''

with open(OUT / 'load_in_qgis.py', 'w', encoding='utf-8') as f:
    f.write(LOADER)

print(f"  Script PyQGIS écrit  : {OUT / 'load_in_qgis.py'}")

# ────────── README ──────────
README = '''# Projet QGIS — CH4 Maroc

Projet QGIS auto-généré pour la cartographie thématique des émissions de méthane (CH4)
au Maroc, modèles FOD et TNO, années 1994 à 2040.

## Contenu

```
qgis_project/
├── CH4_Maroc.qgs              Projet QGIS (ouvrir avec QGIS 3.x)
├── data/
│   ├── regions_ch4.geojson    12 régions, 1 colonne par (modèle, année)
│   └── communes_ch4.geojson   1541 communes, 1 colonne par (modèle, année)
├── load_in_qgis.py            Script PyQGIS de secours
└── README.md                  Ce fichier
```

## Utilisation rapide

1. **Ouvrir QGIS 3.x** (3.22 ou ultérieur recommandé)
2. **Projet -> Ouvrir** -> sélectionner `CH4_Maroc.qgs`
3. Le projet charge :
   - 12 fonds de carte (Satellite + Labels actifs par défaut)
   - 42 couches Régions (21 années x 2 modèles)
   - 8 couches Communes (4 années x 2 modèles)
4. Toutes les couches sont cochées/décochées dans le panneau des couches
5. Par défaut, seule la couche **Régions > FOD > 2024** est visible

## Symbologie

- **Palette** : YlOrRd 10 classes (jaune pâle -> rouge sombre)
- **Méthode** : Ruptures par quantiles (déciles 10%, 20%, ..., 90%)
- **Identique** au rendu de la carte web interactive

## Habillage (Mise en page)

1. **Projet -> Nouvelle mise en page** -> nommer (ex. "CH4_FOD_2024")
2. Dans le composeur :
   - **Ajouter une carte** (rectangle)
   - **Ajouter une légende** (filtrer pour ne garder que la couche active)
   - **Ajouter une barre d échelle** (km)
   - **Ajouter une flèche Nord**
   - **Ajouter un titre** (étiquette)
3. **Mise en page -> Exporter au format PDF / PNG / SVG**

## Atlas (cartes en série)

Pour générer automatiquement 1 carte par année :
1. Créer une couche "couverture" listant les années
2. Mise en page -> Atlas -> activer + lier à la couverture
3. La carte d emprise change pour chaque année

## Script de secours

Si `CH4_Maroc.qgs` ne s ouvre pas (version QGIS différente, etc.) :

1. Lancer QGIS, créer un nouveau projet vide
2. Plugins -> Console Python (Ctrl+Alt+P)
3. Bouton **Show Editor** -> **Open Script** -> `load_in_qgis.py`
4. Bouton **Run Script** (flèche verte)
5. **Projet -> Enregistrer sous** -> `CH4_Maroc.qgs`

## Régénérer

Si les fichiers de données sources changent :

```bash
python build_qgis_project.py
```

## SCR

- Projet : **EPSG:4326** (WGS 84)
- Pour le Maroc, reprojeter en EPSG:26191 (Merchich Nord Maroc) si vous voulez
  travailler en mètres : clic droit sur couche -> Exporter -> Enregistrer sous
'''

with open(OUT / 'README.md', 'w', encoding='utf-8') as f:
    f.write(README)

print(f"  README écrit         : {OUT / 'README.md'}")

print("=" * 60)
print(f"OK — Projet généré dans {OUT}")
print("Ouvre maintenant CH4_Maroc.qgs dans QGIS.")
print("=" * 60)
