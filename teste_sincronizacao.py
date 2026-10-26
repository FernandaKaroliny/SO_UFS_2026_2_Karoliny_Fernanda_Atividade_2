import threading
import time
import queue

class SimuladorCache:
    def __init__(self):
        self.acessos_inseguros = 0
        self.acessos_seguros = 0
        self.trava = threading.Lock()

    def registrar_acesso_inseguro(self):
        """Simula a leitura, um micro-atraso (troca de contexto) e a gravação sem Mutex."""
        temp = self.acessos_inseguros
        time.sleep(0.001) # Força o kernel a trocar de thread no meio da operação
        self.acessos_inseguros = temp + 1

    def registrar_acesso_seguro(self):
        """Usa a trava (Mutex) para garantir exclusão mútua na seção crítica."""
        with self.trava:
            temp = self.acessos_seguros
            time.sleep(0.001)
            self.acessos_seguros = temp + 1

def demonstrar_condicao_corrida():
    print("--- PARTE D (OPÇÃO 2): Condição de Corrida e Atualização Perdida ---")
    print("Iniciando 100 threads simultâneas para atualizar o cache...")
    
    cache = SimuladorCache()
    threads_inseguras = []
    threads_seguras = []

    # Teste INSEGURO
    for _ in range(100):
        t = threading.Thread(target=cache.registrar_acesso_inseguro)
        threads_inseguras.append(t)
        t.start()
    for t in threads_inseguras: t.join()

    # Teste SEGURO
    for _ in range(100):
        t = threading.Thread(target=cache.registrar_acesso_seguro)
        threads_seguras.append(t)
        t.start()
    for t in threads_seguras: t.join()

    print(f"[SEM MUTEX] Esperado: 100 | Real: {cache.acessos_inseguros} (CORROMPIDO - Atualizações Perdidas!)")
    print(f"[COM MUTEX] Esperado: 100 | Real: {cache.acessos_seguros} (ÍNTEGRO - Protegido por Lock)\n")

def demonstrar_fila_saturada():
    print("--- PARTE D (FALHA CONTROLADA): Fila Saturada ---")
    # Fila com buffer limitado a apenas 3 itens
    fila = queue.Queue(maxsize=3) 

    def produtor_agressivo():
        for i in range(1, 6):
            try:
                # block=False força a fila a lançar um erro em vez de fazer a thread dormir
                fila.put(f"Requisição-{i}", block=False) 
                print(f"Produtor inseriu Requisição-{i}. Ocupação da fila: {fila.qsize()}/3")
            except queue.Full:
                print(f"[FALHA] Fila estourou! Requisição-{i} rejeitada. (Produtor bloqueado / Fila Saturada)")
    
    t = threading.Thread(target=produtor_agressivo)
    t.start()
    t.join()

if __name__ == "__main__":
    demonstrar_condicao_corrida()
    demonstrar_fila_saturada()