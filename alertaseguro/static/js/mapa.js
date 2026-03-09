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
        radius: 9,
        weight: 1,
        fillOpacity: 0.9,
        color: inc.status_color || "#333",
        fillColor: inc.status_color || "#333",
      });

      const local = [inc.location_name, inc.parish, inc.county, inc.district]
        .filter(Boolean)
        .join(", ");
      const updated = inc.updated_at_api
        ? new Date(inc.updated_at_api).toLocaleString()
        : "";

      // Meios envolvidos
      const meios = [];
      if (inc.means_aerial) meios.push(`✈️ Aéreos: ${inc.means_aerial}`);
      if (inc.means_terrain) meios.push(`🚒 Terrestres: ${inc.means_terrain}`);
      if (inc.means_aquatic) meios.push(`🛶 Aquáticos: ${inc.means_aquatic}`);
      if (inc.means_man) meios.push(`👷 Operacionais: ${inc.means_man}`);
      const meiosHtml = meios.length
        ? `<ul class="list-disc ml-6 space-y-1">${meios.map(m => `<li>${m}</li>`).join("")}</ul>`
        : `<p class="italic text-gray-500">Sem meios envolvidos</p>`;

      marker.on("click", () => {
        const html = `
          <div class="flex flex-col space-y-2">
            <h3 class="text-2xl font-bold text-red-600">${inc.natureza || "Incidente"}</h3>

            ${inc.status ? `<p><span class="font-semibold">Estado:</span> <span class="text-blue-700">${inc.status}</span></p>` : ""}
            ${local ? `<p><span class="font-semibold">Local:</span> ${local}</p>` : ""}
            ${updated ? `<p><span class="font-semibold">Atualizado:</span> ${updated}</p>` : ""}

            <div class="mt-2">
              <p class="font-semibold">Meios envolvidos:</p>
              ${meiosHtml}
            </div>

            ${inc.kml ? `<p class="mt-2"><a href="${inc.kml}" target="_blank" class="text-blue-600 hover:underline">📍 Ver KML</a></p>` : ""}

            <div class="mt-2 text-gray-400 text-xs">
              ID: ${inc.api_id}
            </div>
          </div>
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