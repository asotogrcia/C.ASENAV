document.getElementById('contact-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const company = document.getElementById('company').value;
    const message = document.getElementById('message').value;

    if (name && email && message) {
        alert(`¡Gracias, ${name}! Hemos recibido tu mensaje y te contactaremos pronto.`);
        this.reset();
    } else {
        alert('Por favor, completa los campos obligatorios (Nombre, Correo Electrónico y Mensaje).');
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