$(document).ready(function() {
    const contenedorID = '#contenedor-usuarios';

    // 1. Buscador AJAX
    $(document).on('submit', '#form-busqueda-usuarios', function (e) {
        e.preventDefault();
        const query = $(this).find('input[name="q"]').val();
        
        $(contenedorID).css('opacity', '0.5');

        $.ajax({
            url: `/usuarios/gestion/?q=${query}`, 
            type: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(html) {
                $(contenedorID).html(html);
                $(contenedorID).css('opacity', '1');
            }
        });
    });

    // 2. Paginación AJAX
    $(document).on('click', contenedorID + ' .pagination a', function (e) {
        e.preventDefault();
        let href = $(this).attr('href');
        
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

    // 3. INTERCEPTAR GUARDADO DE USUARIO (Edición)
    $(document).on('submit', '.form-editar-usuario', function (e) {
        e.preventDefault(); 
        
        const form = $(this); 
        const url = form.attr('action'); 
        const modal = form.closest('.modal'); 
        const btnSubmit = form.find('button[type="submit"]');

        // Desactivar botón
        btnSubmit.prop('disabled', true).text('Guardando...');

        $.ajax({
            url: url,
            type: 'POST',
            data: form.serialize(), 
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                if (response.success) {
                    // A. ÉXITO
                    
                    // 1. Ocultar el modal
                    const modalInstance = bootstrap.Modal.getInstance(modal[0]);
                    modalInstance.hide();
                    
                    // 2. Mostrar mensaje de éxito (Desde Django o genérico)
                    mostrarToast(response.message || "Se han guardado los cambios exitosamente.", "success");
                    
                    // 3. Recargar la tabla
                    $('#form-busqueda-usuarios').submit(); 
                    
                } else {
                    // B. ERROR LÓGICO (Anti-Suicidio, validación, etc.)
                    
                    // AQUÍ ESTÁ EL CAMBIO CLAVE:
                    // Usamos 'response.message' que viene de Django
                    mostrarToast(response.message, "danger");
                    
                    // Nota: No cerramos el modal ni recargamos la tabla, 
                    // así el usuario puede leer el error y corregir.
                }
            },
            error: function(xhr, status, error) {
                // C. ERROR DE SERVIDOR (500, 404)
                console.error(error);
                // Usamos mostrarToast en vez de alert para mantener el estilo
                mostrarToast('Ocurrió un error inesperado en el servidor.', 'danger');
            },
            complete: function() {
                // Reactivar botón
                btnSubmit.prop('disabled', false).text('Guardar Cambios');
            }
        });
    });

});