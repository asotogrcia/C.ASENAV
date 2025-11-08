// Función para buscar mantenciones
$(document).on('submit', '#form-busqueda-mantenciones', function (e) {
    e.preventDefault();
    const query = $(this).find('input[name="q"]').val();
    $.get(`/mantenciones/mantenciones/tabla/?q=${query}`, function (html) {
        $('').html(html);
    });
});

$(document).on('click', '.pagination a', function (e) {
    e.preventDefault();
    const url = $(this).attr('href');
    $.get(url, function (html) {
        $('').html(html);
    });
});




// Abrir modal de nueva mantención
$('#nueva-mantencion').on('click', function () {
    $.get('/mantenciones/mantenciones/create_form/', function (html) {
        $('#mantencionContent').html(html);
        $('#mantencion-form').attr('action', '/mantenciones/mantenciones/create/');
        $('#mantencionModal').modal('show');
    });
});

//Abrir modal de editar mantención
$('.editar-mantencion').on('click', function () {
    const id = $(this).data('id');
    $.get(`/mantenciones/mantenciones/${id}/editar_form/`, function (html) {
        $('#mantencionContent').html(html);
        $('#mantencion-form').attr('action', `/mantenciones/mantenciones/${id}/editar/`);
        $('#mantencionModal').modal('show');
    });
});

//Vista de detalles de mantención
$('.ver-mantencion').on('click', function () {
    const id = $(this).data('id');
    $.get(`/mantenciones/mantenciones/${id}/ver/`, function (html) {
        $('#detalleMantencionContent').html(html);
        $('#detalleMantencionModal').modal('show');
    });
});

// Enviar formulario de mantención
$(document).on('submit', '#mantencion-form', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    $.ajax({
        url: $(this).attr('action'),
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $('#mantencionModal').modal('hide');
                mostrarToast('Mantención registrada correctamente.', 'success');
                cargarTablaMantenciones();
            } else {
                mostrarToast('Error al guardar la mantención.', 'danger');
            }
        }
    });
});

// Cargar tabla de mantenciones
function cargarTablaMantenciones() {
    $.get('/mantenciones/mantenciones/tabla/', function (html) {
        $('#mantencionesList').html(html);
    });
}


//Función validación archivos
function validarArchivos(input) {
    const archivos = input.files;
    const maxArchivos = 3;
    const extensionesPermitidas = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'xlsm'];

    if (archivos.length > maxArchivos) {
        mostrarToast(`Máximo ${maxArchivos} archivos permitidos.`, 'warning');
        input.value = '';
        return;
    }

    for (let archivo of archivos) {
        const ext = archivo.name.split('.').pop().toLowerCase();
        if (!extensionesPermitidas.includes(ext)) {
            mostrarToast(`Archivo no permitido: ${archivo.name}`, 'danger');
            input.value = '';
            return;
        }
    }
}

function agregarRepuesto() {
    const html = $('.repuesto-item').first().clone();
    $('#repuestos-container').append(html);
}