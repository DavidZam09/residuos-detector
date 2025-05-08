// Node.JS y Express.js para la API del backend
// Este archivo se encargará de manejar las rutas y la conexión a la base de datos

const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Configuración de la conexión a la base de datos
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root', // Cambia esto si tu usuario de MySQL es diferente
  password: '', // Cambia esto si tienes una contraseña configurada
  database: 'residuosbd',
});

// Conectar a la base de datos
db.connect((err) => {
  if (err) {
    console.error('Error al conectar a la base de datos:', err);
    return;
  }
  console.log('Conexión exitosa a la base de datos.');
});

// Rutas
app.get('/', (req, res) => {
  res.send('API de Residuos funcionando');
});

// Iniciar el servidor
app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});

// Endpoint para iniciar sesión
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
  
    const query = 'SELECT id, username FROM usuarios WHERE username = ? AND password = ?';
    db.query(query, [username, password], (err, results) => {
      if (err) {
        console.error('Error al verificar las credenciales:', err);
        res.status(500).json({ success: false, message: 'Error del servidor' });
        return;
      }
  
      if (results.length > 0) {
        const user = results[0];
        res.status(200).json({
          success: true,
          message: 'Login exitoso',
          user: {
            id: user.id,
            username: user.username,
          },
        });
      } else {
        res.status(401).json({ success: false, message: 'Credenciales incorrectas' });
      }
    });
  });
// Endpoint para registrar un usuario
app.post('/api/register', (req, res) => {
  const { username, password } = req.body;

  // Verificar si el usuario ya existe
  const selectQuery = 'SELECT * FROM usuarios WHERE username = ?';
  db.query(selectQuery, [username], (err, results) => {
    if (err) {
      console.error('Error al verificar el usuario:', err);
      res.status(500).json({ success: false, message: 'Error del servidor' });
      return;
    }

    if (results.length > 0) {
      res.status(400).json({ success: false, message: 'El usuario ya existe' });
    } else {
      // Insertar el nuevo usuario
      const insertQuery = 'INSERT INTO usuarios (username, password) VALUES (?, ?)';
      db.query(insertQuery, [username, password], (err, results) => {
        if (err) {
          console.error('Error al registrar el usuario:', err);
          res.status(500).json({ success: false, message: 'Error del servidor' });
          return;
        }

        res.status(201).json({ success: true, message: 'Usuario registrado exitosamente' });
      });
    }
  });
});
  // Endpoint para registrar un residuo detectado
app.post('/api/residuos', (req, res) => {
    const { tipo_residuo, ubicacion, usuario_id } = req.body;
  
    const query = 'INSERT INTO residuos_detectados (tipo_residuo, ubicacion, usuario_id) VALUES (?, ?, ?)';
    db.query(query, [tipo_residuo, ubicacion, usuario_id], (err, results) => {
      if (err) {
        console.error('Error al registrar el residuo:', err);
        res.status(500).json({ success: false, message: 'Error del servidor' });
        return;
      }
  
      res.status(201).json({ success: true, message: 'Residuo registrado exitosamente' });
    });
  });
  // Endpoint para obtener los niveles de un usuario
app.get('/api/niveles/:usuario_id', (req, res) => {
    const { usuario_id } = req.params;
  
    const query = 'SELECT * FROM niveles WHERE usuario_id = ?';
    db.query(query, [usuario_id], (err, results) => {
      if (err) {
        console.error('Error al obtener los niveles:', err);
        res.status(500).json({ success: false, message: 'Error del servidor' });
        return;
      }
  
      if (results.length > 0) {
        res.status(200).json({ success: true, data: results[0] });
      } else {
        res.status(404).json({ success: false, message: 'Niveles no encontrados' });
      }
    });
  });

  // Endpoint para actualizar niveles
// Endpoint para actualizar o crear niveles
app.put('/api/niveles', (req, res) => {
    const { usuario_id, nivel_actual, puntos_acumulados } = req.body;
  
    // Verificar si el usuario ya existe en la tabla niveles
    const selectQuery = 'SELECT * FROM niveles WHERE usuario_id = ?';
    db.query(selectQuery, [usuario_id], (err, results) => {
      if (err) {
        console.error('Error al verificar los niveles:', err);
        res.status(500).json({ success: false, message: 'Error del servidor' });
        return;
      }
  
      if (results.length > 0) {
        // Si el usuario ya existe, actualizar los puntos y niveles
        const existingNivel = results[0].nivel_actual;
        const existingPuntos = results[0].puntos_acumulados;
  
        // Calcular los nuevos puntos y nivel
        let nuevosPuntos = existingPuntos + puntos_acumulados;
        let nuevoNivel = existingNivel;
  
        if (nuevosPuntos >= 100) {
          nuevoNivel += Math.floor(nuevosPuntos / 100); // Incrementar el nivel
          nuevosPuntos = nuevosPuntos % 100; // Restar los puntos que exceden 100
        }
  
        const updateQuery = 'UPDATE niveles SET nivel_actual = ?, puntos_acumulados = ? WHERE usuario_id = ?';
        db.query(updateQuery, [nuevoNivel, nuevosPuntos, usuario_id], (err, updateResults) => {
          if (err) {
            console.error('Error al actualizar los niveles:', err);
            res.status(500).json({ success: false, message: 'Error del servidor' });
            return;
          }
  
          res.status(200).json({ success: true, message: 'Niveles actualizados exitosamente' });
        });
      } else {
        // Si el usuario no existe, insertar un nuevo registro
        const insertQuery = 'INSERT INTO niveles (usuario_id, nivel_actual, puntos_acumulados) VALUES (?, ?, ?)';
        db.query(insertQuery, [usuario_id, nivel_actual, puntos_acumulados], (err, insertResults) => {
          if (err) {
            console.error('Error al insertar los niveles:', err);
            res.status(500).json({ success: false, message: 'Error del servidor' });
            return;
          }
  
          res.status(201).json({ success: true, message: 'Niveles creados exitosamente' });
        });
      }
    });
  });
  // Endpoint para registrar una alerta
// Endpoint para registrar una alerta única
app.post('/api/alertas', (req, res) => {
  const { mensaje, ip, ubicacion, usuario_id } = req.body;

  // Verificar si la alerta ya existe
  const selectQuery = 'SELECT * FROM alertas WHERE mensaje = ? AND ip = ?';
  db.query(selectQuery, [mensaje, ip], (err, results) => {
    if (err) {
      console.error('Error al verificar la alerta:', err);
      res.status(500).json({ success: false, message: 'Error del servidor' });
      return;
    }

    if (results.length > 0) {
      // Si la alerta ya existe, no se inserta
      res.status(200).json({ success: false, message: 'La alerta ya existe' });
    } else {
      // Insertar la nueva alerta
      const insertQuery = 'INSERT INTO alertas (mensaje, ip, ubicacion, usuario_id) VALUES (?, ?, ?, ?)';
      db.query(insertQuery, [mensaje, ip, ubicacion, usuario_id], (err, results) => {
        if (err) {
          console.error('Error al registrar la alerta:', err);
          res.status(500).json({ success: false, message: 'Error del servidor' });
          return;
        }

        res.status(201).json({ success: true, message: 'Alerta registrada exitosamente' });
      });
    }
  });
});

// Endpoint para obtener todas las alertas
app.get('/api/alertas', (req, res) => {
  const query = 'SELECT * FROM alertas ORDER BY id DESC';
  db.query(query, (err, results) => {
    if (err) {
      console.error('Error al obtener las alertas:', err);
      res.status(500).json({ success: false, message: 'Error del servidor' });
      return;
    }

    res.status(200).json({ success: true, data: results });
  });
});

// Endpoint para obtener alertas no leídas
app.get('/api/alertassinleer', (req, res) => {
  const query = 'SELECT * FROM alertas WHERE leido = FALSE ORDER BY id DESC';
  db.query(query, (err, results) => {
    if (err) {
      console.error('Error al obtener las alertas:', err);
      res.status(500).json({ success: false, message: 'Error del servidor' });
      return;
    }

    res.status(200).json({ success: true, data: results });
  });
});

// Endpoint para marcar una alerta como leída
app.put('/api/alertas/:id/marcar-leida', (req, res) => {
  const { id } = req.params;
  const query = 'UPDATE alertas SET leido = TRUE WHERE id = ?';
  db.query(query, [id], (err, results) => {
    if (err) {
      console.error('Error al marcar la alerta como leída:', err);
      res.status(500).json({ success: false, message: 'Error del servidor' });
      return;
    }

    res.status(200).json({ success: true, message: 'Alerta marcada como leída' });
  });
});