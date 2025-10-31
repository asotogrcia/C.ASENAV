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

document.getElementById('contact-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const company = document.getElementById('company').value;
    const message = document.getElementById('message').value;

    if (name && email && message) {
        mostrarToast('Gracias por tu mensaje, te contactaremos pronto!', 'success')
    } else {
        mostrarToast('Por favor, complete los campos requeridos.', 'warning');
    }
});


// Trigger barra navegadora
document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.getElementById("mainNavbar");
    const logoAsenav = document.querySelectorAll("#logoAsenav path")
    const navLinks = document.querySelectorAll(".nav-link");
    const trigger = document.getElementById("scrollTrigger");

    const observer = new IntersectionObserver(function (entries) {
        if (entries[0].boundingClientRect.top < 0) {
            navbar.classList.add("navbar-solid");
            navbar.classList.remove("navbar-transparent");
            logoAsenav.forEach(p => {
                p.setAttribute("fill", "#002B5B");
            });
            
            navLinks.forEach(l => {
                l.classList.add("nav-link-scrolled");
                l.classList.remove("nav-link-solid");
            });
        } else {
            navbar.classList.remove("navbar-solid");
            navbar.classList.add("navbar-transparent");
            logoAsenav.forEach(p => {
                p.setAttribute("fill", "#ffffffff");
            });
            navLinks.forEach(l => {
                l.classList.add("nav-link-solid");
                l.classList.remove("nav-link-scrolled");
            });
        }
    });

    observer.observe(trigger);
});