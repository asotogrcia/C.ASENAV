document.addEventListener('DOMContentLoaded', function () {
    
    // =========================================================
    // 1. OBTENCIÓN DE DATOS (DEL HTML)
    // =========================================================
    const dataContainer = document.getElementById('dashboard-data');
    
    // Función auxiliar para parsear JSON de forma segura
    const parseData = (attr) => {
        try {
            const raw = dataContainer.getAttribute(attr);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            console.error(`Error al leer datos del atributo ${attr}:`, e);
            return [];
        }
    };

    // Extraemos los datos de Django
    const equiposLabels = parseData('data-equipos-labels');
    const equiposValues = parseData('data-equipos-values');
    
    const mantLabels = parseData('data-mant-labels');
    const mantValues = parseData('data-mant-values');
    
    const topLabels = parseData('data-top-labels');
    const topValues = parseData('data-top-values');
    
    const mesLabels = parseData('data-mes-labels');
    const mesValues = parseData('data-mes-values');
    
    const calendarEvents = parseData('data-calendar-events');


    // =========================================================
    // 2. GRÁFICOS (CHART.JS)
    // =========================================================
    
    // A. Estado de Equipos (Doughnut)
    const ctxEquipos = document.getElementById('estadoEquiposChart');
    if (ctxEquipos) {
        new Chart(ctxEquipos, {
            type: 'doughnut',
            data: {
                labels: equiposLabels,
                datasets: [{
                    data: equiposValues,
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107', '#6c757d'], // Verde, Amarillo, Rojo, Gris
                    borderWidth: 0
                }]
            },
            options: { 
                responsive: true, 
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } } 
            }
        });
    }

    // B. Estado Mantenciones (Pie)
    const ctxMant = document.getElementById('tipoMantencionChart');
    if (ctxMant) {
        new Chart(ctxMant, {
            type: 'pie',
            data: {
                labels: mantLabels,
                datasets: [{
                    data: mantValues,
                    backgroundColor: ['#dc3545', '#198754', '#ffc107', '#0d6efd'],
                    borderWidth: 0
                }]
            },
            options: { 
                responsive: true, 
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } } 
            }
        });
    }

    // C. Equipos más Intervenidos (Barra Horizontal)
    const ctxTop = document.getElementById('equiposIntervenidosChart');
    if (ctxTop) {
        new Chart(ctxTop, {
            type: 'bar',
            data: {
                labels: topLabels,
                datasets: [{
                    label: 'Intervenciones',
                    data: topValues,
                    backgroundColor: '#022873', // Azul oscuro corporativo
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y', // Hace que las barras sean horizontales
                responsive: true,
                scales: { 
                    x: { beginAtZero: true, ticks: { stepSize: 1 } } 
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // D. Actividad Mensual (Línea)
    const ctxMes = document.getElementById('mantencionesMensualesChart');
    if (ctxMes) {
        new Chart(ctxMes, {
            type: 'line',
            data: {
                labels: mesLabels,
                datasets: [{
                    label: 'Total Mantenciones',
                    data: mesValues,
                    borderColor: '#0468BF',
                    backgroundColor: 'rgba(4,104,191,0.1)',
                    tension: 0.4, // Curvatura de la línea
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }


    // =========================================================
    // 3. CALENDARIO (FULLCALENDAR v6)
    // =========================================================
    const calendarEl = document.getElementById('calendar');
    
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es', // Idioma Español
            
            // Textos personalizados
            buttonText: {
                today:    'Hoy',
                month:    'Mes',
                list:     'Lista'
            },

            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,listWeek'
            },
            
            height: 'auto', // Ajuste automático de altura
            events: calendarEvents, // Cargamos los datos de Django
            
            // ACCIÓN: Clic en un día vacío
            dateClick: function(info) {
                mostrarDetalleDia(info.dateStr, calendarEvents);
            },

            // ACCIÓN: Clic en un evento (barrita de color)
            eventClick: function(info) {
                info.jsEvent.preventDefault(); // Evitar navegación
                // Obtenemos fecha formato YYYY-MM-DD
                const fechaStr = info.event.startStr.split('T')[0];
                mostrarDetalleDia(fechaStr, calendarEvents);
            }
        });

        calendar.render();
    }

    // =========================================================
    // 4. FUNCIÓN AUXILIAR: CONSTRUIR ACORDEÓN EN MODAL
    // =========================================================
    function mostrarDetalleDia(fecha, todosLosEventos) {
        const contenedor = document.getElementById('accordionMantenciones');
        const titulo = document.getElementById('modalFechaTitulo');
        const msgVacio = document.getElementById('msgVacioCal');
        
        // Poner fecha en el título del modal
        titulo.textContent = fecha;
        contenedor.innerHTML = ''; // Limpiar contenido anterior

        // Filtramos en memoria los eventos que coinciden con la fecha clickeada
        const eventosDia = todosLosEventos.filter(ev => ev.start === fecha);

        if (eventosDia.length === 0) {
            msgVacio.classList.remove('d-none');
        } else {
            msgVacio.classList.add('d-none');

            // Construir el HTML del Acordeón dinámicamente
            eventosDia.forEach((ev, index) => {
                const props = ev.extendedProps; // Datos extra (estado, encargado, etc)
                const idCollapse = `collapse${index}`;
                const idHeading = `heading${index}`;

                const htmlItem = `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="${idHeading}">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${idCollapse}" aria-expanded="false" aria-controls="${idCollapse}">
                                <div class="d-flex align-items-center w-100 justify-content-between me-3">
                                    <span class="fw-bold text-dark">${ev.title}</span>
                                    <span class="badge text-white" style="background-color: ${ev.backgroundColor}">
                                        ${props.estado}
                                    </span>
                                </div>
                            </button>
                        </h2>
                        <div id="${idCollapse}" class="accordion-collapse collapse" aria-labelledby="${idHeading}" data-bs-parent="#accordionMantenciones">
                            <div class="accordion-body bg-light">
                                <div class="mb-2">
                                    <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Encargado</small>
                                    <div class="d-flex align-items-center">
                                        <i class="bi bi-person-circle me-2 text-secondary"></i>
                                        <span>${props.encargado}</span>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Descripción</small>
                                    <p class="mb-0 bg-white p-2 rounded border text-secondary fst-italic">
                                        "${props.descripcion}"
                                    </p>
                                </div>
                                <div class="text-end border-top pt-2">
                                    <a href="/mantenciones/mantenciones/tabla/?q=${ev.title}" class="btn btn-sm btn-primary">
                                        <i class="bi bi-gear-fill"></i> Gestionar Mantención
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                contenedor.insertAdjacentHTML('beforeend', htmlItem);
            });
        }

        // Abrir el Modal
        const modalEl = document.getElementById('modalCalendario');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
});