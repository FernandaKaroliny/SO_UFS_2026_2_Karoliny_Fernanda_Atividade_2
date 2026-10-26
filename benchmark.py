import ingestao
from logs import logger

def rodar_experimento_memoria():
    print("--- BENCHMARK C1, C2, C5 e Parte E: Leitura Convencional vs MMAP sob Pressão ---")
    logger.registrar("Iniciando Benchmarks de Memória", "BENCHMARK")
    
    caminho = "corpus_benchmark.txt"
    
    # C5: Gera arquivo gigante (2 GB) para forçar limite da RAM e ativação de paginação/swap zram
    print("Gerando arquivo de carga de 2 GB. Isso pode levar alguns segundos...")
    ingestao.gerar_corpus(caminho, tamanho_mb=2048) 
    
    # PRIMEIRA EXECUÇÃO (C1): open + read (Atenção: vai pressionar bastante a RAM)
    print("\n[Primeira Execução] Executando leitura convencional (C1)...")
    tam_c1, tempo_c1 = ingestao.ler_convencional(caminho)
    print(f"[C1 - Convencional] Bytes lidos: {tam_c1} | Tempo: {tempo_c1:.4f} segundos")

    print("\n[Segunda Execução] Lendo o mesmo arquivo de novo (Teste do Page Cache do SO)...")
    tam_c1_2, tempo_c1_2 = ingestao.ler_convencional(caminho)
    print(f"[C1 - Convencional 2ª vez] Tempo: {tempo_c1_2:.4f} segundos (Note a redução drástica!)")
    # -----------------------------------------------------------------
    
    # Cenário C2: open + mmap
    print("\nExecutando leitura mapeada (C2)...")
    tam_c2, tempo_c2 = ingestao.ler_mmap(caminho)
    print(f"[C2 - Arquivo Mapeado] Bytes lidos: {tam_c2} | Tempo: {tempo_c2:.4f} segundos")
    
    # Atualizamos o log para salvar o tempo da 2ª leitura também
    logger.registrar(f"Resultado C1(1ª): {tempo_c1:.4f}s | C1(2ª): {tempo_c1_2:.4f}s | C2: {tempo_c2:.4f}s", "METRICA")
 
if __name__ == "__main__":
    rodar_experimento_memoria()


    