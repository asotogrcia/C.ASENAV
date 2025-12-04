/* static/JS/mantenciones/mantenciones.js */

$(document).ready(function() {
    
    const contenedorID = '#mantencionesList';

    // ==============================================================
    // 1. NAVEGACIÓN: BUSCADOR Y PAGINACIÓN (AJAX)
    // ==============================================================

    // A. Buscador
    $(document).on('submit', '#form-busqueda-mantenciones', function (e) {
        e.preventDefault();
        const query = $(this).find('input[name="q"]').val();
        
        $(contenedorID).css('opacity', '0.5');

        $.get(`/mantenciones/mantenciones/tabla/?q=${query}`, function (html) {
            $(contenedorID).html(html);
            $(contenedorID).css('opacity', '1');
        }).fail(function() {
            console.error("Error al buscar");
            $(contenedorID).css('opacity', '1');
        });
    });

    // B. Paginación
    $(document).on('click', contenedorID + ' .pagination a', function (e) {
        e.preventDefault();
        let href = $(this).attr('href');
        
        // Asegurar ruta absoluta si viene relativa
        if (!href.includes('/tabla/')) { 
            href = '/mantenciones/mantenciones/tabla/' + href; 
        }

        $(contenedorID).css('opacity', '0.5');

        $.ajax({
            url: href,
            type: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(html) {
                $(contenedorID).html(html);
                $(contenedorID).css('opacity', '1');
            }
        });
    });


    // ==============================================================
    // 2. APERTURA DE MODALES (CREAR vs EDITAR)
    // ==============================================================

    // A. Abrir modal de CREACIÓN (Carga remota)
    // Como el formulario de crear siempre es igual, lo traemos del servidor
    $('#nueva-mantencion').on('click', function () {
        $.get('/mantenciones/mantenciones/create_form/', function (html) {
            $('#mantencionContent').html(html); 
            $('#mantencion-form').attr('action', '/mantenciones/mantenciones/create/');
            $('#mantencionModal').modal('show');
        });
    });

    // B. Abrir modal de EDICIÓN (Carga Local)
    // CORRECCIÓN: El modal ya existe dentro de la fila de la tabla, solo hay que abrirlo.
    $(document).on('click', '.editar-mantencion', function () {
        const id = $(this).data('id');
        const modalElement = document.getElementById(`modalMantencion${id}`);
        
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else {
            console.error('No se encontró el modal local para ID:', id);
        }
    });


    // ==============================================================
    // 3. INTERCEPTOR DE GUARDADO (CREAR Y EDITAR)
    // ==============================================================
    // Esta función maneja tanto el formulario de crear (#mantencion-form) 
    // como los múltiples formularios de editar (.form-editar-mantencion)
    
    $(document).on('submit', '.form-editar-mantencion, #mantencion-form', function(e) {
        e.preventDefault();

        const form = $(this);
        const url = form.attr('action');
        const modalElement = form.closest('.modal');
        const btnSubmit = form.find('button[type="submit"]');
        const textoOriginal = btnSubmit.text();

        // Bloquear botón para evitar doble envío
        btnSubmit.prop('disabled', true).text('Guardando...');

        // Usamos FormData para soportar subida de archivos en la creación
        const formData = new FormData(this);

        $.ajax({
            url: url,
            type: 'POST',
            data: formData,
            processData: false, 
            contentType: false, 
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                if (response.success) {
                    // 1. Cerrar Modal
                    const modalInstance = bootstrap.Modal.getInstance(modalElement[0]);
                    if (modalInstance) modalInstance.hide();

                    // 2. LIMPIEZA CRÍTICA (Soluciona bloqueo de pantalla)
                    $('.modal-backdrop').remove();
                    $('body').removeClass('modal-open').css('padding-right', '');

                    // 3. Feedback
                    if (typeof mostrarToast === "function") {
                        mostrarToast(response.message || 'Operación exitosa.', 'success');
                    } else {
                        alert(response.message || 'Éxito.');
                    }

                    // 4. Recargar Tabla
                    $('#form-busqueda-mantenciones').submit();
                } else {
                    if (typeof mostrarToast === "function") {
                        mostrarToast(response.message || 'Error en el formulario.', 'danger');
                    } else {
                        alert(response.message || 'Error.');
                    }
                }
            },
            error: function() {
                if (typeof mostrarToast === "function") {
                    mostrarToast('Error de conexión con el servidor.', 'danger');
                } else {
                    alert('Error de conexión.');
                }
            },
            complete: function() {
                btnSubmit.prop('disabled', false).text(textoOriginal);
            }
        });
    });


    // ==============================================================
    // 4. FINALIZAR MANTENCIÓN (LÓGICA DE REPUESTOS)
    // ==============================================================

    // A. Abrir Modal de Finalizar (Carga formulario específico vía AJAX)
    $(document).on('click', '.finalizar-mantencion', function () {
        const id = $(this).data('id');
        // Cargamos el HTML en el contenedor del content, no en el body
        $.get(`/mantenciones/mantenciones/${id}/finalizar/`, function (html) {
            $('#finalizarMantencionContainer').html(html); 
            $('#finalizarMantencionModal').modal('show');
        });
    });

    // B. Agregar Repuesto a la Tabla Visual (Validación de Stock Cliente)
    $(document).on('click', '#btnAgregarRepuestoFinalizar', function() {
        const select = $('#selRepFinalizar');
        const inputCant = $('#cantRepFinalizar');
        const tbody = $('#tablaRepuestosFinalizar');
        const msgVacio = $('#mensajeSinRepuestos');

        const id = select.val();
        const nombre = select.find(':selected').data('nombre');
        const stock = parseInt(select.find(':selected').data('stock')) || 0;
        const cantidad = parseInt(inputCant.val());

        // Validaciones
        if (!id) {
            if (typeof mostrarToast === "function") mostrarToast('Selecciona un repuesto.', 'warning');
            return;
        }
        if (!cantidad || cantidad < 1) {
            if (typeof mostrarToast === "function") mostrarToast('Ingresa una cantidad válida.', 'warning');
            return;
        }
        if (cantidad > stock) {
            if (typeof mostrarToast === "function") mostrarToast(`Stock insuficiente. Solo hay ${stock} disponibles.`, 'danger');
            return;
        }

        msgVacio.hide(); 

        // Verificar si ya existe en la tabla para sumar
        let filaExistente = tbody.find(`tr[data-id="${id}"]`);
        if (filaExistente.length > 0) {
            let cantActual = parseInt(filaExistente.data('cantidad'));
            let nuevaCant = cantActual + cantidad;
            
            if (nuevaCant > stock) {
                if (typeof mostrarToast === "function") mostrarToast(`No puedes agregar más. El total supera el stock (${stock}).`, 'danger');
                return;
            }

            filaExistente.data('cantidad', nuevaCant);
            filaExistente.find('td:eq(1)').text(nuevaCant); 
        } else {
            // Crear fila nueva
            let fila = `
                <tr data-id="${id}" data-cantidad="${cantidad}">
                    <td>${nombre}</td>
                    <td class="text-center fw-bold">${cantidad}</td>
                    <td class="text-center">
                        <button type="button" class="btn btn-sm btn-outline-danger border-0 py-0 btn-borrar-rep-finalizar">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            tbody.append(fila);
        }

        select.val('');
        inputCant.val('');
    });

    // C. Borrar fila de repuesto
    $(document).on('click', '.btn-borrar-rep-finalizar', function() {
        $(this).closest('tr').remove();
        if ($('#tablaRepuestosFinalizar tr').length === 0) {
            $('#mensajeSinRepuestos').show();
        }
    });

    // D. Enviar Formulario de Finalización
    $(document).on('submit', '#formFinalizarMantencion', function(e) {
        e.preventDefault();

        const form = $(this);
        const btnSubmit = form.find('button[type="submit"]');
        const textoOriginal = btnSubmit.html();

        // 1. Empaquetar tabla visual a JSON
        let repuestosArray = [];
        $('#tablaRepuestosFinalizar tr').each(function() {
            repuestosArray.push({
                id: $(this).data('id'),
                cantidad: $(this).data('cantidad')
            });
        });

        // 2. Asignar al input oculto
        $('#repuestosDataFinalizar').val(JSON.stringify(repuestosArray));

        // 3. Enviar
        btnSubmit.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Procesando...');

        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                if (response.success) {
                    $('#finalizarMantencionModal').modal('hide');
                    
                    $('.modal-backdrop').remove();
                    $('body').removeClass('modal-open').css('padding-right', '');

                    if (typeof mostrarToast === "function") mostrarToast(response.message, 'success');
                    
                    $('#form-busqueda-mantenciones').submit();
                } else {
                    if (typeof mostrarToast === "function") mostrarToast(response.message, 'danger');
                    btnSubmit.prop('disabled', false).html(textoOriginal);
                }
            },
            error: function() {
                if (typeof mostrarToast === "function") mostrarToast('Error al finalizar.', 'danger');
                btnSubmit.prop('disabled', false).html(textoOriginal);
            }
        });
    });


    // ==============================================================
    // 5. ELIMINACIÓN Y DETALLES
    // ==============================================================

    // Eliminar Mantención
    $(document).on('click', '.eliminar-mantencion', function () {
        const id = $(this).data('id');
        if (confirm('¿Estás seguro de eliminar esta mantención?')) {
            $.ajax({
                url: `/mantenciones/mantenciones/delete/${id}/`,
                type: 'POST',
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken') 
                },
                success: function (response) {
                    if(response.success){
                        $('#form-busqueda-mantenciones').submit();
                        if (typeof mostrarToast === "function") mostrarToast(response.message || 'Eliminado correctamente.', 'success');
                    } else {
                        if (typeof mostrarToast === "function") mostrarToast('No se pudo eliminar.', 'danger');
                    }
                }
            });
        }
    });

    // Ver Detalles
    $(document).on('click', '.ver-mantencion', function () {
        const id = $(this).data('id');
        $.get(`/mantenciones/mantenciones/${id}/ver/`, function (html) {
            $('#detalleMantencionContent').html(html);
            $('#detalleMantencionModal').modal('show');
        });
    });

});

// ==============================================================
// FUNCIONES UTILITARIAS
// ==============================================================

function validarArchivos(input) {
    const archivos = input.files;
    const maxArchivos = 3;
    const extensionesPermitidas = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'xlsm', 'jpg', 'png'];

    if (archivos.length > maxArchivos) {
        if (typeof mostrarToast === "function") mostrarToast(`Máximo ${maxArchivos} archivos permitidos.`, 'warning');
        input.value = '';
        return;
    }

    for (let archivo of archivos) {
        const ext = archivo.name.split('.').pop().toLowerCase();
        if (!extensionesPermitidas.includes(ext)) {
            if (typeof mostrarToast === "function") mostrarToast(`Archivo no permitido: ${archivo.name}`, 'danger');
            input.value = '';
            return;
        }
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}