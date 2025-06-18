from flask import Flask, request, jsonify, render_template_string
import requests
import threading
import time
from datetime import datetime
import json

app = Flask(__name__)

monitored_urls = {}
status_history = {}

def check_url_status(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'status': 'online' if response.status_code == 200 else 'error',
            'status_code': response.status_code,
            'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'offline',
            'status_code': None,
            'response_time_ms': None,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def monitor_urls():
    while True:
        for url in list(monitored_urls.keys()):
            if url in monitored_urls:
                result = check_url_status(url)
                
                if url not in status_history:
                    status_history[url] = []
                
                status_history[url].append(result)
                
                if len(status_history[url]) > 10:
                    status_history[url] = status_history[url][-10:]
                
                status = result['status']
                print(f"[{result['timestamp']}] {url} - {status}")
                
                if status == 'offline':
                    print(f"ALERTA: {url} esta fora do ar! Erro: {result['error']}")
                elif status == 'error':
                    print(f"AVISO: {url} retornou status {result['status_code']}")
        
        time.sleep(30)

monitor_thread = threading.Thread(target=monitor_urls, daemon=True)
monitor_thread.start()

@app.route('/')
def home():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monitor de Status</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .url-item { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .status-online { background-color: #d4edda; }
            .status-offline { background-color: #f8d7da; }
            .status-error { background-color: #fff3cd; }
            button { padding: 8px 15px; margin: 5px; cursor: pointer; }
            input[type="url"] { width: 300px; padding: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Monitor de Status de Servicos Web</h1>
            
            <div>
                <h3>Adicionar Nova URL</h3>
                <form id="addUrlForm">
                    <input type="url" id="urlInput" placeholder="https://example.com" required>
                    <button type="submit">Adicionar URL</button>
                </form>
            </div>

            <div id="urlsList">
                <h3>URLs Monitoradas</h3>
                <div id="urls-container"></div>
            </div>
        </div>

        <script>
            function loadUrls() {
                fetch('/api/urls')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('urls-container');
                        container.innerHTML = '';
                        
                        if (Object.keys(data).length === 0) {
                            container.innerHTML = '<p>Nenhuma URL sendo monitorada.</p>';
                            return;
                        }
                        
                        for (const [url, urlData] of Object.entries(data)) {
                            const lastStatus = urlData.last_status;
                            const statusClass = lastStatus ? `status-${lastStatus.status}` : '';
                            
                            const urlDiv = document.createElement('div');
                            urlDiv.className = `url-item ${statusClass}`;
                            
                            let statusText = 'Aguardando primeira verificacao...';
                            if (lastStatus) {
                                statusText = `Status: ${lastStatus.status.toUpperCase()}`;
                                if (lastStatus.response_time_ms) {
                                    statusText += ` | Tempo: ${lastStatus.response_time_ms}ms`;
                                }
                                statusText += ` | Ultima verificacao: ${new Date(lastStatus.timestamp).toLocaleString()}`;
                                if (lastStatus.error) {
                                    statusText += `<br><small>Erro: ${lastStatus.error}</small>`;
                                }
                            }
                            
                            urlDiv.innerHTML = `
                                <strong>${url}</strong>
                                <button onclick="removeUrl('${url}')" style="float: right;">Remover</button>
                                <br>${statusText}
                            `;
                            container.appendChild(urlDiv);
                        }
                    });
            }
            
            function addUrl(url) {
                fetch('/api/urls', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('urlInput').value = '';
                        loadUrls();
                    } else {
                        alert('Erro: ' + data.message);
                    }
                });
            }
            
            function removeUrl(url) {
                fetch(`/api/urls/${encodeURIComponent(url)}`, {method: 'DELETE'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            loadUrls();
                        }
                    });
            }
            
            document.getElementById('addUrlForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const url = document.getElementById('urlInput').value;
                if (url) addUrl(url);
            });
            
            loadUrls();
            setInterval(loadUrls, 10000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/urls', methods=['GET'])
def get_urls():
    result = {}
    for url in monitored_urls:
        last_status = status_history.get(url, [])[-1] if url in status_history and status_history[url] else None
        result[url] = {
            'added_at': monitored_urls[url]['added_at'],
            'last_status': last_status
        }
    return jsonify(result)

@app.route('/api/urls', methods=['POST'])
def add_url():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'message': 'URL e obrigatoria'})
    
    if not url.startswith(('http://', 'https://')):
        return jsonify({'success': False, 'message': 'URL deve comecar com http:// ou https://'})
    
    if url in monitored_urls:
        return jsonify({'success': False, 'message': 'URL ja esta sendo monitorada'})
    
    monitored_urls[url] = {
        'added_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'message': 'URL adicionada com sucesso'})

@app.route('/api/urls/<path:url>', methods=['DELETE'])
def remove_url(url):
    if url in monitored_urls:
        del monitored_urls[url]
        if url in status_history:
            del status_history[url]
        return jsonify({'success': True, 'message': 'URL removida com sucesso'})
    
    return jsonify({'success': False, 'message': 'URL nao encontrada'})

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'monitored_urls_count': len(monitored_urls)
    })

if __name__ == '__main__':
    monitored_urls.update({
        'https://www.adaptersolucoes.com.br': {'added_at': datetime.now().isoformat()},
        'https://alpha.adapter.net.br': {'added_at': datetime.now().isoformat()},
        'https://omega.adapter.net.br': {'added_at': datetime.now().isoformat()}
    })
    
    print("Iniciando Monitor de Status de Servicos Web...")
    print("Acesse: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
