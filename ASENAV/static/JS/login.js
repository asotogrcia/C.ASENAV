$(function () {
    // Abrir modal de registro desde login
    $('#openRegister').click(function(e){
        e.preventDefault();
        $('#loginModal').modal('hide');
        setTimeout(() => $('#registerModal').modal('show'), 300);
    });

    // Abrir modal de login desde registro
    $('#openLogin').click(function(e){
        e.preventDefault();
        $('#registerModal').modal('hide');
        setTimeout(() => $('#loginModal').modal('show'), 300);
    });

    // Función para validar el registro a través de JSON - AJAX
    $('#registerForm').on('submit', function (e) {
        e.preventDefault();
        $.ajax({
            url: '/usuarios/registro/',
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    $('#registerModal').modal('hide');
                    setTimeout(() => $('#verificarModal').modal('show'), 400);
                    alert(response.message); // mensaje de código enviado
                } else {
                    $('#registerError').text('Revisa los campos del formulario');
                }
            }
        });
    });

    // Función para validar el código de verificación a través de JSON - AJAX
    $('#verificarForm').on('submit', function (e) {
        e.preventDefault();
        $.ajax({
            url: '/usuarios/verificar/',
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    $('#verificarModal').modal('hide');
                    alert(response.message);
                    $('#loginModal').modal('show'); // abrir login
                } else {
                    $('#verificarError').text(response.message || 'Código inválido');
                }
            }
        });
    });

    // Función para validar el login a través de JSON - AJAX
    $('#loginForm').on('submit', function (e) {
        e.preventDefault();
        $.ajax({
            url: '/usuarios/login/',
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    location.reload();
                } else {
                    $('#loginError').text(response.message || 'Credenciales incorrectas');
                }
            }
        });
    });
});
