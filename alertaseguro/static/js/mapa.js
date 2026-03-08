document.addEventListener("DOMContentLoaded", () => {
  const mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined") return;

  // ==========================
  // Mapa principal
  // ==========================
  const map = L.map("map", {
    zoomSnap: 0.25,
    zoomDelta: 0.25 
  }).setView([39.9, -8.0], 7.25);
  
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // ==========================
  // Camada de incidentes
  // ==========================
  const incidentesLayer = L.layerGroup().addTo(map);

  function renderIncidentes(data) {
    incidentesLayer.clearLayers();

    data.forEach((inc) => {
      const lat = Number(inc.latitude);
      const lon = Number(inc.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      const marker = L.circleMarker([lat, lon], {
        radius: 8.5,
        weight: 1,
        fillOpacity: 0.85,
        color: inc.status_color || "#333",
        fillColor: inc.status_color || "#333",
      });

      const titulo = inc.natureza || "Incidente";
      const local = [inc.location_name, inc.parish, inc.county, inc.district].filter(Boolean).join(", ");
      const estado = inc.status || "";
      const updated = inc.updated_at_api || "";

      marker.on("click", () => {
        const html = `
          <b class="text-lg">${titulo}</b><br><br>
          ${estado ? "<b>Estado:</b> " + estado + "<br>" : ""}
          ${local ? "<b>Local:</b> " + local + "<br>" : ""}
          ${updated ? "<b>Atualizado:</b> " + updated + "<br>" : ""}
          <br>
          <small>ID: ${inc.api_id}</small>
        `;
        window.openIncidentPanel(html);
      });

      incidentesLayer.addLayer(marker);
    });
  }

  async function loadIncidentes() {
    try {
      const res = await fetch("/api/incidentes/");
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      console.log("Incidentes recebidos:", data.length);
      renderIncidentes(data);
    } catch (err) {
      console.error("Erro a carregar incidentes:", err);
    }
  }

  loadIncidentes();
  setInterval(loadIncidentes, 60000);

  // ==========================
  // Camada municípios
  // ==========================
  const municipiosLayer = L.geoJSON(null, {
    style: (feature) => ({
      weight: 1,
      color: "#555",
      fillColor: feature.properties.cor || "#cccccc",
      fillOpacity: 0.7,
    }),
  });

  let municipiosData = null;
  if (window.MUNICIPIOS_URL) {
    fetch(window.MUNICIPIOS_URL)
      .then((r) => r.json())
      .then((data) => {
        municipiosData = data;
        data.features.forEach((f) => (f.properties.cor = "#cccccc"));
        municipiosLayer.addData(data);
      });
  }

  const checkboxMu = document.getElementById("toggleMunicipios");
  if (checkboxMu) {
    checkboxMu.addEventListener("change", () => {
      if (checkboxMu.checked) map.addLayer(municipiosLayer);
      else map.removeLayer(municipiosLayer);
    });
  }

  // ==========================
  // Cores risco incêndio
  // ==========================
  const cores_risco = { 1: "#00ff00", 2: "#a6ff00", 3: "#f1c40f", 4: "#e67e22", 5: "#a50000" };

  function renderRisco(rcmDict, layer, municipiosGeo) {
    if (!municipiosGeo) return;
    const geo = structuredClone(municipiosGeo);
    geo.features.forEach((f) => {
      const dico = String(f.properties.DICO).padStart(4, "0");
      const rcm = rcmDict[dico];
      f.properties.cor = cores_risco[rcm] || "#cccccc";
    });
    layer.clearLayers();
    layer.addData(geo);
    layer.addTo(map);
  }

  const riscoHojeLayer = L.geoJSON(null, {
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
      if (!checkboxRisco0.checked) return map.removeLayer(riscoHojeLayer);
      fetch("/api/rcm/hoje/")
        .then((r) => r.json())
        .then((rcmDict) => renderRisco(rcmDict, riscoHojeLayer, municipiosData));
    });
  }

  const riscoAmanhaLayer = L.geoJSON(null, {
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
      if (!checkboxRisco1.checked) return map.removeLayer(riscoAmanhaLayer);
      fetch("/api/rcm/amanha/")
        .then((r) => r.json())
        .then((rcmDict) => renderRisco(rcmDict, riscoAmanhaLayer, municipiosData));
    });
  }
});