// Cargar el formulario en el modal
$('#nuevo-equipo').on('click', function () {
    $.get('/equipos/equipo_create_form/', function (data) {
        $('#equipoContent').html(data);
        setTimeout(() => $('#equipoModal').modal('show'), 300);
    });
});

// Enviar el formulario vía AJAX
$(document).on('submit', '#equipo-form', function (e) {
    e.preventDefault();
    $.post('/equipos/equipo_create_submit/', $(this).serialize(), function (response) {
        if (response.success) {
            $('#equipoModal').modal('hide');
            // Actualizar tabla, mostrar mensaje, etc.
        } else {
            $('#modal-content').html(response.html);
        }
    });
});