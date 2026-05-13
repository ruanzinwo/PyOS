# imports
import time
import random

# ==========================================
# ESTRUTURAS DE DADOS DO KERNEL
# ==========================================

# Tabela global de processos (Nossa "RAM")
tabela_processos = []
pid_counter = 1000  # PIDs na vida real começam em 1000

# Recursos do sistema (Mutex / Deadlock)
recursos = {
    "impressora": None,
    "scanner": None
}

# IPC - Memória compartilhada
memoria_compartilhada = {}


class PCB:
    """Bloco Descritor de Processo (Process Control Block)"""

    def __init__(self, nome, prioridade=5):
        global pid_counter

        self.pid = pid_counter
        self.nome = nome
        self.prioridade = prioridade
        self.parent_pid = None
        self.estado = "PRONTO"  # PRONTO, EXECUTANDO, BLOQUEADO, ZUMBI
        self.ciclos_restantes = random.randint(2, 6)

        pid_counter += 1


# ==========================================
# FUNÇÕES DO KERNEL E ESCALONADOR
# ==========================================

def boot():
    """Simula a inicialização do Sistema Operacional"""

    print("Iniciando PyOS Kernel v1.0...")
    time.sleep(1)

    print("Carregando módulos de memória [OK]")
    time.sleep(0.5)

    print("Iniciando escalonador de processos [OK]")
    time.sleep(0.5)

    print("Bem-vindo ao terminal. Digite 'help' para comandos.\n")


def spawn_process(nome, prioridade=5):
    """Cria um novo processo e adiciona na tabela (RAM)"""

    # LIMITE DE MEMÓRIA (OOM)
    if len(tabela_processos) >= 5:
        print("[Kernel] ERRO: Out of Memory! Limite de processos atingido.")
        return

    novo_processo = PCB(nome, prioridade)
    tabela_processos.append(novo_processo)

    print(f"[Kernel] Processo '{nome}' criado com PID {novo_processo.pid}")


def escalonador_tick():
    """Simula um ciclo do processador executando a fila"""

    prontos = [p for p in tabela_processos if p.estado == "PRONTO"]

    # Escalonamento por prioridade
    prontos.sort(key=lambda p: p.prioridade, reverse=True)

    if not prontos:
        print("[CPU] Ociosa (Idle). Nenhum processo na fila de prontos.")
        return

    processo_atual = prontos[0]

    processo_atual.estado = "EXECUTANDO"

    print(f"\n[CPU] Executando PID {processo_atual.pid} ({processo_atual.nome})...")
    time.sleep(1)

    processo_atual.ciclos_restantes -= 1

    if processo_atual.ciclos_restantes <= 0:
        processo_atual.estado = "ZUMBI"
        print(f"[Kernel] Processo PID {processo_atual.pid} virou ZUMBI.")

    else:
        processo_atual.estado = "PRONTO"

        # Round Robin: move para o final da fila
        tabela_processos.remove(processo_atual)
        tabela_processos.append(processo_atual)

        print(
            f"[Kernel] Chaveamento de contexto. "
            f"PID {processo_atual.pid} pausado e movido para o fim da fila."
        )


# ==========================================
# INTERFACE COM O USUÁRIO (SHELL)
# ==========================================

def shell():
    """O laço principal que aguarda comandos do usuário"""

    global tabela_processos

    while True:
        try:
            comando = input("root@pyos:~# ").strip().lower().split()

            if not comando:
                continue

            acao = comando[0]

            if acao == "exit":
                print("Desligando o sistema...")
                break

            elif acao == "help":
                print("Comandos disponíveis:")
                print("  spawn [nome] [prioridade] - Cria um novo processo")
                print("  ps                        - Lista os processos ativos")
                print("  cpu                       - Executa 1 ciclo do processador")
                print("  run                       - Executa automaticamente todos os processos prontos")
                print("  kill [PID]                - Encerra um processo à força")
                print("  block [PID]               - Bloqueia um processo")
                print("  unblock [PID]             - Desbloqueia um processo")
                print("  lock [PID] [recurso]      - Solicita acesso ao recurso")
                print("  unlock [PID] [recurso]    - Libera o recurso")
                print("  wait                      - Remove processos zumbis da RAM")
                print("  fork [PID]                - Clona um processo")
                print("  send [PID] [mensagem]     - Envia mensagem IPC")
                print("  read [PID]                - Lê mensagens IPC")
                print("  clear                     - Limpa a tela")
                print("  exit                      - Desliga o sistema")

            elif acao == "clear":
                print("\033[H\033[J", end="")

            elif acao == "spawn":
                if len(comando) > 1:
                    try:
                        prioridade = 5

                        if len(comando) > 2:
                            prioridade = int(comando[2])

                        spawn_process(comando[1], prioridade)

                    except ValueError:
                        print("Erro: prioridade deve ser um número inteiro.")
                else:
                    print("Uso correto: spawn [nome] [prioridade]")

            elif acao == "ps":
                print(
                    f"{'PID':<6} | {'PPID':<6} | {'NOME':<12} | "
                    f"{'PRIOR':<8} | {'ESTADO':<12} | {'CICLOS'}"
                )
                print("-" * 75)

                if not tabela_processos:
                    print("Nenhum processo em execução.")
                else:
                    for p in tabela_processos:
                        print(
                            f"{p.pid:<6} | "
                            f"{str(p.parent_pid):<6} | "
                            f"{p.nome[:12]:<12} | "
                            f"{p.prioridade:<8} | "
                            f"{p.estado:<12} | "
                            f"{p.ciclos_restantes}"
                        )

            elif acao == "kill":
                if len(comando) > 1:
                    try:
                        alvo = int(comando[1])
                        antes = len(tabela_processos)

                        tabela_processos = [
                            p for p in tabela_processos if p.pid != alvo
                        ]

                        if len(tabela_processos) < antes:
                            print(f"[Kernel] Sinal SIGKILL enviado. PID {alvo} destruído.")
                        else:
                            print(f"[Kernel] PID {alvo} não encontrado.")

                    except ValueError:
                        print("Erro: O PID deve ser um número inteiro.")
                else:
                    print("Uso correto: kill [PID]")

            elif acao == "cpu":
                escalonador_tick()

            elif acao == "run":
                print("[Kernel] Execução automática iniciada...")

                while True:
                    prontos = [p for p in tabela_processos if p.estado == "PRONTO"]

                    if not prontos:
                        break

                    escalonador_tick()
                    time.sleep(0.5)

                print("[Kernel] Todos os processos prontos finalizaram ou foram bloqueados.")

            elif acao == "block":
                if len(comando) > 1:
                    try:
                        pid = int(comando[1])

                        for p in tabela_processos:
                            if p.pid == pid:
                                p.estado = "BLOQUEADO"
                                print(f"[Kernel] Processo PID {pid} bloqueado.")
                                break
                        else:
                            print(f"[Kernel] PID {pid} não encontrado.")

                    except ValueError:
                        print("Erro: PID inválido.")
                else:
                    print("Uso correto: block [PID]")

            elif acao == "unblock":
                if len(comando) > 1:
                    try:
                        pid = int(comando[1])

                        for p in tabela_processos:
                            if p.pid == pid:
                                p.estado = "PRONTO"
                                print(f"[Kernel] Processo PID {pid} desbloqueado.")
                                break
                        else:
                            print(f"[Kernel] PID {pid} não encontrado.")

                    except ValueError:
                        print("Erro: PID inválido.")
                else:
                    print("Uso correto: unblock [PID]")

            elif acao == "lock":
                if len(comando) > 2:
                    try:
                        pid = int(comando[1])
                        recurso = comando[2]

                        processo = next(
                            (p for p in tabela_processos if p.pid == pid),
                            None
                        )

                        if not processo:
                            print("[Kernel] Processo não encontrado.")
                            continue

                        if recurso not in recursos:
                            print("[Kernel] Recurso inexistente.")
                            continue

                        if recursos[recurso] is None:
                            recursos[recurso] = pid
                            print(f"[Mutex] PID {pid} obteve {recurso}.")
                        else:
                            processo.estado = "BLOQUEADO"
                            print(f"[Deadlock] {recurso} ocupado. PID {pid} bloqueado.")

                    except ValueError:
                        print("PID inválido.")
                else:
                    print("Uso correto: lock [PID] [recurso]")

            elif acao == "unlock":
                if len(comando) > 2:
                    try:
                        pid = int(comando[1])
                        recurso = comando[2]

                        if recurso not in recursos:
                            print("[Kernel] Recurso inexistente.")
                            continue

                        if recursos[recurso] == pid:
                            recursos[recurso] = None
                            print(f"[Mutex] PID {pid} liberou {recurso}.")
                        else:
                            print("[Mutex] Esse processo não possui esse recurso.")

                    except ValueError:
                        print("PID inválido.")
                else:
                    print("Uso correto: unlock [PID] [recurso]")

            elif acao == "wait":
                zumbis = [p for p in tabela_processos if p.estado == "ZUMBI"]

                if not zumbis:
                    print("[Kernel] Nenhum processo zumbi encontrado.")
                else:
                    for z in zumbis:
                        tabela_processos.remove(z)
                        print(f"[Kernel] Processo ZUMBI PID {z.pid} removido da RAM.")

            elif acao == "fork":
                if len(comando) > 1:
                    try:
                        pid_pai = int(comando[1])

                        pai = next(
                            (p for p in tabela_processos if p.pid == pid_pai),
                            None
                        )

                        if not pai:
                            print("[Kernel] Processo pai não encontrado.")
                            continue

                        if len(tabela_processos) >= 5:
                            print("[Kernel] ERRO: Out of Memory! Limite de processos atingido.")
                            continue

                        filho = PCB(f"{pai.nome}_clone", pai.prioridade)
                        filho.ciclos_restantes = pai.ciclos_restantes
                        filho.parent_pid = pai.pid

                        tabela_processos.append(filho)

                        print(f"[Fork] Processo filho criado. PID {filho.pid} | Pai {pai.pid}")

                    except ValueError:
                        print("PID inválido.")
                else:
                    print("Uso correto: fork [PID]")

            elif acao == "send":

                if len(comando) > 2:

                    try:

                        pid = int(comando[1])

                        mensagem = " ".join(comando[2:])

                        processo = next(
                            (p for p in tabela_processos if p.pid == pid),
                            None
                        )

                        if not processo:
                            print("[IPC] Processo não encontrado.")
                            continue

                        if pid not in memoria_compartilhada:
                            memoria_compartilhada[pid] = []

                        memoria_compartilhada[pid].append(mensagem)

                        print(f"[IPC] Mensagem enviada ao PID {pid}.")

                    except ValueError:
                        print("PID inválido.")

                else:
                    print("Uso correto: send [PID] [mensagem]")

            elif acao == "read":

                if len(comando) > 1:

                    try:

                        pid = int(comando[1])

                        if (
                            pid not in memoria_compartilhada
                            or not memoria_compartilhada[pid]
                        ):

                            print("[IPC] Nenhuma mensagem encontrada.")

                        else:

                            print(f"[IPC] Mensagens do PID {pid}:")

                            for msg in memoria_compartilhada[pid]:
                                print(f"- {msg}")

                    except ValueError:
                        print("PID inválido.")

                else:
                    print("Uso correto: read [PID]")
            else:
                print(f"bash: {acao}: comando não encontrado. Digite 'help'.")

        except KeyboardInterrupt:
            print("\nPor favor, use 'exit' para sair do PyOS.")


# ==========================================
# INÍCIO DO SISTEMA
# ==========================================

if __name__ == "__main__":
    boot()
    shell()