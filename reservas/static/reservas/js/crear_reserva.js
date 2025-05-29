console.log(window.fechasOcupadas);
document.addEventListener('DOMContentLoaded', function() {
    const fechasOcupadas = window.fechasOcupadas || [];
    const rangos = fechasOcupadas.map(r => ({
        from: r.fecha_inicio,
        to: r.fecha_fin
    }));
    console.log(rangos);
    
    flatpickr("input[name='fecha_inicio']", {
        dateFormat: "Y-m-d",
        disable: rangos,
        minDate: "today"
    });
    flatpickr("input[name='fecha_fin']", {
        dateFormat: "Y-m-d",
        disable: rangos,
        minDate: "today"
    });
});