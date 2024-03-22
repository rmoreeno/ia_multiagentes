import pygame
import sys
import threading
import time
import random

running = True

################################ INICIALIZAÇÃO #################################
pygame.init()

################################ DEF. CONFIG. (IMAGENS, CORES E TAMANHOS) #################################
logo_mbv = pygame.image.load('logo.png')
cuidadora = pygame.image.load('cuidadora.png')
tecnica = pygame.image.load('tecnica.png')
enfermeira = pygame.image.load('enfermeira.png')
medico = pygame.image.load('medico.png')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (5, 36, 73)
BLUETWO = (185, 216, 234)

SCREEN_WIDTH, SCREEN_HEIGHT = 850, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hospital de Idosos")

################################ POSIÇÃO DOS QUARTOS #################################
quartos_posicoes = {
    0: (50, 50),
    1: (240, 50),
    2: (430, 50),
    3: (620, 50),
    4: (50, 430),
    5: (240, 430),
    6: (430, 430),
    7: (620, 430),
}

#Estado inicial dos agentes
estado_agentes = {
    'cuidadora': {'posicao': (350, 310), 'inicio': (350, 310), 'destino': None, 'icon': cuidadora, 'speed': 1, 'retornando': False},
    'tecnica': {'posicao': (400, 310), 'inicio': (400, 310), 'destino': None, 'icon': tecnica, 'speed': 1, 'retornando': False},
    'enfermeira': {'posicao': (450, 310), 'inicio': (450, 310), 'destino': None, 'icon': enfermeira, 'speed': 1, 'retornando': False},
    'medico': {'posicao': (500, 310), 'inicio': (500, 310), 'destino': None, 'icon': medico, 'speed': 1, 'retornando': False}
}

for agente in estado_agentes.values():
    agente.update({'atendendo': False, 'tempo_atendimento': 0})

################################ AMBIENTE #################################
# Quarto
def draw_room(x, y, width, height):
    # Paredes
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 5)
    # Porta
    pygame.draw.rect(screen, WHITE, (x + 120, y + (height) - 5, 30, 5))
    # Cama
    pygame.draw.rect(screen, BLUE, (x + 20, y + height - 40, 60, 25))
    # Armários
    pygame.draw.rect(screen, BLUETWO, (x + width - 50, y + 20, 20, 20)) 
    pygame.draw.rect(screen, BLUETWO, (x + width - 80, y + 20, 20, 20)) 

#  Posicionamento logo logística de atendimentos
def draw_logo():
    logo_width, logo_height = logo_mbv.get_size()
    logo_x = (SCREEN_WIDTH - logo_width) // 2
    logo_y = (SCREEN_HEIGHT - logo_height) // 2
    screen.blit(logo_mbv, (logo_x, logo_y))

################################ PACIENTES #################################
# Estrutura do paciente
class Paciente:
    def __init__(self, quarto, sinais_vitais):
        self.quarto = quarto
        self.sinais_vitais = sinais_vitais 

    def atualizar_sinais_vitais(self):
        self.sinais_vitais['pressao'] = random.randint(120, 180) 
        self.sinais_vitais['frequencia_cardiaca'] = random.randint(70, 120)

# Lista de pacientes
pacientes = [Paciente(quarto=i, sinais_vitais={'pressao': 120, 'frequencia_cardiaca': 80}) for i in range(8)]

# Atualizando sinais vitais de todos os pacientes
def atualizar_sinais_vitais_pacientes():
    while running:
        for paciente in pacientes:
            paciente.atualizar_sinais_vitais()
            pressao = paciente.sinais_vitais['pressao']
            frequencia_cardiaca = paciente.sinais_vitais['frequencia_cardiaca']
            if 121 <= pressao <= 150:
                estado_agentes['cuidadora']['destino'] = quartos_posicoes[paciente.quarto]
            elif 151 <= pressao <= 170:
                estado_agentes['tecnica']['destino'] = quartos_posicoes[paciente.quarto]
            elif pressao > 170 and frequencia_cardiaca > 110:
                estado_agentes['medico']['destino'] = quartos_posicoes[paciente.quarto] 
            elif pressao > 170 and frequencia_cardiaca < 110:
                estado_agentes['enfermeira']['destino'] = quartos_posicoes[paciente.quarto] 
        time.sleep(15)

threading.Thread(target=atualizar_sinais_vitais_pacientes, daemon=True).start()

# Mostrar sinais vitais na tela
def draw_vitals(x, y, sinais_vitais):
    font = pygame.font.SysFont(None, 14)
    pressao_text = font.render(f"Pressão: {sinais_vitais['pressao']}", True, BLACK)
    freq_text = font.render(f"Frequência: {sinais_vitais['frequencia_cardiaca']}", True, BLACK)
    screen.blit(pressao_text, (x, y))
    screen.blit(freq_text, (x, y + 20))

################################ AGENTES #################################  

#Movimentação dos agentes
def mover_agente(agente):
    if agente['retornando'] and agente['posicao'] == agente['inicio']:
        agente['retornando'] = False
        agente['atendendo'] = False
    elif agente['destino']:
        if not agente['atendendo']:
            agente['posicao'] = mover_agente_para(agente['posicao'], agente['destino'], agente['speed'])
            if agente['posicao'] == agente['destino'] and not agente['retornando']:
                agente['atendendo'] = True
                agente['tempo_atendimento'] = 10
        else:
            if agente['tempo_atendimento'] > 0:
                agente['tempo_atendimento'] -= 1
            else:
                agente['atendendo'] = False
                agente['destino'] = agente['inicio']
                agente['retornando'] = True

#Movimentação com posição desejada
def mover_agente_para(posicao_atual, posicao_destino, speed):
    x_atual, y_atual = posicao_atual
    x_destino, y_destino = posicao_destino

    if abs(x_destino - x_atual) > abs(y_destino - y_atual):
        if x_atual < x_destino:
            x_atual = min(x_atual + speed, x_destino)
        elif x_atual > x_destino:
            x_atual = max(x_atual - speed, x_destino)
    else:
        if y_atual < y_destino:
            y_atual = min(y_atual + speed, y_destino)
        elif y_atual > y_destino:
            y_atual = max(y_atual - speed, y_destino)

    return x_atual, y_atual

################################ MONITORAMENTO #################################  
thread_monitoramento = threading.Thread(target=atualizar_sinais_vitais_pacientes, daemon=True)
thread_monitoramento.start()

# Função que define o comportamento de cada agente
def comportamento_agente(icon, posicao_atual, quarto):
    posicao_destino = obter_posicao_quarto(quarto)
    while posicao_atual != posicao_destino:
        posicao_atual = mover_agente(posicao_atual, posicao_destino)
        time.sleep(0.1) 

# Função para obter a posição de um quarto pelo seu número
def obter_posicao_quarto(quarto_num):
    return quartos_posicoes[quarto_num]

# Função para os comportamentos das cuidadoras, técnicas e enfermeiras
def checar_paciente(agent_type, quarto):
    # Define o destino com base no quarto do paciente
    destino = obter_posicao_quarto(quarto)
    # Atualiza o estado do agente
    estado_agentes[agent_type]['destino'] = destino

################################ LÓGICA DE ATENDIMENTO #################################  
def monitorar_pacientes(frequencia_cardiaca, pressao):
    while running:
        for paciente in pacientes:
            pressao = paciente.sinais_vitais['pressao']
            if 121 <= pressao <= 150:
                checar_paciente('cuidadora', paciente.quarto)
            elif 151 <= pressao <= 170:
                checar_paciente('tecnica', paciente.quarto)
            elif pressao > 170 and frequencia_cardiaca < 110:
                checar_paciente('enfermeira', paciente.quarto)
            elif pressao > 170 and frequencia_cardiaca > 110:
                checar_paciente('medico', paciente.quarto)
        time.sleep(5) 

# Iniciar a thread de monitoramento
threading.Thread(target=monitorar_pacientes, daemon=True).start()

################################ AGENTE 1 = CUIDADORAS #################################  
    #Devem ir até o paciente quando a pressão estiver entre 130 e 150

################################ AGENTE 2 = TÉCNICAS #################################  
    #Devem ir até o paciente quando a pressão estiver entre 151 e 170

################################ AGENTE 3 = CUIDADORAS #################################  
    #Devem ir até o paciente quando a pressão estiver acima de 170

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    
    # Posicionamento quartos
    for i in range(4):
        draw_room(50 + i * 190, 50, 180, 120)
    for i in range(4):
        draw_room(50 + i * 190, 430, 180, 120)

    # Sala de espera
    draw_logo()

    for i, paciente in enumerate(pacientes):
        # Calcular a posição X e Y com base na posição do quarto
        if i < 4:
            x, y = 50 + i * 190, 50
        else:
            x, y = 50 + (i - 4) * 190, 430
        # Subtrai um valor de Y para mover o texto para cima na tela
        draw_vitals(x + 20, y + 20, paciente.sinais_vitais)

    # Mova os agentes e desenhe-os em suas posições atuais
    for agente in estado_agentes.values():
        mover_agente(agente)
        screen.blit(agente['icon'], agente['posicao'])

    # Atualiza a tela
    pygame.display.flip()

pygame.quit()
sys.exit()
