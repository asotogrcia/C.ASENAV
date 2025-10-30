const mantenciones = [
    { title: 'Mantención Grúa #2', start: '2025-11-10' },
    { title: 'Mantención Compresor #5', start: '2025-11-15' },
    { title: 'Mantención Garra #1', start: '2025-10-20' },
    { title: 'Mantención Soldadora #3', start: '2025-11-25' },
    { title: 'Mantención Torno #4', start: '2025-11-30' },
];

// Confg del calendario
$('#calendar').fullCalendar({
    //Confg básica del calendario
    defaultView: 'month',
    loocale: 'es',
    editable: false,
    selectable: false,
    height: '200px',
    aspectRatio: 1.5,
    //Confg de las mantenciones en el calendario
    events: mantenciones.map(mantenimiento => ({
        title: mantenimiento.title,
        start: mantenimiento.start,
        allDay: true,
    })),
    dayClick: function(info) {
        //Obtener el día seleccionado
        const date = info.dateStr;
        //Obtener las mantenciones del día seleccionado
        const mantencionesDelDia = mantenciones.filter(mantenimiento => mantenimiento.start === date);
        //Mostrar las mantenciones en un modal
        showMantencionesModal(mantencionesDelDia);
    }
});

function showMantencionesModal(mantenciones) {
    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('mantencionesModal'));
    modal.show();

    // Limpiar la lista de mantenciones
    const mantencionesList = document.getElementById('mantencionesList');
    mantencionesList.innerHTML = '';

    // Mostrar las mantenciones
    const ul = document.createElement('ul');
    ul.className = 'list-group';

    mantenciones.forEach(mantenimiento => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = mantenimiento.title;
        ul.appendChild(li);
    });
    mantencionesList.appendChild(ul);
}