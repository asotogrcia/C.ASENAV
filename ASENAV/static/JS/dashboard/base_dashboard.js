$(document).ready(function () {
    // Mostrar / ocultar sidebar
    $("#toggleSidebar").on("click", function () {
        $("#sidebar").toggleClass("active");
    });

    // Cerrar sidebar al hacer click fuera (en pantallas pequeñas)
    $(document).on("click", function (e) {
        if (!$(e.target).closest("#sidebar, #toggleSidebar").length) {
            $("#sidebar").removeClass("active");
        }
    });
});


// Función para mostrar un toast
function mostrarToast(mensaje, tipo = 'success') {
    const toastEl = document.getElementById('toast-notificacion');
    const toastBody = document.getElementById('toast-body');

    // Cambiar color según tipo
    toastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
    toastEl.classList.add(`bg-${tipo}`);

    toastBody.textContent = mensaje;

    const toast = new bootstrap.Toast(toastEl, {
        delay: 2000, // El toast se desaparece luego de 2 segundos
        autohide: true
    });
    toast.show();
}

