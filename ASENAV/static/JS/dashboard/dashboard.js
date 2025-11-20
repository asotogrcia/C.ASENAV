// Función para gráficos
document.addEventListener('DOMContentLoaded', function () {
    // Estado de los equipos
    new Chart(document.getElementById('estadoEquiposChart'), {
        type: 'doughnut',
        data: {
            labels: ['Operativos', 'En Mantenimiento', 'Con Fallas'],
            datasets: [{
                data: [14, 5, 2],
                backgroundColor: ['#0468BF', '#FFC107', '#DC3545'],
                borderWidth: 0
            }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });

    // Tipo de mantención
    new Chart(document.getElementById('tipoMantencionChart'), {
        type: 'pie',
        data: {
            labels: ['Preventivas', 'Correctivas'],
            datasets: [{
                data: [65, 35],
                backgroundColor: ['#FFC107', '#DC3545'],
                borderWidth: 0
            }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });

    // Equipos más intervenidos
    new Chart(document.getElementById('equiposIntervenidosChart'), {
        type: 'bar',
        data: {
            labels: ['Grúa #2', 'Compresor #5', 'Garra #1', 'Soldadora #3', 'Torno #4'],
            datasets: [{
                label: 'Intervenciones',
                data: [8, 6, 5, 4, 3],
                backgroundColor: '#022873'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: { x: { beginAtZero: true } },
            plugins: { legend: { display: false } }
        }
    });

    // Mantenciones por mes
    new Chart(document.getElementById('mantencionesMensualesChart'), {
        type: 'line',
        data: {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct'],
            datasets: [{
                label: 'Total de Mantenciones',
                data: [5, 6, 8, 10, 9, 12, 11, 13, 10, 15],
                borderColor: '#0468BF',
                backgroundColor: 'rgba(4,104,191,0.2)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
});
