document.addEventListener('DOMContentLoaded', function() {
    const toggleMenuItems = document.querySelectorAll('.toggle-menu');

    toggleMenuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const submenu = item.nextElementSibling; // Encuentra el siguiente <ul> (submenú)
            if (submenu) {
                submenu.classList.toggle('submenu'); // Alternar la visibilidad del submenú
            }
            e.preventDefault(); // Evitar el comportamiento predeterminado del enlace
        });
    });
});