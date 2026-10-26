import queue
import threading
import time
import sqlite3
from logs import logger
from cache_compartilhado import CacheCompartilhado
import ingestao

# Configurações experimentais (Parte C do Roteiro)
TAMANHO_FILA = 50
NUM_PRODUTORES = 2
NUM_CONSUMIDORES = 4

# Filas e Instâncias Compartilhadas
fila_requisicoes = queue.Queue(maxsize=TAMANHO_FILA)
cache = CacheCompartilhado(capacidade=100)

def recuperar_contexto(consulta):
    """Localiza o trecho relevante no banco de dados SQLite com tratamento de falhas (C6)."""
    inicio = time.perf_counter()
    trecho = "Contexto não encontrado."
    
    try:
        # Abertura modo leitura via URI permite capturar exclusão acidental do DB de forma limpa
        conn = sqlite3.connect("file:banco_vetores.db?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT trecho FROM documentos LIMIT 1") # Busca simplificada
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            trecho = resultado[0]
            
    except sqlite3.OperationalError as e:
        # C6 - Falha controlada: O servidor registra a queda mas não encerra a execução das threads
        logger.registrar(f"[FALHA CONTROLADA] Erro ao acessar o índice vetorial: {e}", "ERRO")
        return "Serviço de banco de dados temporariamente indisponível."
        
    tempo_rec = time.perf_counter() - inicio
    logger.registrar(f"Recuperação: Extraiu {len(trecho)} bytes em {tempo_rec:.4f}s")
    return trecho

def simular_geracao(consulta, contexto):
    """Gera a resposta (ou chama o runtime local do Ollama via subprocess)."""
    inicio = time.perf_counter()
    time.sleep(0.08) # Simula latência de processamento de IA / GPU
    resposta = f"LLM_Output: Sobre '{consulta}', a base diz: '{contexto[:20]}...'"
    tempo_ger = time.perf_counter() - inicio
    return resposta, tempo_ger

def consumidor_trabalhador(id_thread):
    while True:
        # Registra espera na fila (tempo em que o trabalhador fica bloqueado sem requisição)
        inicio_espera = time.perf_counter()
        req = fila_requisicoes.get()
        tempo_espera = time.perf_counter() - inicio_espera
        
        if req is None: # Comando de encerramento
            break
            
        consulta = req["consulta"]
        logger.registrar(f"Trabalhador {id_thread} assumiu requisição '{consulta}' (Aguardou {tempo_espera:.4f}s na fila)")
        
        resposta_cache = cache.buscar(consulta)
        if resposta_cache:
            logger.registrar(f"Trabalhador {id_thread}: ACERTO DE CACHE para '{consulta}'")
        else:
            logger.registrar(f"Trabalhador {id_thread}: ERRO DE CACHE. Processando pipeline...")
            contexto = recuperar_contexto(consulta)
            resposta, tempo_geracao = simular_geracao(consulta, contexto)
            cache.salvar(consulta, resposta, tempo_geracao)
            logger.registrar(f"Trabalhador {id_thread}: Geração finalizada em {tempo_geracao:.4f}s")
        
        fila_requisicoes.task_done()

def produtor(id_thread, total_consultas):
    """Envia requisições repetidas propositalmente para forçar o uso de cache (C4)."""
    consultas_teste = ["Como a RAM funciona?", "Defina escalonador CFS", "Como a RAM funciona?"]
    for i in range(total_consultas):
        consulta = consultas_teste[i % len(consultas_teste)]
        tamanho = len(consulta.encode('utf-8'))
        
        fila_requisicoes.put({"consulta": consulta, "id_produtor": id_thread, "tamanho": tamanho})
        logger.registrar(f"Produtor {id_thread}: Enfileirou '{consulta}' ({tamanho} bytes)")
        time.sleep(0.02) # Simula o delay de requisições de rede

def iniciar_servidor(num_consumidores):
    logger.registrar(f"INICIANDO TESTE COM {num_consumidores} TRABALHADORES", "SISTEMA")
    print(f"\n--- Iniciando execução com {num_consumidores} Consumidores ---")
    
    # Reset do cache e fila para o novo teste
    global cache, fila_requisicoes
    cache = CacheCompartilhado(capacidade=100)
    fila_requisicoes = queue.Queue(maxsize=TAMANHO_FILA)

    ingestao.gerar_corpus("corpus.txt", tamanho_mb=2)
    tamanho_bytes, qtde_indices = ingestao.ingestao_sqlite("corpus.txt")

    inicio_teste = time.perf_counter()

    threads_cons = []
    for i in range(num_consumidores):
        t = threading.Thread(target=consumidor_trabalhador, args=(i,))
        t.start()
        threads_cons.append(t)

    threads_prod = []
    for i in range(NUM_PRODUTORES):
        t = threading.Thread(target=produtor, args=(i, 15)) 
        t.start()
        threads_prod.append(t)

    for t in threads_prod:
        t.join()
    fila_requisicoes.join()

    for _ in range(num_consumidores):
        fila_requisicoes.put(None)
    for t in threads_cons:
        t.join()

    tempo_total = time.perf_counter() - inicio_teste
    
    logger.registrar(f"Teste com {num_consumidores} threads -> Acertos: {cache.acertos} | Tempo Total: {tempo_total:.4f}s", "METRICA")
    print(f"Finalizado em {tempo_total:.4f}s. Verifique o log.")
    
if __name__ == "__main__":
# VARIÁVEL EXPERIMENTAL (CUMPRINDO O ITEM 7.2):
    # Testando com 1, 2 e 4 trabalhadores para observar a diferença de desempenho
    for qtd in [1, 2, 4]:
        iniciar_servidor(num_consumidores=qtd)
        time.sleep(1) # Pausa rápida entre os testes