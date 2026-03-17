import { INCIDENT_ICONS } from "./icons.js";

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
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  // ==========================
  // ICONES INCIDENTES
  // ==========================

  function getIncidentIconPath(inc) {

    if (inc.natureza && INCIDENT_ICONS.natureza[inc.natureza]) {
      return INCIDENT_ICONS.natureza[inc.natureza];
    }

    if (inc.category && INCIDENT_ICONS.tipo[inc.category]) {
      return INCIDENT_ICONS.tipo[inc.category];
    }

    return INCIDENT_ICONS.default;
  }

  function createIncidentMarker(lat, lon, inc) {

  const color = inc.status_color || "#333";
  const iconPath = getIncidentIconPath(inc);

  const icon = L.divIcon({
    className: "",
    html: `
      <div style="
        width:36px;       /* aumento da bola */
        height:36px;
        border-radius:50%;
        background:${color};
        display:flex;
        align-items:center;
        justify-content:center;
        border:2px solid white;
      ">
        <img src="${iconPath}" style="
          width:18px;     /* aumento do SVG dentro */
          height:18px;
          filter: brightness(0) invert(1);
        ">
      </div>
    `,
    iconSize: [36, 36],        // tamanho do icon
    iconAnchor: [18, 18]       // centralizar
  });

  return L.marker([lat, lon], { icon });
}

  // ==========================
  // Camada de incidentes
  // ==========================
  const incidentesLayer = L.layerGroup().addTo(map);
  const markersMap = new Map();
  const updateNote = document.getElementById("update-note");

  function createIncidentHtml(inc) {

    const local = [
      inc.location_name,
      inc.parish,
      inc.county,
      inc.district
    ].filter(Boolean).join(", ");

    const updated = inc.updated_at_api
      ? new Date(inc.updated_at_api).toLocaleString()
      : "";

    const meios = [];

    if (inc.means_aerial) meios.push(`🚁 Aéreos: ${inc.means_aerial}`);
    if (inc.means_terrain) meios.push(`🚒 Terrestres: ${inc.means_terrain}`);
    if (inc.means_aquatic) meios.push(`🛳️ Aquáticos: ${inc.means_aquatic}`);
    if (inc.means_man) meios.push(`👷 Operacionais: ${inc.means_man}`);

    const meiosHtml = meios.length
      ? `<ul class="list-disc ml-6 space-y-1">${meios.map(m => `<li>${m}</li>`).join("")}</ul>`
      : `<p class="italic text-gray-500">Sem meios envolvidos</p>`;

    return `
      <div class="flex flex-col space-y-2">
        <h3 class="text-2xl font-bold text-red-600">${inc.natureza || "Incidente"}</h3>

        ${inc.status ? `<p><span class="font-semibold">Estado:</span> ${inc.status}</p>` : ""}
        ${local ? `<p><span class="font-semibold">Local:</span> ${local}</p>` : ""}
        ${updated ? `<p><span class="font-semibold">Atualizado:</span> ${updated}</p>` : ""}

        <div class="mt-2">
          <p class="font-semibold">Meios envolvidos:</p>
          ${meiosHtml}
        </div>

        ${inc.kml ? `<p class="mt-2"><a href="${inc.kml}" target="_blank" class="text-blue-600 hover:underline">Ver KML</a></p>` : ""}

        <div class="mt-2 text-gray-500 text-xs">
          ID: ${inc.api_id}
        </div>

      </div>
    `;
  }

  function showUpdateNote(message) {

    updateNote.innerHTML = message;

    updateNote.classList.remove("opacity-0");
    updateNote.classList.add("opacity-100");

    setTimeout(() => {
      updateNote.classList.remove("opacity-100");
      updateNote.classList.add("opacity-0");
    }, 5000);
  }

  function renderIncidentes(data) {

    const activeIds = new Set();

    data.forEach((inc) => {

      activeIds.add(inc.api_id);

      const lat = Number(inc.latitude);
      const lon = Number(inc.longitude);

      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      if (markersMap.has(inc.api_id)) {

        const marker = markersMap.get(inc.api_id);

        const newMarker = createIncidentMarker(lat, lon, inc);

        marker.setIcon(newMarker.options.icon);

        marker.options.data = inc;

      } else {

        const marker = createIncidentMarker(lat, lon, inc);

        marker.options.data = inc;

        marker.on("click", () => {
          window.openIncidentPanel(createIncidentHtml(marker.options.data));
        });

        markersMap.set(inc.api_id, marker);

        incidentesLayer.addLayer(marker);
      }
    });

    for (const [id, marker] of markersMap) {

      if (!activeIds.has(id)) {

        incidentesLayer.removeLayer(marker);

        markersMap.delete(id);
      }
    }
  }

  async function loadIncidentes() {

    try {

      showUpdateNote("Atualizando incidentes... <br> Próxima atualização em 5:00 minutos.");

      const res = await fetch("/api/incidentes/");

      if (!res.ok) throw new Error("HTTP " + res.status);

      const data = await res.json();

      renderIncidentes(data);

    } catch (err) {

      console.error("Erro a carregar incidentes:", err);

      showUpdateNote("Erro ao atualizar incidentes");
    }
  }

  loadIncidentes();

  setInterval(loadIncidentes, 5 * 60 * 1000);

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

  const cores_risco = {
    1: "#00ff00",
    2: "#a6ff00",
    3: "#f1c40f",
    4: "#e67e22",
    5: "#a50000"
  };

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