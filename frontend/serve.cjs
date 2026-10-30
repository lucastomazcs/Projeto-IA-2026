const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const files = {
  '/': 'index.html', '/index.html': 'index.html', '/app.html': 'app.html',
  '/landing.css': 'landing.css', '/style.css': 'style.css', '/app.js': 'app.js',
  '/assets/empreendedora.png': 'assets/empreendedora.png'
};
const mime = {html:'text/html; charset=utf-8', css:'text/css; charset=utf-8', js:'text/javascript; charset=utf-8', png:'image/png'};
http.createServer((req, res) => {
  const file = files[new URL(req.url, 'http://localhost').pathname];
  if (!file) { res.writeHead(404); return res.end('Not found'); }
  fs.readFile(path.join(__dirname, file), (error, data) => {
    if (error) { res.writeHead(500); return res.end('Unable to read file'); }
    res.setHeader('Content-Type', mime[file.split('.').pop()]);
    res.end(data);
  });
}).listen(4173, '127.0.0.1', () => console.log('Local: http://127.0.0.1:4173'));
