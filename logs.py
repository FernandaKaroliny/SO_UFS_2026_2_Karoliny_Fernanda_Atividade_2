import time
import threading

class ServicoLog:
    def __init__(self, arquivo="eventos_servidor.log"):
        self.arquivo = arquivo
        self.trava = threading.Lock() # Mutex para proteção de seção crítica

    def registrar(self, evento, tipo="INFO"):
        agora = time.strftime('%Y-%m-%d %H:%M:%S')
        mensagem = f"[{agora}] [{tipo}] {evento}\n"
        
        # O bloco 'with' adquire a trava (Lock), escreve e a libera em seguida
        with self.trava:
            with open(self.arquivo, "a", encoding="utf-8") as f:
                f.write(mensagem)

# Instância global para ser utilizada nos outros arquivos
logger = ServicoLog()