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