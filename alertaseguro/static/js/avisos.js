document.addEventListener('DOMContentLoaded', function () {

    function atualizarFiltros() {
        const filtrosSelecionados = [];

        document.querySelectorAll('input[name="filtros"]:checked').forEach(function (checkbox) {
            filtrosSelecionados.push(checkbox.value);
        });

        document.querySelectorAll('.aviso').forEach(function (aviso) {
            const gravidadeAviso = aviso.dataset.gravidade; 

            if (filtrosSelecionados.length === 0 || filtrosSelecionados.includes(gravidadeAviso)) {
                aviso.style.display = 'block'; 
            } else {
                aviso.style.display = 'none'; 
            }
        });
    }

    document.querySelectorAll('input[name="filtros"]').forEach(function (checkbox) {
        checkbox.addEventListener('change', atualizarFiltros);
    });

    atualizarFiltros();
});