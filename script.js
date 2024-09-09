// script.js

// Seleccionar todos los elementos con submenú
const toggleMenus = document.querySelectorAll('.toggle-menu');

toggleMenus.forEach(menu => {
    menu.addEventListener('click', function(e) {
        // Si el elemento tiene un submenú, entonces evitamos el comportamiento predeterminado (ir a un enlace)
        const submenu = this.nextElementSibling;
        if (submenu && submenu.classList.contains('submenu')) {
            e.preventDefault();
            // Alternar la clase 'open' en el padre para mostrar/ocultar el submenú
            this.parentElement.classList.toggle('open');
        }
    });
});
