"use strict";

/* ═══════════════════════════════════════════════════════════════
   COMMUN — Thème, Langue, Recherche, Compteurs
   Inclus sur toutes les pages (accueil, donnees, statistiques, articles)
═══════════════════════════════════════════════════════════════ */

/* ── Active link selon la page courante ── */
(function highlightActiveNav() {
  const path = (location.pathname.split('/').pop() || 'accueil.html').toLowerCase();
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = (a.getAttribute('href') || '').toLowerCase();
    if (href === path) a.classList.add('active');
    else a.classList.remove('active');
  });
})();

/* ── Compteurs animés (s'il y en a sur la page) ── */
(function initCounters() {
  const counters = document.querySelectorAll('.counter');
  if (!counters.length) return;
  const cntObs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.target, 10);
      const suffix = '';
      let cur = 0;
      const step = Math.ceil(target / 60);
      const t = setInterval(() => {
        cur = Math.min(cur + step, target);
        el.textContent = cur.toLocaleString('fr-FR') + suffix;
        if (cur >= target) clearInterval(t);
      }, 20);
      cntObs.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(c => cntObs.observe(c));
})();

/* ═══════════════════════════════════════════════════════════════
   RECHERCHE GLOBALE (barre navbar)
═══════════════════════════════════════════════════════════════ */
const SEARCH_ITEMS = [];
function rebuildSearchItems(lang) {
  SEARCH_ITEMS.length = 0;
  const items = lang === 'fr' ? [
    { label:'Carte interactive',       icon:'fa-map-marked-alt', href:'carte_interactive.html',                    group:'Pages' },
    { label:'Statistiques CH4',        icon:'fa-chart-line',     href:'statistiques.html',                          group:'Pages' },
    { label:'Données disponibles',     icon:'fa-database',       href:'donnees.html',                               group:'Pages' },
    { label:'Articles scientifiques',  icon:'fa-book-open',      href:'articles.html',                              group:'Pages' },
    { label:'Comment ça marche',       icon:'fa-route',          href:'accueil.html#how-it-works',                  group:'Sections' },
    { label:'À propos du projet',      icon:'fa-info-circle',    href:'accueil.html#about',                         group:'Sections' },
    { label:'Modèle FOD',              icon:'fa-flask',          href:'carte_interactive.html?model=fod',           group:'Modèles' },
    { label:'Modèle TNO',              icon:'fa-vial',           href:'carte_interactive.html?model=tno',           group:'Modèles' },
    { label:'Données 1994',            icon:'fa-calendar',       href:'carte_interactive.html?year=1994',           group:'Années' },
    { label:'Données 2004',            icon:'fa-calendar',       href:'carte_interactive.html?year=2004',           group:'Années' },
    { label:'Données 2014',            icon:'fa-calendar',       href:'carte_interactive.html?year=2014',           group:'Années' },
    { label:'Données 2024',            icon:'fa-calendar',       href:'carte_interactive.html?year=2024',           group:'Années' },
  ] : [
    { label:'Interactive map',         icon:'fa-map-marked-alt', href:'carte_interactive.html',                    group:'Pages' },
    { label:'CH4 Statistics',          icon:'fa-chart-line',     href:'statistiques.html',                          group:'Pages' },
    { label:'Available data',          icon:'fa-database',       href:'donnees.html',                               group:'Pages' },
    { label:'Scientific articles',     icon:'fa-book-open',      href:'articles.html',                              group:'Pages' },
    { label:'How it works',            icon:'fa-route',          href:'accueil.html#how-it-works',                  group:'Sections' },
    { label:'About the project',       icon:'fa-info-circle',    href:'accueil.html#about',                         group:'Sections' },
    { label:'FOD model',               icon:'fa-flask',          href:'carte_interactive.html?model=fod',           group:'Models' },
    { label:'TNO model',               icon:'fa-vial',           href:'carte_interactive.html?model=tno',           group:'Models' },
    { label:'1994 data',               icon:'fa-calendar',       href:'carte_interactive.html?year=1994',           group:'Years' },
    { label:'2004 data',               icon:'fa-calendar',       href:'carte_interactive.html?year=2004',           group:'Years' },
    { label:'2014 data',               icon:'fa-calendar',       href:'carte_interactive.html?year=2014',           group:'Years' },
    { label:'2024 data',               icon:'fa-calendar',       href:'carte_interactive.html?year=2024',           group:'Years' },
  ];
  items.forEach(i => SEARCH_ITEMS.push(i));
}

(function initGlobalSearch() {
  const gsInput    = document.getElementById('globalSearch');
  const gsDropdown = document.getElementById('searchDropdown');
  if (!gsInput || !gsDropdown) return;

  function render(q) {
    gsDropdown.innerHTML = '';
    if (!q || q.length < 2) { gsDropdown.classList.remove('visible'); return; }
    const qn = q.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    const hits = SEARCH_ITEMS.filter(it =>
      it.label.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').includes(qn) ||
      it.group.toLowerCase().includes(qn)
    ).slice(0, 8);

    if (!hits.length) {
      gsDropdown.innerHTML = `<div style="padding:14px 16px;color:var(--muted);font-size:.85rem;">Aucun résultat pour "<b>${q}</b>"</div>`;
      gsDropdown.classList.add('visible');
      return;
    }
    let lastGroup = '';
    hits.forEach(item => {
      if (item.group !== lastGroup) {
        lastGroup = item.group;
        const g = document.createElement('div');
        g.className = 'search-result-group';
        g.textContent = item.group;
        gsDropdown.appendChild(g);
      }
      const a = document.createElement('a');
      a.className = 'search-result-item';
      a.href = item.href;
      a.innerHTML = `<i class="fas ${item.icon}"></i> ${item.label}`;
      gsDropdown.appendChild(a);
    });
    gsDropdown.classList.add('visible');
  }

  gsInput.addEventListener('input',  () => render(gsInput.value.trim()));
  gsInput.addEventListener('focus',  () => { if (gsInput.value.trim().length >= 2) gsDropdown.classList.add('visible'); });
  gsInput.addEventListener('blur',   () => setTimeout(() => gsDropdown.classList.remove('visible'), 180));
  gsInput.addEventListener('keydown', e => {
    if (e.key === 'Escape') { gsDropdown.classList.remove('visible'); gsInput.blur(); }
  });
})();

/* ═══════════════════════════════════════════════════════════════
   SYSTÈME DE TRADUCTION FR / EN
═══════════════════════════════════════════════════════════════ */
const T = {
  /* Brand & nav */
  'brand.tagline':      { fr:"Géoportail national de qualité de l'air", en:'National air quality geoportal' },
  'nav.accueil':        { fr:'Accueil',        en:'Home' },
  'nav.carte':          { fr:'Carte',          en:'Map' },
  'nav.stats':          { fr:'Statistiques',   en:'Statistics' },
  'nav.donnees':        { fr:'Données',        en:'Data' },
  'nav.articles':       { fr:'Articles',       en:'Articles' },
  'nav.assistant':      { fr:'Assistant IA',   en:'AI Assistant' },
  'nav.about':          { fr:'À propos',       en:'About' },

  /* ── Carte interactive ── */
  'brand.tagline.short':{ fr:'Géoportail national',                          en:'National geoportal' },
  'carte.search.ph':    { fr:'Rechercher une région ou une commune...',      en:'Search for a region or commune...' },
  'carte.sidebar.title':{ fr:'Cartographie CH₄ Maroc',                       en:'CH₄ Morocco Mapping' },
  'carte.sidebar.sub':  { fr:'Émissions de méthane issues des déchets ménagers', en:'Methane emissions from municipal waste' },
  'carte.section.display':   { fr:'Affichage',          en:'Display' },
  'carte.section.params':    { fr:'Paramètres',         en:'Parameters' },
  'carte.section.anim':      { fr:'Animation temporelle', en:'Time animation' },
  'carte.section.filter':    { fr:'Filtre par seuil CH₄', en:'CH₄ threshold filter' },
  'carte.section.overlays':  { fr:'Couches additionnelles', en:'Additional layers' },
  'carte.mode.regions':  { fr:'Régions',  en:'Regions' },
  'carte.mode.communes': { fr:'Communes', en:'Communes' },
  'carte.label.model':   { fr:'Modèle', en:'Model' },
  'carte.label.year':    { fr:'Année',  en:'Year' },
  'carte.anim.slow':     { fr:'Lent',    en:'Slow' },
  'carte.anim.normal':   { fr:'Normal',  en:'Normal' },
  'carte.anim.fast':     { fr:'Rapide',  en:'Fast' },
  'carte.filter.label':  { fr:'Seuil :', en:'Threshold:' },
  'carte.filter.info':   { fr:'Toutes les zones affichées', en:'All areas displayed' },
  'carte.overlay.communes':  { fr:'Communes (Maroc)',  en:'Communes (Morocco)' },
  'carte.overlay.emissions': { fr:'Émissions CH₄',      en:'CH₄ Emissions' },
  'carte.overlay.dechets':   { fr:'Sites de déchets',   en:'Waste sites' },
  'carte.action.refresh':    { fr:'Actualiser', en:'Refresh' },
  'carte.action.compare':    { fr:'Comparer',   en:'Compare' },
  'carte.action.swipe':      { fr:'Swipe',      en:'Swipe' },
  'carte.action.export':     { fr:'Exporter',   en:'Export' },
  'carte.section.impact':    { fr:'Impact climat', en:'Climate impact' },
  'carte.impact.note':       { fr:'Total national · PRG 100 ans = 28 (GIEC AR6)', en:'National total · 100-yr GWP = 28 (IPCC AR6)' },
  'carte.popup.equiv':       { fr:'Équivalent climat',    en:'Climate equivalent' },
  'carte.popup.co2eq':       { fr:'CO₂eq',                en:'CO₂eq' },
  'carte.popup.cars':        { fr:'voitures/an',          en:'cars/yr' },
  'carte.popup.flights':     { fr:'vols Casa→Paris',      en:'flights CMN→CDG' },
  'carte.popup.trees':       { fr:'arbres à planter',     en:'trees to plant' },
  'carte.tooltip.zoomin':    { fr:'Zoom avant', en:'Zoom in' },
  'carte.tooltip.zoomout':   { fr:'Zoom arrière', en:'Zoom out' },
  'carte.tooltip.drag':      { fr:'Activer/désactiver le déplacement', en:'Toggle pan' },
  'carte.tooltip.info':      { fr:'Info méthane / CH₄', en:'Methane / CH₄ info' },
  'carte.tooltip.satellite': { fr:'Données satellitaires', en:'Satellite imagery' },
  'carte.tooltip.opacity':   { fr:'Opacité des couches',   en:'Layer opacity' },
  'carte.tooltip.home':      { fr:'Centrer sur le Maroc',  en:'Center on Morocco' },
  'carte.tooltip.style':     { fr:'Cartographie',          en:'Map style' },
  'carte.tooltip.grid':      { fr:'Zones à risque',        en:'Risk zones' },
  'carte.tooltip.share':     { fr:'Partager la vue',       en:'Share view' },
  'carte.cmp.title':         { fr:'Comparaison FOD vs TNO', en:'FOD vs TNO comparison' },
  'carte.cmp.close':         { fr:'Fermer',                 en:'Close' },
  'carte.cmp.legend':        { fr:'Faible → Élevé (t/an)',  en:'Low → High (t/yr)' },
  'carte.coord.position':    { fr:'Position',               en:'Position' },
  'carte.legend.unit':       { fr:'t/an',                   en:'t/yr' },
  'carte.share.copied':      { fr:'Lien copié !',           en:'Link copied!' },
  'carte.opacity.label':     { fr:'OPACITÉ',                en:'OPACITY' },
  'search.placeholder': { fr:'Recherche de sections, articles, régions…', en:'Search sections, articles, regions…' },
  'art.search.ph':      { fr:'Rechercher titre, auteur, revue…',          en:'Search title, author, journal…' },
  /* Sub menu */
  'sub.donnees':        { fr:'Données',         en:'Data' },
  'sub.fod':            { fr:'Modèle FOD',      en:'FOD Model' },
  'sub.tno':            { fr:'Modèle TNO',      en:'TNO Model' },
  'sub.analyse':        { fr:'Analyse',         en:'Analysis' },
  'sub.tendances':      { fr:'Tendances 2024',  en:'Trends 2024' },
  'sub.publications':   { fr:'Publications',    en:'Publications' },
  'sub.apropos':        { fr:'À propos',        en:'About' },
  /* Hero (accueil) */
  'partners.label': { fr:"Sous l'égide de", en:'Under the aegis of' },
  'hero.badge':   { fr:"Portail officiel de suivi de la qualité de l'air et des émissions CH4",
                    en:'Official portal for air quality monitoring and CH4 emissions' },
  'hero.h1':      { fr:'Bienvenue sur le géoportail <span class="accent">CH4 MAROC</span>',
                    en:'Welcome to the geoportal <span class="accent">CH4 MAROC</span>' },
  'hero.p1':      { fr:"CH4 MAROC met à disposition des données géospatiales nationales et régionales dédiées aux émissions de méthane, à l'air et aux ressources naturelles. Découvrez une interface intuitive pour consulter des couches SIG, explorer des analyses thématiques et suivre l'évolution des émissions par région et commune.",
                    en:'CH4 MAROC provides national and regional geospatial data dedicated to methane emissions, air quality and natural resources. Discover an intuitive interface to browse GIS layers, explore thematic analyses and track emission trends by region and commune.' },
  'hero.p2':      { fr:"Notre plateforme réunit des ressources cartographiques, des outils d'analyse et des visualisations interactives pour les décideurs, les chercheurs et les acteurs territoriaux. Accédez à des cartes, rapports, publications et commentaires communautaires dans un environnement sécurisé et professionnel.",
                    en:'Our platform brings together mapping resources, analysis tools and interactive visualisations for decision-makers, researchers and territorial stakeholders. Access maps, reports, publications and community comments in a secure and professional environment.' },
  'cta.map':      { fr:'<i class="fas fa-map-marked-alt"></i> Accéder à la carte interactive', en:'<i class="fas fa-map-marked-alt"></i> Open the interactive map' },
  'cta.how':      { fr:'<i class="fas fa-info-circle"></i> Comment ça marche',                 en:'<i class="fas fa-info-circle"></i> How it works' },
  /* Stats */
  'stat.communes': { fr:'Communes analysées',   en:'Analysed communes' },
  'stat.regions':  { fr:'Régions couvertes',    en:'Covered regions' },
  'stat.years':    { fr:'Années de données',    en:'Data years' },
  'stat.models':   { fr:'Modèles intégrés',     en:'Integrated models' },
  /* Cards */
  'pubs.title':       { fr:'Dernières Publications',   en:'Latest Publications' },
  'pubs.viewall':     { fr:'Voir tout',                en:'View all' },
  'comments.title':   { fr:'Derniers Commentaires',    en:'Latest Comments' },
  'comments.filter':  { fr:'Filtrer',                  en:'Filter' },
  /* How */
  'how.title':   { fr:'<i class="fas fa-route"></i> Comment ça marche', en:'<i class="fas fa-route"></i> How it works' },
  'how.sub':     { fr:'En trois étapes simples, explorez et analysez les émissions de méthane sur le territoire marocain.',
                   en:'In three simple steps, explore and analyse methane emissions across Moroccan territory.' },
  'how.s1.title':{ fr:'Choisir vos paramètres',      en:'Choose your parameters' },
  'how.s1.desc': { fr:"Sélectionnez le modèle (FOD ou TNO), l'année (1994–2024) et le niveau d'affichage (régions ou communes) depuis le panneau latéral.",
                   en:'Select the model (FOD or TNO), the year (1994–2024) and the display level (regions or communes) from the side panel.' },
  'how.s2.title':{ fr:'Explorer la carte',           en:'Explore the map' },
  'how.s2.desc': { fr:"Naviguez sur la carte interactive, cliquez sur une zone pour afficher ses émissions CH4, utilisez la recherche ou lancez l'animation temporelle.",
                   en:'Navigate the interactive map, click on any zone to display its CH4 emissions, use the search bar or launch the temporal animation.' },
  'how.s3.title':{ fr:'Exporter vos données',        en:'Export your data' },
  'how.s3.desc': { fr:'Téléchargez les résultats en CSV, GeoJSON, PNG ou PDF. Partagez votre vue via un lien URL généré automatiquement.',
                   en:'Download results as CSV, GeoJSON, PNG or PDF. Share your view via an automatically generated URL.' },
  'how.cta':     { fr:'<i class="fas fa-play"></i> Commencer maintenant',  en:'<i class="fas fa-play"></i> Get started' },
  /* About */
  'about.badge': { fr:'<i class="fas fa-graduation-cap"></i> Projet de Fin d\'Études', en:'<i class="fas fa-graduation-cap"></i> Final Year Project' },
  'about.title': { fr:'À propos du projet', en:'About the project' },
  'about.p1':    { fr:"Ce géoportail a été développé dans le cadre d'un <strong>Projet de Fin d'Études (PFE)</strong> en Sciences de l'Information Géographique. Il vise à cartographier et analyser les émissions de méthane (CH4) issues des déchets ménagers solides au Maroc sur la période 1994–2024.",
                   en:'This geoportal was developed as part of a <strong>Final Year Project (FYP)</strong> in Geographic Information Science. It aims to map and analyse methane (CH4) emissions from municipal solid waste in Morocco over the period 1994–2024.' },
  'about.p2':    { fr:"Deux modèles d'estimation sont intégrés : le modèle <strong>FOD</strong> (First Order Decay, IPCC 2006) et le modèle <strong>TNO</strong>, appliqués à l'échelle des régions et des communes marocaines.",
                   en:'Two estimation models are integrated: the <strong>FOD</strong> model (First Order Decay, IPCC 2006) and the <strong>TNO</strong> model, applied at the scale of Moroccan regions and communes.' },
  'about.tag1':  { fr:'<i class="fas fa-map"></i> SIG & Cartographie',       en:'<i class="fas fa-map"></i> GIS & Mapping' },
  'about.tag2':  { fr:'<i class="fas fa-smog"></i> Émissions CH4',           en:'<i class="fas fa-smog"></i> CH4 Emissions' },
  'about.tag3':  { fr:'<i class="fas fa-trash"></i> Déchets ménagers',       en:'<i class="fas fa-trash"></i> Municipal waste' },
  'about.tag4':  { fr:'<i class="fas fa-globe-africa"></i> Maroc',           en:'<i class="fas fa-globe-africa"></i> Morocco' },
  'team.student.name': { fr:'Étudiant(e)', en:'Student' },
  'team.student.role': { fr:'Ingénieur en Sciences Géomatiques et Ingénierie Topographique', en:'Engineer in Geomatics Science and Topographic Engineering' },
  'team.student.year': { fr:"Projet de Fin d'Études — 2026", en:'Final Year Project — 2026' },
  'team.sup.title':    { fr:'Encadrant(e)', en:'Supervisor' },
  'team.sup.desc':     { fr:'Directeur / Directrice de recherche', en:'Research Director' },
  'team.sup.dept':     { fr:'Université — Département SIG', en:'University — GIS Department' },
  'tech.label':        { fr:'Technologies utilisées', en:'Technologies used' },
  /* Charts page */
  'charts.title':       { fr:'<i class="fas fa-chart-line"></i> Statistiques des émissions CH4',  en:'<i class="fas fa-chart-line"></i> CH4 Emission Statistics' },
  'charts.sub':         { fr:'Visualisation interactive des émissions de méthane par région et par année (données réelles)',
                          en:'Interactive visualisation of methane emissions by region and year (real data)' },
  'charts.tab.regions': { fr:'Par région',  en:'By region' },
  'charts.tab.evo':     { fr:'Évolution',   en:'Evolution' },
  'charts.cta':         { fr:'<i class="fas fa-map-marked-alt"></i> Explorer sur la carte interactive', en:'<i class="fas fa-map-marked-alt"></i> Explore on the interactive map' },
  /* Datasets page */
  'data.title': { fr:'<i class="fas fa-database"></i> Données disponibles',  en:'<i class="fas fa-database"></i> Available data' },
  'data.sub':   { fr:'Jeux de données CH4 couvrant 4 décennies, 2 modèles, 16 régions et 1 538 communes du Maroc',
                  en:'CH4 datasets covering 4 decades, 2 models, 16 regions and 1,538 communes of Morocco' },
  'ds1.name':   { fr:'Régions — Modèle FOD',     en:'Regions — FOD Model' },
  'ds1.desc':   { fr:'Émissions CH4 par région administrative (16 régions) via le modèle First Order Decay',
                  en:'CH4 emissions by administrative region (16 regions) via the First Order Decay model' },
  'ds2.name':   { fr:'Communes — Modèle FOD',    en:'Communes — FOD Model' },
  'ds2.desc':   { fr:'Émissions CH4 pour les 1 538 communes marocaines, estimées par le modèle FOD-IPCC 2006',
                  en:'CH4 emissions for the 1,538 Moroccan communes, estimated by the FOD-IPCC 2006 model' },
  'ds3.name':   { fr:'Régions — Modèle TNO',     en:'Regions — TNO Model' },
  'ds3.desc':   { fr:'Estimations CH4 par région selon le modèle TNO, comparables aux données FOD',
                  en:'CH4 estimates by region according to the TNO model, comparable to FOD data' },
  'ds4.name':   { fr:'Communes — Modèle TNO',    en:'Communes — TNO Model' },
  'ds4.desc':   { fr:'Estimations CH4 communales par le modèle TNO pour les 4 périodes clés',
                  en:'Communal CH4 estimates by the TNO model for the 4 key periods' },
  'ds.btn':     { fr:'<i class="fas fa-eye"></i> Visualiser',  en:'<i class="fas fa-eye"></i> View' },
  /* Articles */
  'art.title':  { fr:'<i class="fas fa-book-open"></i> Articles scientifiques',  en:'<i class="fas fa-book-open"></i> Scientific articles' },
  'art.sub':    { fr:'Références bibliographiques sur les émissions CH4 issues des déchets solides municipaux',
                  en:'Bibliographic references on CH4 emissions from municipal solid waste' },
  'art.more':   { fr:'<i class="fas fa-search"></i> Voir plus sur Google Scholar',  en:'<i class="fas fa-search"></i> View more on Google Scholar' },
  /* Footer */
  'footer.brand.desc':    { fr:'Géoportail national de cartographie des émissions de méthane issues des déchets ménagers solides au Maroc.',
                            en:'National geoportal for mapping methane emissions from municipal solid waste in Morocco.' },
  'footer.nav.title':     { fr:'Navigation',          en:'Navigation' },
  'footer.src.title':     { fr:'Sources de données',  en:'Data sources' },
  'footer.contact.title': { fr:'Contact',             en:'Contact' },
  'footer.badge':         { fr:'<i class="fas fa-shield-alt"></i> Données à usage académique',  en:'<i class="fas fa-shield-alt"></i> Academic use data' },
  'footer.bot.left':      { fr:'© 2026 CH4 MAROC — Projet de Fin d\'Études. Tous droits réservés.',  en:'© 2026 CH4 MAROC — Final Year Project. All rights reserved.' },
  'footer.bot.right':     { fr:'Développé avec <i class="fas fa-heart" style="color:#ff5c35;"></i> — Leaflet · GeoJSON · IPCC FOD/TNO',
                            en:'Built with <i class="fas fa-heart" style="color:#ff5c35;"></i> — Leaflet · GeoJSON · IPCC FOD/TNO' },
};

let currentLang = localStorage.getItem('ch4lang') || 'fr';

function setLang(lang) {
  currentLang = lang;
  try { localStorage.setItem('ch4lang', lang); } catch(e) {}
  document.documentElement.lang = lang;

  // Titre de page : ne remplace QUE si la page a opté avec data-i18n-title sur <html>
  const titleKey = document.documentElement.dataset.i18nTitle;
  if (titleKey && T[titleKey] && T[titleKey][lang]) {
    document.title = T[titleKey][lang];
  }

  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.dataset.lang === lang));

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (T[key] && T[key][lang] !== undefined) el.innerHTML = T[key][lang];
  });

  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.dataset.i18nPh;
    if (T[key] && T[key][lang] !== undefined) el.placeholder = T[key][lang];
  });

  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.dataset.i18nTitle;
    if (T[key] && T[key][lang] !== undefined) el.setAttribute('title', T[key][lang]);
  });

  /* Hook page-spécifique éventuel (charts, etc.) */
  if (typeof window.onLangChange === 'function') window.onLangChange(lang);

  rebuildSearchItems(lang);
}

/* Helper exposé pour traductions JS-side (popups, alerts dynamiques) */
window.t = function(key, fallback) {
  const lang = currentLang || 'fr';
  if (T[key] && T[key][lang] != null) return T[key][lang];
  return fallback != null ? fallback : key;
};
window.getCurrentLang = function() { return currentLang; };

document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => setLang(btn.dataset.lang));
});

setLang(currentLang);

/* ═══════════════════════════════════════════════════════════════
   BASCULE THÈME CLAIR / SOMBRE
═══════════════════════════════════════════════════════════════ */
(function initThemeToggle() {
  const btn = document.getElementById('themeToggle');
  if (!btn) return;
  const icon = btn.querySelector('i');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('ch4theme', theme); } catch(e) {}
    if (icon) icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    btn.setAttribute('aria-label', theme === 'light' ? 'Activer le mode sombre' : 'Activer le mode clair');
    btn.setAttribute('title',      theme === 'light' ? 'Mode sombre' : 'Mode clair');

    /* Hook page-spécifique éventuel (rebuild charts) */
    if (typeof window.onThemeChange === 'function') window.onThemeChange(theme);
  }

  const initial = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(initial);

  btn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });
})();
