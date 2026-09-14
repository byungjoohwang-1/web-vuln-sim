'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, 'public');
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8'};
const server = http.createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) {res.writeHead(405);res.end();return;}
  let pathname;
  try {pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);}
  catch (_) {res.writeHead(400);res.end();return;}
  if (pathname === '/') pathname = '/network-system-security.html';
  const target = path.resolve(root, '.' + pathname);
  if (!target.startsWith(root + path.sep) || pathname.includes('\\') || pathname.includes(':') || !mime[path.extname(target)]) {res.writeHead(403);res.end();return;}
  fs.readFile(target, (error, content) => {
    if (error) {res.writeHead(404);res.end('Not found');return;}
    res.writeHead(200, {'Content-Type':mime[path.extname(target)],'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
    res.end(req.method === 'HEAD' ? undefined : content);
  });
});
const port = Number(process.env.PORT || 0);
if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('Invalid PORT');
server.listen(port, '127.0.0.1', () => console.log('http://127.0.0.1:' + server.address().port + '/network-system-security.html'));
