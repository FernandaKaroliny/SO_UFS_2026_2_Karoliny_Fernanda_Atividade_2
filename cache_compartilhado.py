import threading

class CacheCompartilhado:
    def __init__(self, capacidade=100):
        self.capacidade = capacidade
        self.memoria = {}
        self.acertos = 0
        self.erros = 0
        self.substituicoes = 0
        self.tempo_economizado = 0.0
        self.trava = threading.Lock() # Proteção contra condições de corrida

    def buscar(self, chave):
        with self.trava:
            if chave in self.memoria:
                self.acertos += 1
                # Acumula o tempo que o sistema deixou de gastar gerando a resposta
                self.tempo_economizado += self.memoria[chave]['tempo_geracao']
                return self.memoria[chave]['resposta']
            self.erros += 1
            return None

    def salvar(self, chave, resposta, tempo_geracao):
        with self.trava:
            if chave not in self.memoria and len(self.memoria) >= self.capacidade:
                # Política de remoção FIFO (First-In, First-Out)
                chave_removida = next(iter(self.memoria))
                self.memoria.pop(chave_removida)
                self.substituicoes += 1
            
            self.memoria[chave] = {
                'resposta': resposta, 
                'tempo_geracao': tempo_geracao
            }