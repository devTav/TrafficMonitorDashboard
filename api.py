from fastapi import FastAPI
import uvicorn
from typing import List

# funcoes do collector.py p captura de dados
from collector import get_current_snapshot, get_history, start_capture
import threading

# criando a api

app = FastAPI(title="Traffic Monitor API")

# Endpoint p ver os dados da janela atual
@app.get("/stats/current")
def read_current_stats():
    return get_current_snapshot() # retorna o snapshot da janela de 5 segundos atual

# Endpoint p historico das ultimas janelas
@app.get("/stats/history")
def read_history_stats(limit: int = 10):
    return get_history()[-limit:] # retorna uma lista das N ultimas janelas abertas

# funcao p iniciar o collector em uma thread paralela
def run_collector():
    start_capture()

if __name__ == "__main__":
    print("[*] Iniciando a captura de pacotes em background...")
    collector_thread = threading.Thread(target=run_collector, daemon=True)
    collector_thread.start()
    
    print("[*] Iniciando o servidor da API em http://localhost:9000")
    uvicorn.run(app, host="0.0.0.0", port=9000)

# foreach ($i in 1..20) {
#     curl.exe http://10.181.2.137:8000/test.txt -o NUL
#     Start-Sleep -Milliseconds 200
# }