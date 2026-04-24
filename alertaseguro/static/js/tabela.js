import { INCIDENT_ICONS } from "./icons.js";

document.addEventListener('DOMContentLoaded', () => {

    const container = document.getElementById('incidentes-container');

    let todosIncidentes = [];
    let modo = "ativos";

    function getIncidentIconPath(inc) {

        if (inc.natureza && INCIDENT_ICONS.natureza?.[inc.natureza]) {
            return INCIDENT_ICONS.natureza[inc.natureza];
        }

        if (inc.category && INCIDENT_ICONS.tipo?.[inc.category]) {
            return INCIDENT_ICONS.tipo[inc.category];
        }

        return INCIDENT_ICONS.default;
    }

    function atualizarBotoes() {

        const btnAtivos = document.getElementById('btn-ativos');
        const btnHistorico = document.getElementById('btn-historico');

        if (modo === "ativos") {

            btnAtivos.classList.add("bg-red-600");
            btnAtivos.classList.remove("bg-gray-700");

            btnHistorico.classList.add("bg-gray-700");
            btnHistorico.classList.remove("bg-red-600");

        } else {

            btnHistorico.classList.add("bg-red-600");
            btnHistorico.classList.remove("bg-gray-700");

            btnAtivos.classList.add("bg-gray-700");
            btnAtivos.classList.remove("bg-red-600");
        }
    }

    function setBotoesLoading(state) {

        const botoes = [
            document.getElementById('btn-ativos'),
            document.getElementById('btn-historico')
        ];

        botoes.forEach(btn => {
            btn.disabled = state;

            if (state) {
                btn.classList.add("opacity-50", "cursor-not-allowed");
            } else {
                btn.classList.remove("opacity-50", "cursor-not-allowed");
            }
        });
    }

    function renderizar(lista) {

        let terrestres = 0, aquaticos = 0, aereos = 0, operacionais = 0;

        container.innerHTML = '';

        document.getElementById('total-incidentes').textContent = lista.length;

        if (!lista.length) {
            container.innerHTML = '<div class="text-center text-gray-500 p-4 italic">Sem incidentes</div>';
            return;
        }

        lista.forEach(inc => {

            terrestres += inc.means?.terrain || 0;
            aquaticos += inc.means?.aquatic || 0;
            aereos += inc.means?.aerial || 0;
            operacionais += inc.means?.man || 0;

            const local = [inc.location_name, inc.parish, inc.county, inc.district]
                .filter(Boolean)
                .join(', ');

            const iconPath = getIncidentIconPath(inc);

            const card = document.createElement('div');
            card.className = 'bg-white p-4 rounded-xl shadow hover:shadow-lg transition';

            card.innerHTML = `
                <div class="flex justify-between mb-2">
                <h4 class="font-bold text-red-600">${inc.natureza || '-'}</h4>
                <span style="color:${inc.status_color || '#333'}">
                    ${inc.status || '-'}
                </span>
                </div>

                <div class="text-gray-600">${local || '-'}</div>

                <div class="flex flex-wrap gap-2 mt-2">
                <div class="flex items-center gap-1 px-2 py-1 bg-gray-200 rounded text-sm">
                    <span>Natureza:</span>
                    <img src="${iconPath}" class="w-4 h-4" style="filter: brightness(0) saturate(100%);" />
                    <span>${inc.category || 'Não Informado'}</span>
                </div>
                <div class="flex items-center gap-1 px-2 py-1 bg-gray-200 rounded text-sm">
                    🚒 <span class="text-red-600 font-bold">${inc.means?.terrain || 0}</span>
                </div>
                <div class="flex items-center gap-1 px-2 py-1 bg-gray-200 rounded text-sm">
                    🛥️ <span class="text-blue-600 font-bold">${inc.means?.aquatic || 0}</span>
                </div>
                <div class="flex items-center gap-1 px-2 py-1 bg-gray-200 rounded text-sm">
                    🚁 <span class="text-green-600 font-bold">${inc.means?.aerial || 0}</span>
                </div>
                <div class="flex items-center gap-1 px-2 py-1 bg-gray-200 rounded text-sm">
                    👷 <span class="text-yellow-600 font-bold">${inc.means?.man || 0}</span>
                </div>
                </div>
            `;

            container.appendChild(card);
        });

        document.getElementById('meios-terrestres').textContent = terrestres;
        document.getElementById('meios-aquaticos').textContent = aquaticos;
        document.getElementById('meios-aereos').textContent = aereos;
        document.getElementById('meios-operacionais').textContent = operacionais;
    }

    function aplicarFiltro() {

        setBotoesLoading(true);

        setTimeout(() => {

            let listaFiltrada = todosIncidentes;

            if (modo === "ativos") {

                listaFiltrada = todosIncidentes.filter(inc => {
                    const status = (inc.status || "").trim().toLowerCase();
                    return status !== "encerrada";
                });
            }

            renderizar(listaFiltrada);

            atualizarBotoes();
            setBotoesLoading(false);

        }, 50);
    }

    fetch("/api/incidentes/")
        .then(res => res.json())
        .then(data => {

            todosIncidentes = data;

            modo = "ativos";

            aplicarFiltro();

        })
        .catch(err => {
            console.error(err);
            container.innerHTML = '<div class="text-red-500 p-4">Erro ao carregar incidentes</div>';
        });

    document.getElementById('btn-ativos').addEventListener('click', () => {
        modo = "ativos";
        aplicarFiltro();
    });

    document.getElementById('btn-historico').addEventListener('click', () => {
        modo = "historico";
        aplicarFiltro();
    });

});