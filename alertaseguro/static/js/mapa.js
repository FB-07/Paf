import { INCIDENT_ICONS } from "./icons.js";
import { ICONS } from "./icons.js";

document.addEventListener("DOMContentLoaded", () => {

  const mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined") return;

  // ==========================
  // Mapa principal
  // ==========================
  const map = L.map("map", {
    zoomSnap: 0.25,
    zoomDelta: 0.25
  }).setView([39.9, -8.0], 7);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    referrerPolicy: "strict-origin-when-cross-origin"
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
    iconSize: [36, 36],       
    iconAnchor: [18, 18]       
  });

  return L.marker([lat, lon], { icon });
}

  // ==========================
  // Camada de incidentes
  // ==========================
  const incidentesLayer = L.layerGroup().addTo(map);
  const markersMap = new Map();

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

    const m = inc.means || {};
    const weather = inc.weather || {};

    const nearbySection = (title, icon, arr) => `
      <div class="bg-white border rounded-xl shadow-sm overflow-hidden">

        <div class="flex items-center gap-2 px-3 py-2 bg-gray-50 border-b">
          <span class="text-lg">${icon}</span>
          <h4 class="font-bold text-gray-700">${title}</h4>
        </div>

        <div class="divide-y">

          ${
            arr && arr.length
              ? arr.map((i) => `
                  <div class="flex justify-between items-center px-3 py-2 text-sm hover:bg-gray-50 transition">

                    <span class="text-gray-800 font-medium truncate max-w-[180px]">
                      ${i.name}
                    </span>

                    <span class="text-gray-500 text-xs whitespace-nowrap">
                      ${i.distance ? i.distance : "-"}
                    </span>

                  </div>
                `).join("")
              : `
                <div class="px-3 py-2 text-sm text-gray-400 italic">
                  Sem dados disponíveis
                </div>
              `
          }

        </div>

      </div>
    `;

    const meanBox = (icon, label, value, color) => `
      <div class="flex flex-col items-center justify-center p-3 rounded-xl shadow bg-white border">
        <div class="text-2xl">${icon}</div>
        <div class="text-xs text-gray-500 mt-1">${label}</div>
        <div class="text-lg font-bold ${color}">${value}</div>
      </div>
    `;

    return `
      <div class="flex flex-col gap-4 text-gray-800">

        <div class="flex justify-between items-center">
          <h3 class="text-xl font-bold text-red-600">
            ${inc.natureza || "Incidente"}
          </h3>

          <span class="text-xs px-2 py-1 rounded bg-red-100 text-red-600 font-semibold">
            ${inc.status || ""}
          </span>
        </div>

        ${local ? `
          <div class="bg-gray-50 p-2 rounded-lg text-sm">
            ${ICONS.location} ${local}
          </div>
        ` : ""}

        ${updated ? `
          <div class="text-xs text-gray-500">
            ${ICONS.time} Ultima atualização: ${updated}
          </div>
        ` : ""}

        <div>
          <p class="font-semibold mb-2">Meios envolvidos</p>

          <div class="grid grid-cols-2 gap-2">
            ${meanBox(ICONS.means.aerial, "Aéreos", m.aerial || 0, "text-green-600")}
            ${meanBox(ICONS.means.terrain, "Terrestres", m.terrain || 0, "text-red-600")}
            ${meanBox(ICONS.means.aquatic, "Aquáticos", m.aquatic || 0, "text-blue-600")}
            ${meanBox(ICONS.means.man, "Operacionais", m.man || 0, "text-yellow-600")}
          </div>
        </div>

        ${weather && Object.keys(weather).length ? `
          <div class="bg-gradient-to-r from-blue-50 to-blue-100 p-3 rounded-xl shadow-sm">
            <p class="font-semibold mb-2">🌦️ Meteorologia</p>

            <div class="grid grid-cols-2 gap-2 text-sm">

              <div>Temp: ${weather.temperature_c ?? "-"} ºC</div>
              <div>Humidade: ${weather.humidity_percent ?? "-"}%</div>

              <div>Vento: ${weather.wind_kmh ?? "-"} km/h</div>
              <div>Direção: ${weather.wind_cardinal ?? "-"} (${weather.wind_degree ?? "-"}º)</div>

              <div>Pressão: ${weather.pressure_hpa ?? "-"} hPa</div>
              <div>Precipitação: ${weather.precipitation_mmh ?? "-"} mm</div>

              <div>${weather.description ?? "-"}</div>

            </div>
          </div>
        ` : ""}

        ${nearbySection("Bombeiros mais próximos", ICONS.fire, inc.nearby_fire_stations)}

        ${nearbySection("Hospitais mais próximos", ICONS.hospital, inc.nearby_emergencies)}

        ${nearbySection("Bases aéreas mais próximas", ICONS.air, inc.nearby_airbases)}

        <div class="text-xs text-gray-400">
          ID: ${inc.api_id}
        </div>

      </div>
    `;
  }

  function getSelectedStatuses() {
    return {
      "Em Curso": document.getElementById("statusCurso")?.checked,
      "Em Resolução": document.getElementById("statusResolucao")?.checked,
      "Despacho de 1º Alerta": document.getElementById("statusAlerta")?.checked,
      "Chegada ao TO": document.getElementById("statusChegada")?.checked,
      "Em Conclusão": document.getElementById("statusConclusao")?.checked,
    };
  }

  function renderIncidentes(data) {

    const activeIds = new Set();

    const selectedStatuses = getSelectedStatuses();

    data.forEach((inc) => {

      if (!selectedStatuses[inc.status]) return;

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

      const res = await fetch("/api/incidentes/");

      if (!res.ok) throw new Error("HTTP " + res.status);

      const data = await res.json();

      renderIncidentes(data);

    } catch (err) {

      console.error("Erro a carregar incidentes:", err);

    }
  }

  loadIncidentes();

  setInterval(loadIncidentes, 5 * 60 * 1000);

  const statusCheckboxes = [
    "statusCurso",
    "statusResolucao",
    "statusAlerta",
    "statusChegada",
    "statusConclusao"
  ];

  statusCheckboxes.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", loadIncidentes);
    }
  });

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