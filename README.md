# TrafficMonitorDashboard

**Estado atual:** MVP funcional — captura/aggregação em janelas tumbling de 5 segundos e API REST.

## O que há neste repositório
- `collector.py` — módulo que implementa:
  - agregação em janelas de 5s (tumbling window),
  - rotator que fecha janela e armazena histórico em memória,
  - helpers para injetar pacotes sintéticos (útil para testes).
- `api.py` — FastAPI com endpoints:
  - `GET /stats/current` — snapshot da janela em andamento
  - `GET /stats/history?limit=N` — histórico das últimas N janelas
  - `POST /debug/inject` — (dev only) injetar pacote sintético
- `test_aggregator.py` — testes básicos (pytest) para validar a lógica agregadora.
- `.gitignore` — recomendado para ambientes Python/Windows.

## Como rodar (rápido)
1. Criar e ativar virtualenv (recomendado):
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```
2. Instalar dependências:
   ```bash
   pip install fastapi "uvicorn[standard]" pydantic pytest
   # opcional para captura real:
   pip install scapy
   ```
3. Rodar a API (o rotator de janelas inicia no `startup`):
   ```bash
   python api.py
   ```
4. Testar endpoints:
   - `GET http://127.0.0.1:9000/stats/current`
   - `GET http://127.0.0.1:9000/stats/history?limit=10`
   - Injeção (dev): `POST /debug/inject` com JSON:
     ```json
     { "client_ip":"10.10.10.10", "direction":"in", "proto":"TCP/8000", "size":1200 }
     ```

## Observações importantes
- Para captura real no Windows use **Npcap** (instalar com modo WinPcap e loopback support).
- `collector.start_all(capture=False)` é o padrão para desenvolvimento (sem captura real). Mude `capture=True` e configure `collector.IFACE` para ativar Scapy/Npcap.
- `/debug/inject` é apenas para desenvolvimento — remova/proteja antes de produção.
- Histórico é mantido em memória (deque). Para persistência futura, considerar Redis/SQLite.

## Próximos passos recomendados
- Adicionar proteção/autenticação na API.
- Implementar WebSocket para push em tempo real.
- Persistência opcional para histórico longo (Redis/SQLite).
- Testes de stress com geração de tráfego e validação de perda de pacotes.
