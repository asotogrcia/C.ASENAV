
$(document).ready(function() {
    
    // 1. Manejo del Buscador
    $(document).on('submit', '#form-busqueda-mantenciones', function (e) {
        e.preventDefault();
        const query = $(this).find('input[name="q"]').val();
        
        // Efecto visual opcional: baja la opacidad mientras carga
        $('#mantencionesList').css('opacity', '0.5');

        $.get(`/mantenciones/mantenciones/tabla/?q=${query}`, function (html) {
            $('#mantencionesList').html(html);
            $('#mantencionesList').css('opacity', '1');
        })
        .fail(function() {
            console.error("Error al buscar mantenciones");
            $('#mantencionesList').css('opacity', '1');
        });
    });

    // 2. Manejo de la Paginación (Clicks en "Anterior", "Siguiente", "1", "2"...)
    $(document).on('click', '#mantencionesList .pagination a', function (e) {
        e.preventDefault();
        const url = $(this).attr('href');
        

        let href = $(this).attr('href');
        const baseUrl = '/mantenciones/mantenciones/tabla/';
        let urlFinal = href;
        if (!href.includes(baseUrl)) {
            // Si el href empieza con '?', lo concatenamos
            urlFinal = baseUrl + href;
        }

        $('#mantencionesList').css('opacity', '0.5');

        $.ajax({
            url: urlFinal,
            type: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }, 
            success: function(html) {
                $('#mantencionesList').html(html);
                $('#mantencionesList').css('opacity', '1');
            },
            error: function(xhr, status, error) {
                console.error("Error en paginación:", error);
                $('#mantencionesList').css('opacity', '1');
            }
        });
    });

    // 3. Reactivar modales o tooltips si es necesario
    // Si tus botones de editar/eliminar dejan de funcionar tras buscar, 
    // avísame y agregamos aquí la reinicialización.
});

// Función para buscar mantenciones
// $(document).on('submit', '#form-busqueda-mantenciones', function (e) {
//     e.preventDefault();
//     const query = $(this).find('input[name="q"]').val();
//     $.get(`/mantenciones/mantenciones/tabla/?q=${query}`, function (html) {
//         $('').html(html);
//     });
// });

// $(document).on('click', '.pagination a', function (e) {
//     e.preventDefault();
//     const url = $(this).attr('href');
//     $.get(url, function (html) {
//         $('').html(html);
//     });
// });




// Abrir modal de nueva mantención
$('#nueva-mantencion').on('click', function () {
    $.get('/mantenciones/mantenciones/create_form/', function (html) {
        $('#mantencionContent').html(html);
        $('#mantencion-form').attr('action', '/mantenciones/mantenciones/create/');
        $('#mantencionModal').modal('show');
    });
});

//Abrir modal de editar mantención
$(document).on('click', '.editar-mantencion', function () {
    const id = $(this).data('id');
    $.get(`/mantenciones/mantenciones/${id}/editar_form/`, function (html) {
        $('#mantencionContent').html(html);
        $('#mantencion-form').attr('action', `/mantenciones/mantenciones/${id}/editar/`);
        $('#mantencionModal').modal('show');
    });
});

//Vista de detalles de mantención
$(document).on('click', '.ver-mantencion', function () {
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

//Finalizar Mantención
$(document).on('click', '.finalizar-mantencion', function () {
    const id = $(this).data('id');
    $.get(`/mantenciones/mantenciones/${id}/finalizar/`, function (html) {
        $('#finalizarMantencionModal #finalizarMantencionContent').html(html);
        $('#form-finalizar-mantencion').attr('action', `/mantenciones/mantenciones/${id}/finalizar/`);
        $('#finalizarMantencionModal').modal('show');
    });
});

$(document).on('submit', '#form-finalizar-mantencion', function (e) {
    e.preventDefault(); // evita que el navegador envíe el formulario
    const url = $(this).attr('action');
    const data = $(this).serialize();

    $.post(url, data, function (response) {
        if (response.success) {
            $('#finalizarMantencionModal').modal('hide');
            mostrarToast('Mantención finalizada correctamente', 'success');
            // Actualizar tabla o recargar
            setTimeout(() => location.reload(), 2000);
        } else {
            mostrarToast('Error al finalizar mantención', 'danger');
        }
    }).fail(function (xhr) {
        $('#finalizarMantencionModal #finalizarMantencionContent').html(xhr.responseText);
        mostrarToast('Error de validación o conexión', 'warning');
    });
});

//Eliminación de Mantencion
$(document).on('click', '.eliminar-mantencion', function () {
    const id = $(this).data('id');
    if (confirm('¿Estás seguro de que deseas eliminar este repuesto?')) {
        $.post(`/mantenciones/mantenciones/delete/${id}/`, {}, function () {
            cargarTablaMantenciones();
            mostrarToast('Mantención eliminada correctamente.', 'danger');
        });
    }
});


function agregarRepuesto() {
    const html = $('.repuesto-item').first().clone();
    $('#repuestos-container').append(html);
}