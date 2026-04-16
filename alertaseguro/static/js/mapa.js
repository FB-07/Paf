import { INCIDENT_ICONS, ICONS } from "./icons.js";

document.addEventListener("DOMContentLoaded", () => {

  // ==========================
  // MENU DE CAMADAS
  // ==========================
  const menuBtn = document.getElementById("menu-btn-layers");
  const menu = document.getElementById("layers-menu");

  if (menuBtn && menu) {
    menuBtn.addEventListener("click", () => {
      menu.classList.toggle("hidden");
    });

    document.querySelectorAll("#layers-menu button[data-layer]").forEach(btn => {
      btn.addEventListener("click", () => {
        changeBaseLayer(btn.dataset.layer);
        menu.classList.add("hidden");
      });
    });
  }

  document.addEventListener("click", (event) => {
    if (!menu || !menuBtn) return;

    const clickedInsideMenu = menu.contains(event.target);
    const clickedButton = menuBtn.contains(event.target);

    if (!menu.classList.contains("hidden") && !clickedInsideMenu && !clickedButton) {
      menu.classList.add("hidden");
    }
  });

  // ==========================
  // MAPA
  // ==========================
  const mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined") return;

  const map = L.map("map", {
    zoomSnap: 0.25,
    zoomDelta: 0.25
  }).setView([39.9, -8.0], 7);

  setTimeout(() => map.invalidateSize(), 300);

  const baseLayers = {
    road: L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap",
      referrerPolicy: "strict-origin-when-cross-origin"
    }),

    claro: L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      maxZoom: 20,
      attribution: "&copy; OpenStreetMap & CARTO",
      referrerPolicy: "strict-origin-when-cross-origin"
    }),

    escuro: L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      maxZoom: 20,
      attribution: "&copy; OpenStreetMap & CARTO",
      referrerPolicy: "strict-origin-when-cross-origin"
    }),

    satelite: L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      maxZoom: 19,
      attribution: "&copy; Esri",
      referrerPolicy: "strict-origin-when-cross-origin"
    })
  };

  const savedBase = localStorage.getItem("baseLayer");
  let currentBase = baseLayers[savedBase] || baseLayers.road;

  currentBase.addTo(map);

  function changeBaseLayer(name) {
    if (!baseLayers[name]) return;

    map.removeLayer(currentBase);
    currentBase = baseLayers[name];
    currentBase.addTo(map);

    localStorage.setItem("baseLayer", name);
  }

  // ==========================
  // INCIDENTES 
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
          width:36px;
          height:36px;
          border-radius:50%;
          background:${color};
          display:flex;
          align-items:center;
          justify-content:center;
          border:2px solid white;
        ">
          <img src="${iconPath}" style="width:18px;height:18px;filter:brightness(0) invert(1);">
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    return L.marker([lat, lon], { icon });
  }

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
              ? arr.map(i => `
                  <div class="flex justify-between items-center px-3 py-2 text-sm hover:bg-gray-50">
                    <span class="text-gray-800 font-medium truncate max-w-[180px]">
                      ${i.name}
                    </span>
                    <span class="text-gray-500 text-xs">
                      ${i.distance || "-"}
                    </span>
                  </div>
                `).join("")
              : `<div class="px-3 py-2 text-sm text-gray-400 italic">Sem dados disponíveis</div>`
          }
        </div>
      </div>
    `;

    const meanBox = (icon, label, value, color) => `
      <div class="flex flex-col items-center p-3 rounded-xl shadow bg-white border">
        <div class="text-2xl">${icon}</div>
        <div class="text-xs text-gray-500">${label}</div>
        <div class="text-lg font-bold ${color}">${value}</div>
      </div>
    `;

    return `
      <div class="flex flex-col gap-4 text-gray-800">

        <div class="flex justify-between items-center">
          <h3 class="text-xl font-bold text-red-600">
            ${inc.natureza || "Incidente"}
          </h3>
          <span 
            class="text-xs px-2 py-1 rounded font-semibold text-white"
            style="background:${inc.status_color || '#666'}; opacity:0.7;"
          >
            ${inc.status || ""}
          </span>
        </div>

        ${local ? `<div class="bg-gray-50 p-2 rounded-lg text-sm">${ICONS.location} ${local}</div>` : ""}
        ${updated ? `<div class="text-xs text-gray-500">${ICONS.time} Última atualização: ${updated}</div>` : ""}

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
          <div class="bg-blue-50 p-3 rounded-xl">
            <p class="font-semibold mb-2">🌦️ Meteorologia</p>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>Temp: ${weather.temperature_c ?? "-"} ºC</div>
              <div>Humidade: ${weather.humidity_percent ?? "-"}%</div>
              <div>Vento: ${weather.wind_kmh ?? "-"} km/h</div>
              <div>Direção: ${weather.wind_cardinal ?? "-"}</div>
              <div>Pressão: ${weather.pressure_hpa ?? "-"} hPa</div>
              <div>Precipitação: ${weather.precipitation_mmh ?? "-"} mm</div>
            </div>
          </div>
        ` : ""}

        ${nearbySection("Bombeiros mais próximos", ICONS.fire, inc.nearby_fire_stations)}
        ${nearbySection("Hospitais mais próximos", ICONS.hospital, inc.nearby_emergencies)}
        ${nearbySection("Bases aéreas mais próximas", ICONS.air, inc.nearby_airbases)}

        <div class="text-xs text-gray-400">ID: ${inc.api_id}</div>
      </div>
    `;
  }

  const incidentesLayer = L.layerGroup().addTo(map);
  const markersMap = new Map();

  function getSelectedStatuses() {
    return {
      "Em Curso": document.getElementById("statusCurso")?.checked,
      "Em Resolução": document.getElementById("statusResolucao")?.checked,
      "Despacho de 1º Alerta": document.getElementById("statusAlerta")?.checked,
      "Chegada ao TO": document.getElementById("statusChegada")?.checked,
      "Em Conclusão": document.getElementById("statusConclusao")?.checked,
    };
  }

  function saveStatusFilters() {
    const data = {
      statusCurso: document.getElementById("statusCurso")?.checked,
      statusResolucao: document.getElementById("statusResolucao")?.checked,
      statusAlerta: document.getElementById("statusAlerta")?.checked,
      statusChegada: document.getElementById("statusChegada")?.checked,
      statusConclusao: document.getElementById("statusConclusao")?.checked,
    };

    localStorage.setItem("statusFilters", JSON.stringify(data));
  }

  const savedFilters = JSON.parse(localStorage.getItem("statusFilters") || "{}");

  ["statusCurso", "statusResolucao", "statusAlerta", "statusChegada", "statusConclusao"]
    .forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;

      if (savedFilters[id] !== undefined) {
        el.checked = savedFilters[id];
      }

      el.addEventListener("change", () => {
        saveStatusFilters();
        loadIncidentes();
      });
    });

  function renderIncidentes(data) {
    const activeIds = new Set();
    const selectedStatuses = getSelectedStatuses();

    data.forEach(inc => {

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
          window.openIncidentPanel(createIncidentHtml(inc));
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
      if (!res.ok) throw new Error(res.status);

      const data = await res.json();
      renderIncidentes(data);

    } catch (err) {
      console.error("Erro a carregar incidentes:", err);
    }
  }

  loadIncidentes();
  setInterval(loadIncidentes, 5 * 60 * 1000);

  // ==========================
  // MUNICÍPIOS
  // ==========================
  const municipiosLayer = L.geoJSON(null, {
    style: f => ({
      weight: 1,
      color: "#555",
      fillColor: f.properties.cor || "#cccccc",
      fillOpacity: 0.7,
    }),
  });

  let municipiosData = null;

  if (window.MUNICIPIOS_URL) {
    fetch(window.MUNICIPIOS_URL)
      .then(r => r.json())
      .then(data => {
        municipiosData = data;
        data.features.forEach(f => f.properties.cor = "#cccccc");
        municipiosLayer.addData(data);
      });
  }

  document.getElementById("toggleMunicipios")?.addEventListener("change", (e) => {
    e.target.checked ? map.addLayer(municipiosLayer) : map.removeLayer(municipiosLayer);
  });

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

    geo.features.forEach(f => {
      const dico = String(f.properties.DICO).padStart(4, "0");
      const rcm = rcmDict[dico];
      f.properties.cor = cores_risco[rcm] || "#cccccc";
    });

    layer.clearLayers();
    layer.addData(geo);
    layer.addTo(map);
  }

  const riscoHojeLayer = L.geoJSON(null, {
    style: f => ({
      weight: 1,
      color: "#555",
      fillColor: f.properties.cor || "#cccccc",
      fillOpacity: 0.7,
    }),
  });

  const riscoAmanhaLayer = L.geoJSON(null, {
    style: f => ({
      weight: 1,
      color: "#555",
      fillColor: f.properties.cor || "#cccccc",
      fillOpacity: 0.7,
    }),
  });

  document.getElementById("toggleRisco0")?.addEventListener("change", (e) => {
    if (!e.target.checked) return map.removeLayer(riscoHojeLayer);

    fetch("/api/rcm/hoje/")
      .then(r => r.json())
      .then(rcmDict => renderRisco(rcmDict, riscoHojeLayer, municipiosData));
  });

  document.getElementById("toggleRisco1")?.addEventListener("change", (e) => {
    if (!e.target.checked) return map.removeLayer(riscoAmanhaLayer);

    fetch("/api/rcm/amanha/")
      .then(r => r.json())
      .then(rcmDict => renderRisco(rcmDict, riscoAmanhaLayer, municipiosData));
  });

});