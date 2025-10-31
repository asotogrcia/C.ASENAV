// Configura jQuery para incluir el token CSRF en cada POST
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^GET|HEAD|OPTIONS|TRACE$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        }
    }
});

// Cargar el formulario en el modal
$('#nuevo-equipo').on('click', function () {
    $.get('/equipos/equipo_create_form/', function (data) {
        $('#equipoContent').html(data);
        $('#equipo-form').attr('action', `/equipos/equipo_create_submit/`);
        setTimeout(() => $('#equipoModal').modal('show'), 300);
    });
});

// Enviar el formulario vía AJAX - CREACIÓN
$(document).on('submit', '#equipo-form', function (e) {
    e.preventDefault();
    const url = $(this).attr('action');
    const data = $(this).serialize();
    $.post(url, data, function (response) {
        if (response.success) {
            $('#equipoModal').modal('hide');
            $('#buscador-equipos').submit();
            mostrarToast('Equipo creado exitosamente.', 'success');

            $('#graficoEstados').load('/equipos/grafico/', function () {
                // Re-renderizar gráfico después de cargar el nuevo canvas
                renderizarGraficoEstados();
            });

        } else {
            $('#equipoModal').modal('hide');
            mostrarToast('Error al guardar el equipo', 'danger');
        }
    });
});


// Abrir modal de edición de equipo vía AJAX - EDICIÓN
$(document).on('click', '.editar-equipo', function () {
    const id = $(this).data('id');
    $.get(`/equipos/equipo/${id}/edit_form/`, function (html) {
        $('#equipoContent').html(html);
        $('#equipo-form').attr('action', `/equipos/equipo/${id}/edit/`);
        $('#equipoTitle').text('Editar Equipo');
        $('#equipoModal').modal('show');
    });
});



// Confirmar eliminación de equipo vía AJAX - ELIMINACIÓN
$(document).on('click', '.eliminar-equipo', function () {
    const id = $(this).data('id');
    if (confirm('¿Estás seguro de que deseas eliminar este equipo?')) {
        $.post(`/equipos/equipo/${id}/delete/`, {}, function (response) {
            if (response.success) {
                mostrarToast('Equipo eliminado correctamente', 'success');
                $('#equiposList').load('/equipos/tabla/');
                $('#graficoEstados').load('/equipos/grafico/', function () {
                    renderizarGraficoEstados();
                });
            } else {
                mostrarToast('Error al eliminar el equipo', 'danger');
            }
        });
    }
});





//Gráfico de Pizza
document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('estadoEquiposChart');
    if (!canvas) return; // Evita el error si no existe

    const valores = JSON.parse(canvas.dataset.valores);
    const ctx = canvas.getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Óptimo', 'Advertencia', 'Crítico', 'Fuera de servicio'],
            datasets: [{
                data: valores,
                backgroundColor: ['#198754', '#ffc107', '#dc3545', '#6c757d'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
});

function renderizarGraficoEstados() {
    const canvas = document.getElementById('estadoEquiposChart');
    if (!canvas) return;

    const valores = JSON.parse(canvas.dataset.valores);
    const ctx = canvas.getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Óptimo', 'Advertencia', 'Crítico', 'Fuera de servicio'],
            datasets: [{
                data: valores,
                backgroundColor: ['#198754', '#ffc107', '#dc3545', '#6c757d'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

let currentQuery = '';

$(document).on('submit', '#buscador-equipos', function (e) {
    e.preventDefault();
    currentQuery = $(this).serialize(); // ✅ guarda el query
    $('#equiposList').load(`/equipos/tabla/?${currentQuery}`);
});

$(document).on('click', '.pagination a', function (e) {
    e.preventDefault();
    const baseUrl = $(this).attr('href'); // puede ser ?page=2 o ?q=...&page=2
    const url = `/equipos/tabla/${baseUrl.includes('?') ? baseUrl + '&' + currentQuery : '?' + currentQuery}`;
    $('#equiposList').load(url);
});


