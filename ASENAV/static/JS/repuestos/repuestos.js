$(document).ready(function () {
    $.get('/repuestos/repuestos/tabla/', function (html) {
        $('#repuestosList').html(html);
    });
    actualizarGraficosRepuestos();
});

function cargarTablaRepuestos() {
    const query = $('#buscador-repuestos input[name="q"]').val();
    $.get('/repuestos/repuestos/tabla/', { q: query }, function (html) {
        $('#repuestosList').html(html);
    });
}


// Función para Buscador
let currentQuery = '';

// Función para buscar repuestos
$(document).on('submit', '#buscador-repuestos', function (e) {
    e.preventDefault();
    currentQuery = $(this).serialize(); // ✅ guarda el query
    $('#repuestosList').load(`/repuestos/repuestos/tabla/?${currentQuery}`);
});

//Función para paginación
$(document).on('click', '.pagination a', function (e) {
    e.preventDefault();
    const baseUrl = $(this).attr('href'); // puede ser ?page=2 o ?q=...&page=2
    const url = `/repuestos/repuestos/tabla/${baseUrl.includes('?') ? baseUrl + '&' + currentQuery : '?' + currentQuery}`;
    $('#repuestosList').load(url);
});

//Abrir modal de creación
$('#nuevo-repuesto').on('click', function () {
    $.get('/repuestos/repuestos/create_form/', function (html) {
        $('#repuestoContent').html(html);
        $('#repuesto-form').attr('action', '/repuestos/repuestos/create/');
        $('#repuestoTitle').text('Nuevo Repuesto');
        $('#repuestoModal').modal('show');
    });
});

//Abrir modal de movimiento
$(document).on('click', '.movimiento-repuesto', function () {
    const id = $(this).data('id');
    $.get('/repuestos/repuestos/movimiento/create_form/', function (html) {
        $('#movimientoContent').html(html);
        $('#movimiento-form').attr('action', '/repuestos/repuestos/movimiento/create/');
        $('#movimientoModal').modal('show');

        // Preseleccionar el repuesto si se abrió desde la tabla
        $('#movimiento-form select[name="repuesto"]').val(id);
    });
});

//Enviar formulario de movimiento
$(document).on('submit', '#movimiento-form', function (e) {
    e.preventDefault();
    const url = $(this).attr('action');
    const data = $(this).serialize();
    $.post(url, data, function (response) {
        if (response.success) {
            $('#movimientoModal').modal('hide');
            cargarTablaRepuestos();
            mostrarToast('Movimiento registrado correctamente.', 'success');
            actualizarGraficosRepuestos();
        } else {
            mostrarToast('Error al registrar el movimiento.', 'danger');
        }
    });
});

//Abrir modal de edición
$(document).on('click', '.editar-repuesto', function () {
    const id = $(this).data('id');
    $.get(`/repuestos/repuestos/${id}/edit_form/`, function (html) {
        $('#repuestoContent').html(html);
        $('#repuesto-form').attr('action', `/repuestos/repuestos/${id}/edit/`);
        $('#repuestoTitle').text('Editar Repuesto');
        $('#repuestoModal').modal('show');
    });
});

// 📄 Ver detalle en modal
$(document).on('click', '.ver-repuesto', function () {
    const id = $(this).data('id');
    $.get(`/repuestos/repuestos/${id}/detalle_modal/`, function (html) {
        $('#detalleRepuestoContent').html(html);
        $('#detalleRepuestoModal').modal('show');
    });
});

//Enviar formulario (crear o editar)
$(document).on('submit', '#repuesto-form', function (e) {
    e.preventDefault();
    const url = $(this).attr('action');
    const data = $(this).serialize();
    $.post(url, data, function (response) {
        if (response.success) {
            $('#repuestoModal').modal('hide');
            cargarTablaRepuestos();
            mostrarToast('Repuesto guardado exitosamente.', 'success');
            actualizarGraficosRepuestos();
        } else {
            $('#repuestoModal').modal('hide');
            mostrarToast('Error al guardar el repuesto.', 'danger');
        }
    });
});

//Eliminar repuesto
$(document).on('click', '.eliminar-repuesto', function () {
    const id = $(this).data('id');
    if (confirm('¿Estás seguro de que deseas eliminar este repuesto?')) {
        $.post(`/repuestos/repuestos/${id}/delete/`, {}, function () {
            cargarTablaRepuestos();
            mostrarToast('Repuesto eliminado.', 'warning');
            actualizarGraficosRepuestos();
        });
    }
});

//Actualizar gráficos
function actualizarGraficosRepuestos() {
    $('#graficoStockEstado').load('/repuestos/repuestos/grafico_stock_estado/', function () {
        renderizarGraficoStockEstado();
    });
    $('#graficoUbicacion').load('/repuestos/repuestos/grafico_ubicacion/', function () {
        renderizarGraficoUbicacion();
    });
    $('#graficoEstado').load('/repuestos/repuestos/grafico_estado/', function () {
        renderizarGraficoEstado();
    });
    $('#graficoIngresoMensual').load('/repuestos/repuestos/grafico_ingreso_mensual/', function () {
        renderizarGraficoIngresoMensual();
    });
    $('#graficoStockCritico').load('/repuestos/repuestos/grafico_stock_critico/', function () {
        renderizarGraficoStockCritico();
    });
}



// Funciones para renderizar los gráficos
function renderizarGraficoStockEstado() {
    $.get('/repuestos/repuestos/grafico_stock_estado/', function (data) {
        const ctx = document.getElementById('graficoStockEstado').getContext('2d');
        if (window.graficoStockEstado instanceof Chart) {
            window.graficoStockEstado.destroy(); // ✅ limpiar gráfico anterior
        }
        window.graficoStockEstado = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.colors
                }]
            }
        });
    });
}

function renderizarGraficoUbicacion() {
    $.get('/repuestos/repuestos/grafico_ubicacion/', function (data) {
        const ctx = document.getElementById('graficoUbicacion').getContext('2d');
        if (window.graficoUbicacion instanceof Chart) {
            window.graficoUbicacion.destroy();
        }
        window.graficoUbicacion = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Cantidad de Repuestos',
                    data: data.values,
                    backgroundColor: data.colors
                }]
            },
            options: {
                indexAxis: 'x',
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });
}
function renderizarGraficoEstado() {
    $.get('/repuestos/repuestos/grafico_estado/', function (data) {
        const ctx = document.getElementById('graficoEstado').getContext('2d');
        if (window.graficoEstado instanceof Chart) window.graficoEstado.destroy();
        window.graficoEstado = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.colors
                }]
            }
        });
    });
}

function renderizarGraficoStockCritico() {
    $.get('/repuestos/repuestos/grafico_stock_critico/', function (data) {
        const ctx = document.getElementById('graficoStockCritico').getContext('2d');
        if (window.graficoStockCritico instanceof Chart) window.graficoStockCritico.destroy();
        window.graficoStockCritico = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Cantidad actual',
                    data: data.values,
                    backgroundColor: data.colors
                }, {
                    label: 'Stock mínimo',
                    data: data.minimos,
                    backgroundColor: '#ffc107'
                }]
            },
            options: {
                indexAxis: 'x',
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    });
}

function renderizarGraficoIngresoMensual() {
    $.get('/repuestos/repuestos/grafico_ingreso_mensual/', function (data) {
        const ctx = document.getElementById('graficoIngresoMensual').getContext('2d');
        if (window.graficoIngresoMensual instanceof Chart) window.graficoIngresoMensual.destroy();
        window.graficoIngresoMensual = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Ingresos por mes',
                    data: data.values,
                    borderColor: data.color,
                    fill: false,
                    tension: 0.3
                }]
            }
        });
    });
}
