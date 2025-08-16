// wa_qr.js
const express = require('express');
const cors = require('cors');
const qrcode = require('qrcode'); // ← Asegúrate de tenerlo instalado
const fs = require('fs');
const path = require('path');
const { Client, LocalAuth } = require('whatsapp-web.js');

const app = express();
app.use(cors());

const client = new Client({ authStrategy: new LocalAuth() });
let qrCode = null;

client.on('qr', qr => {
  qrCode = qr;
  console.log("🟩 QR recibido, generando imagen...");
  // Guardar el QR como imagen PNG que Flask pueda servir
  qrcode.toFile(path.join(__dirname, '/static', 'qr.png'), qr, (err) => {
    if (err) return console.error("❌ Error generando imagen QR:", err);
    console.log("✅ Imagen QR guardada en /static/qr.png");
  });
});

client.on('ready', () => {
  console.log("🟢 Cliente de WhatsApp listo");
});

client.initialize();

// Ruta para obtener el QR como texto (opcional)
app.get('/qr', async (req, res) => {
  if (!qrCode) return res.status(404).send('QR no generado aún.');
  res.send({ qr: qrCode });
});

const PORT = 3001;
app.listen(PORT, () => console.log(`📡 Servidor WA‑QR en http://localhost:${PORT}`));

