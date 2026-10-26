import os
import time
import mmap
import sqlite3

def gerar_corpus(caminho, tamanho_mb=5):
    """Cria um documento de texto sintético para servir de base documental."""
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("Sistemas operacionais gerenciam hardware e abstraem recursos. " * (tamanho_mb * 1024 * 15))

def ingestao_sqlite(caminho_txt, db_path="banco_vetores.db"):
    """Lê, fragmenta e armazena os embeddings simulados no SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS documentos (id INTEGER PRIMARY KEY, trecho TEXT, vetor TEXT)")
    cursor.execute("DELETE FROM documentos") # Limpa execuções antigas
    
    with open(caminho_txt, "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    # Fragmenta o documento em partes menores (chunks) de 200 caracteres
    fragmentos = [conteudo[i:i+200] for i in range(0, len(conteudo), 200)]
    
    # Produzir embeddings simulados e guardar
    for frag in fragmentos[:500]: # Limita a 500 blocos para agilizar os testes
        vetor_simulado = str([len(frag), ord(frag[0]), frag.count("a")]) # Simulação de vetor
        cursor.execute("INSERT INTO documentos (trecho, vetor) VALUES (?, ?)", (frag, vetor_simulado))
    
    conn.commit()
    tamanho_corpus = os.path.getsize(caminho_txt)
    registros = cursor.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    conn.close()
    
    return tamanho_corpus, registros

def ler_convencional(caminho):
    """Lê arquivo usando cópia de blocos para RAM (C1)."""
    inicio = time.perf_counter()
    with open(caminho, "rb") as f:
        dados = f.read()
    return len(dados), time.perf_counter() - inicio

def ler_mmap(caminho):
    """Lê arquivo usando mapeamento direto de memória virtual (C2)."""
    inicio = time.perf_counter()
    with open(caminho, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            _ = mm[:1000] # Força falta de página minor para acessar os dados
            tamanho = mm.size()
    return tamanho, time.perf_counter() - inicio