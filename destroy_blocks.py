import os
import sys
import pygame
import traceback
from collections import deque
import random

os.chdir(os.path.dirname(__file__))

# Centralizar o jogo na tela do computador
if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

# Inicializar PyGame
pygame.init()

# Definir janela que ocorrerá o jogo
bg_main = pygame.image.load('main.png')  # Menu
background = pygame.image.load('8320.png')  # Jogo

# Definir largura e comprimento da tela do jogo
(width, height) = (750, 700)
screen = pygame.display.set_mode((width, height))

# Definir nome do jogo
pygame.display.set_caption("Destroy Blocks")

# Controlar o tempo de jogo e o FPS
clock = pygame.time.Clock()

# Algumas definições de fontes
font32 = pygame.font.SysFont("Indie Flower", 32)
font60 = pygame.font.SysFont("Indie Flower", 60)

# Arquivo .txt para guardar o Highest Score
file = open("hs.txt", "r")
highest_score = int(file.read().strip())
file.close()

# Algumas definições de cores
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BUTTON_PRESSED = (230, 194, 62)
BUTTON_NON_PRESSED = (255, 235, 161)


class Game:
    def __init__(self, player, time):
        self.blocks_type = deque()
        self.line_org = [0, 0, 0, 0]
        self.score_1 = 0
        self.score_2 = 0
        self.radius = 15
        self.stop = time * 1000 * 60

        # Inicialização para 1 jogador
        if player == 1:
            self.player1_x = 105
            self.player1_y = 635
            self.player2_x = None
            self.player2_y = None

        # Inicialização para 2 jogadores
        if player == 2:
            self.player1_x = 105
            self.player1_y = 590
            self.player2_x = 105
            self.player2_y = 655

    # Geração dos blocos a serem destruídos
    def blocks(self):
        for i in range(0, 2):
            self.line_org[2 * i + 1] = 1

        if self.blocks_type:
            if self.blocks_type[0][1][1] > height - 100:
                self.blocks_type.popleft()

            for elem in self.blocks_type:
                elem[1][1] = elem[1][1] + 1

                if self.line_org[2 * elem[3]] > 0 and self.line_org[2 * elem[3] + 1] == 1:
                    self.line_org[2 * elem[3]] = self.line_org[2 * elem[3]] - 1
                    self.line_org[2 * elem[3] + 1] = 0

                pygame.draw.rect(screen, elem[0], (elem[1][0], elem[1][1], elem[1][2], elem[1][3]))

        line = random.randrange(1, 7)  # Escolher randomicamente uma das 6 colunas onde surgem os blocos
        color = random.randrange(2)  # Escolher randomicamente cor Azul ou Vermelha para o bloco

        # Impedir sobreposição de blocos
        if self.line_org[2 * color] == 0:
            if self.blocks_type and self.blocks_type[-1][2] == line:
                return
            if color:
                block = [RED, [115 + 95 * (line - 1), 0, 45, 70], line, color]
            else:
                block = [BLUE, [115 + 95 * (line - 1), 0, 45, 70], line, color]

            self.blocks_type.append(block)
            self.line_org[2 * color] = 100
            pygame.draw.rect(screen, block[0], (block[1][0], block[1][1], block[1][2], block[1][3]))

    # Destruir blocos de o centro (x, y) do player estiver na região delimitada pelo bloco
    def destroy(self, x, y, player):
        isRemove = False
        for elem in self.blocks_type:
            if elem[1][0] < x < (elem[1][0] + elem[1][2]):
                if elem[1][1] < y < (elem[1][1] + elem[1][3]):
                    if player == elem[3] or (player - 2) == elem[3]:
                        isRemove = True  # Se atender as condições, remove o bloco
                        item = elem
                        # Aumentar a pontuação
                        if player == 1:
                            self.score_1 = self.score_1 + 1
                        if player == 2:
                            self.score_2 = self.score_2 + 1
                        break
        if isRemove:
            self.blocks_type.remove(item)

    # Semelhante as destroy, mas aqui perde ponto caso atinga o bloco da cor errada
    def to_dodge(self, x, y, player):
        isRemove = False
        for elem in self.blocks_type:
            if elem[1][0] < x < (elem[1][0] + elem[1][2]):
                if elem[1][1] < y < (elem[1][1] + elem[1][3]):
                    if not (player == elem[3] or (player - 2) == elem[3]):
                        isRemove = True
                        item = elem
                        # Desconta pontuação
                        if player == 1:
                            self.score_1 = self.score_1 - 1
                        if player == 2:
                            self.score_2 = self.score_2 - 1
                        break
        if isRemove:
            self.blocks_type.remove(item)

    # Mostrar quanto tempo falta para o fim da partida em formato de um retângulo
    def timer(self, start):
        y_time = (1 - (self.stop - (pygame.time.get_ticks()-start)) / self.stop) * 200
        pygame.draw.rect(screen, WHITE, (260, 60, 200, 20))
        pygame.draw.rect(screen, BLACK, (260, 60, y_time, 20))
        # Os 4 valores representam, respectivamente: x da origem, y da origem, comprimento e altura do retângulo

    def run(self):
        global highest_score
        running = True
        start = pygame.time.get_ticks()
        while self.stop > (pygame.time.get_ticks() - start) and running:
            screen.fill((0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(font60.render("HS: " + "{}".format(highest_score), True, (255, 255, 255)), (300, 20))

            # Background Image
            if self.player2_x is None:
                screen.blit(font60.render("P: " + "{}".format(self.score_1), True, (255, 0, 0)), (30, 20))
            else:
                screen.blit(font60.render("P1: " + "{}".format(self.score_1), True, (255, 0, 0)), (30, 20))
                screen.blit(font60.render("P2: " + "{}".format(self.score_2), True, (0, 0, 255)), (600, 20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            # Pegar informações do teclado para moviemwntar o player 1
            # Mover player 1 para a esquerda
            if keys[pygame.K_LEFT] and self.player1_x > 105:
                self.player1_x -= 1
            # Mover player 1 para a direita
            if keys[pygame.K_RIGHT] and self.player1_x < 660 - self.radius:
                self.player1_x += 1
            # Destruir bloco vermelho
            if keys[pygame.K_DOWN]:
                self.destroy(self.player1_x, self.player1_y, 1)

            self.to_dodge(self.player1_x, self.player1_y, 1)
            pygame.draw.circle(screen, RED, (self.player1_x, self.player1_y), self.radius)

            # Pegar informações do teclado para moviemwntar o player 2
            if self.player2_x is not None:
                # Mover player 2 para a esquerda
                if keys[pygame.K_a] and self.player2_x > 105:
                    self.player2_x -= 1
                # Mover player 2 para a direita
                if keys[pygame.K_d] and self.player2_x < 660 - self.radius:
                    self.player2_x += 1
                # Destruir bloco azul
                if keys[pygame.K_s]:
                    self.destroy(self.player2_x, self.player2_y, 2)

                self.to_dodge(self.player2_x, self.player2_y, 2)
                pygame.draw.circle(screen, BLUE, (self.player2_x, self.player2_y), self.radius)

            self.blocks()
            self.timer(start)
            pygame.display.update()
            clock.tick(200)  # Controla a velocidade do jogo

        return max(self.score_1, self.score_2)  # Retorna o maior score da partida


# Definir botões na tela inicial para configurar o jogo (jogadores e tempo de jogo)
def button(main_org):
    global highest_score
    mouse = pygame.mouse.get_pos()  # Determinar onde está o cursor do mouse
    click = pygame.mouse.get_pressed()  # Saber se houve click do mouse

    # Explorar cada evento no mouse ou no teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # Detectar se o cursor do mouse está dentro das regiões onde ficam os botões e executar ações quando clicar
        if 215 + 60 > mouse[0] > 215:
            if 320 + 60 > mouse[1] > 320:
                if click[0] == 1:
                    if main_org[1] == 0:
                        main_org[0] = 1
                        main_org[1] = 1
                        break
                    if main_org[1] == 1:
                        main_org[0] = 0
                        main_org[1] = 0
                        break
            if 400 + 60 > mouse[1] > 400:
                if click[0] == 1:
                    if main_org[1] == 0:
                        main_org[0] = 2
                        main_org[1] = 1
                        break
                    if main_org[1] == 1:
                        main_org[0] = 0
                        main_org[1] = 0
                        break
        if 565 + 60 > mouse[0] > 565:
            if 320 + 60 > mouse[1] > 320:
                if click[0] == 1:
                    if main_org[3] == 0:
                        main_org[2] = 1
                        main_org[3] = 1
                        break
                    if main_org[3] == 1:
                        main_org[2] = 0
                        main_org[3] = 0
                        break
            if 400 + 60 > mouse[1] > 400:
                if click[0] == 1:
                    if main_org[3] == 0:
                        main_org[2] = 2
                        main_org[3] = 1
                        break
                    if main_org[3] == 1:
                        main_org[2] = 0
                        main_org[3] = 0
                        break

        # Botão GO!: Dar início ao jogo se as opções de jogadores e tempo tiverem sido escolhidas
        if main_org[1] == 1 and main_org[3] == 1:
            if 345 + 60 > mouse[0] > 345 and 595 + 60 > mouse[1] > 535:
                if click[0] == 1:
                    if main_org[0] == 1:
                        player = 1
                    else:
                        player = 2
                    if main_org[2] == 1:
                        time = 1
                    else:
                        time = 2

                    game = Game(player, time)
                    score = game.run()

                    # Atualizar a nova pontuação máxima
                    if score > highest_score:
                        highest_score = score
    return True


def draw(main_org):
    screen.blit(bg_main, (0, 0))  # Background do menu inicial

    # Escrever o Highest Score na tela inicial
    screen.blit(font32.render("HIGHEST SCORE   {}".format(highest_score), True, (0, 0, 0)), (150, 620))

    # Colocar os botões na tela inicial
    if main_org[1] == 1:
        if main_org[0] == 1:
            pygame.draw.circle(screen, BUTTON_PRESSED, (245, 350), 30)
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 430), 30)
        if main_org[0] == 2:
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 350), 30)
            pygame.draw.circle(screen, BUTTON_PRESSED, (245, 430), 30)

    if main_org[1] == 0:
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 350), 30)
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 430), 30)

    if main_org[3] == 1:
        if main_org[2] == 1:
            pygame.draw.circle(screen, BUTTON_PRESSED, (595, 350), 30)
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 430), 30)
        if main_org[2] == 2:
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 350), 30)
            pygame.draw.circle(screen, BUTTON_PRESSED, (595, 430), 30)

    if main_org[3] == 0:
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 350), 30)
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 430), 30)

    pygame.display.update()  # Atualizar a tela sempre que escrever algo
    pygame.display.flip()


def main():
    main_org = [0, 0, 0, 0]  # Organizar a página inicial
    while True:
        if not button(main_org):
            break

        # Atualizar valor do Highest Score
        file = open("hs.txt", "w")
        file.write(str(highest_score))
        file.close()
        draw(main_org)


if __name__ == "__main__":
    try:
        main()

    except:
        traceback.print_exc()
        pygame.quit()
        input()
