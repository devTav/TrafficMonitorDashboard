import threading
import time
from collections import defaultdict, deque
from typing import Dict, Any
from scapy.all import sniff, IP, TCP, UDP

SERVER_IP = "10.181.2.137" # ipconfig ipv4

IFACE = None # none deixa p scapy achar a melhor itnerface, caso erro trocar Ethernet/Wi-Fi

WINDOW_SECONDS = 5
HISTORY_WINDOWS = 60 # Guardar o historido os ultimos 5 min (60 janelas * 5s)


# -- data structures --

current = defaultdict(lambda: defaultdict(lambda: defaultdict(int))) # armazena os dados das janelas de 5s do momento
history = deque(maxlen=HISTORY_WINDOWS) # lista que guarda janelas anteriores // deqque com maxlen p descartar automaticamente janelas antigas
lock = threading.Lock() # cadeado p garantir consistencia dos dados entre o codigo
window_start = int(time.time()) # marca o inicio da janela atual

# -- funcoes aux --

# funcao aux p captura do nome e porta do protocolo
def _proto_name(pkt):
    if TCP in pkt:
        return f"TCP/{pkt[TCP].sport}" if pkt[IP].src == SERVER_IP else f"TCP/{pkt[TCP].dport}" # vem do servidor, a prota de interesse é a origem (source port) // vai p servidor, é a de destino (destination port)
    if UDP in pkt:
        return f"UDP/{pkt[UDP].sport}" if pkt[IP].src == SERVER_IP else f"UDP/{pkt[UDP].dport}"
    return "OTHER"

# funcao aux p processar cada pacote capturado pelo scapy
def process_packet(pkt):
    global current
    if IP not in pkt:
        return
    
    src, dst = pkt[IP].src, pkt[IP].dst

    if src != SERVER_IP and dst != SERVER_IP: #filtra trafego p apenas que vem e vai do meu server
        return

    #determinar a direcao de quem e o cliente
    direction = "out" if src == SERVER_IP else "in"
    client_ip = dst if direction == "out" else src
    protocol = _proto_name(pkt)
    packet_size = len(pkt)

    with lock:
        current[client_ip][direction][protocol] += packet_size # garantindo integridade da att com o lock


# funcao em thread a parte girando as janelas de tempo
def window_rotator():
    global current, window_start
    while True:
        time.sleep(1) # verificacoes a cada 1 segundo
        now = int(time.time())

        # 5s depois
        if now - window_start >= WINDOW_SECONDS:
            with lock:
                # 1. faz snapshot da janela que acabou
                snapshot ={
                    "t0": window_start,
                    "t1": window_start + WINDOW_SECONDS,
                    "clients": current
                }
                # 2. add no history
                history.append(snapshot)

                #3. faz reset da janela atual p reiniciar a contagem
                current = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
                window_start = now


# Funcoes pra API capturar os dados
def get_current_snapshot():
    with lock:
        return  {
            "t0": window_start,
            "t1": window_start + WINDOW_SECONDS,
            "clients": dict(current)
        }
    
def get_history():
    with lock:
        return list(history)

# Funcao main
def start_capture():
    print(f"[*] iniciando a captura de pacotes para o servidor {SERVER_IP}...")

    rotator_thread = threading.Thread(target=window_rotator, daemon=True)
    rotator_thread.start()
    
    bpf_filter = f"host {SERVER_IP}" # filtro p apenas pacotes do meu server
    
    sniff(filter=bpf_filter, prn=process_packet, store=False, iface=IFACE) # magica :0

if __name__ == "__main__":
    start_capture()