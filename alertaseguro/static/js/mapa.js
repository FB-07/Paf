document.addEventListener("DOMContentLoaded", () => {
  const mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined") return;

  // Mapa principal
  var map = L.map("map").setView([39.9, -8.0], 7);

  var OpenStreetMap_Mapnik = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  });
  OpenStreetMap_Mapnik.addTo(map);

  // API_Incidentes
  fetch("/api/incidentes/")
    .then((resp) => resp.json())
    .then((lista) => {
      lista.forEach((inc) => {
        L.marker([inc.latitude, inc.longitude])
          .addTo(map)
          .bindPopup(`<b>${inc.titulo}</b><br>${inc.descricao}`);
      });
    });

  // Camada dos municípios
  var municipiosLayer = L.geoJSON(null, {
    style: function (feature) {
      return {
        weight: 1,
        color: "#555",
        fillColor: feature.properties.cor || "#cccccc",
        fillOpacity: 0.7,
      };
    },
  });

  if (window.MUNICIPIOS_URL) {
    fetch(window.MUNICIPIOS_URL)
      .then((resp) => resp.json())
      .then((data) => {
        data.features.forEach((f) => (f.properties.cor = "#cccccc"));
        municipiosLayer.addData(data);
      });
  }

  // Checkbox municípios
  const checkboxMu = document.getElementById("toggleMunicipios");
  if (checkboxMu) {
    checkboxMu.addEventListener("change", () => {
      if (checkboxMu.checked) municipiosLayer.addTo(map);
      else map.removeLayer(municipiosLayer);
    });
  }

  // Cores risco de incêndio
  const cores_risco = { 1: "#00ff00", 2: "#a6ff00", 3: "#f1c40f", 4: "#e67e22", 5: "#a50000" };

  // Checkbox risco de incêndio hoje
  let municipiosData0 = null;

  if (window.MUNICIPIOS_URL) {
    fetch(window.MUNICIPIOS_URL)
      .then((r) => r.json())
      .then((data) => { municipiosData0 = data; });
  }

  var riscoHojeLayer = L.geoJSON(null, {
    style: (f) => ({
      weight: 1,
      color: "#555",
      fillColor: f.properties.cor || "#cccccc",
      fillOpacity: 0.7,
    }),
  });

  const checkboxRisco0 = document.getElementById("toggleRisco0");
  if (checkboxRisco0) {
    checkboxRisco0.addEventListener("change", () => {
      if (!checkboxRisco0.checked) {
        map.removeLayer(riscoHojeLayer);
        return;
      }

      fetch("/api/rcm_hoje/")
        .then((r) => r.json())
        .then((rcmDict) => {
          if (!municipiosData0) return;
          const geo = structuredClone(municipiosData0);

          geo.features.forEach((f) => {
            const dico = String(f.properties.DICO).padStart(4, "0");
            const rcm = rcmDict[dico];
            f.properties.cor = cores_risco[rcm] || "#cccccc";
          });

          riscoHojeLayer.clearLayers();
          riscoHojeLayer.addData(geo);
          riscoHojeLayer.addTo(map);
        });
    });
  }

  // Checkbox risco de incêndio amanhã
  let municipiosData1 = null;

  if (window.MUNICIPIOS_URL) {
    fetch(window.MUNICIPIOS_URL)
      .then((r) => r.json())
      .then((data) => { municipiosData1 = data; });
  }

  var riscoAmanhaLayer = L.geoJSON(null, {
    style: (f) => ({
      weight: 1,
      color: "#555",
      fillColor: f.properties.cor || "#cccccc",
      fillOpacity: 0.7,
    }),
  });

  const checkboxRisco1 = document.getElementById("toggleRisco1");
  if (checkboxRisco1) {
    checkboxRisco1.addEventListener("change", () => {
      if (!checkboxRisco1.checked) {
        map.removeLayer(riscoAmanhaLayer);
        return;
      }

      fetch("/api/rcm_amanha/")
        .then((r) => r.json())
        .then((rcmDict) => {
          if (!municipiosData1) return;
          const geo = structuredClone(municipiosData1);

          geo.features.forEach((f) => {
            const dico = String(f.properties.DICO).padStart(4, "0");
            const rcm = rcmDict[dico];
            f.properties.cor = cores_risco[rcm] || "#cccccc";
          });

          riscoAmanhaLayer.clearLayers();
          riscoAmanhaLayer.addData(geo);
          riscoAmanhaLayer.addTo(map);
        });
    });
  }
});
