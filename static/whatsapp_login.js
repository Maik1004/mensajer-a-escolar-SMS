window.onload = function iniciarLogin() {
    const mensajeEl = document.getElementById("mensaje");
    const temporizadorEl = document.getElementById("temporizador");

    let tiempoRestante = 60;
    const intervalo = setInterval(() => {
        let minutos = Math.floor(tiempoRestante / 60);
        let segundos = tiempoRestante % 60;
        temporizadorEl.innerText = `${minutos}:${segundos < 10 ? '0' : ''}${segundos}`;
        tiempoRestante--;

        if (tiempoRestante < 0) {
            clearInterval(intervalo);
            temporizadorEl.innerText = "⌛ Tiempo finalizado";
            despuesDeLogin();
        }
    }, 1000);
};

function despuesDeLogin() {
    alert("✅ Listo.");
    // Aquí puedes redirigir o hacer una llamada:
    // window.location.href = "/enviar_mensaje"
}
