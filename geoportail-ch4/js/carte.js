// Initialisation de la carte Leaflet
const map = L.map('map').setView([31.5, -7.5], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Chargement des données GeoJSON
fetch('data/communes_maroc.geojson')
  .then(response => response.json())
  .then(data => {
    L.geoJSON(data, {
      style: { color: '#1f78b4', weight: 1, fillOpacity: 0.4 }
    }).addTo(map);
  })
  .catch(error => console.error('Erreur chargement GeoJSON:', error));
