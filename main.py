import pygame
import numpy as np
import time
pygame.init() #초기화

#화면 크기 설정
screen_width = 1200 #가로 크기
screen_height = 900 #세로 크기
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED)

#화면 타이틀 설정
pygame.display.set_caption("CircleTest")

#폰트, 색상 설정
titleFont = pygame.font.SysFont( "malgungothic", 50, True, False)
textFont = pygame.font.SysFont( "malgungothic", 30, False, False)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# numpy float 출력 옵션 변경(소수점 3자리까지 출력, array의 원소 값 자체가 변경되지는 않음)
#np.set_printoptions(precision=3, suppress=True)

class textButten: # 글자 버튼
    def __init__(self, text, center, action = None, size = [300,100]):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        color = None
        if(abs(mouse[0] - center[0]) < size[0]/2 and abs(mouse[1] - center[1]) < size[1]/2):
            color = YELLOW
            if(click[0] and (action != None)):
                time.sleep(0.001)
                action()
        else:
            color = WHITE
        text_Title = textFont.render(text, True, color)
        text_Rect = text_Title.get_rect()
        text_Rect.center = center
        screen.blit(text_Title, text_Rect)
        pygame.draw.rect(screen, color, [center[0] - size[0]/2, center[1] - size[1]/2, size[0], size[1]], 3)



def changeScene(scene): # 인자는 인스턴스가 아닌 클래스로 주어져야 한다
    global game
    game = scene()
    pygame.display.flip()



class titleScene: # 타이틀 화면
    def __init__(self):
        pass
    def event(self, event):
        pass
    def draw(self):
        # 타이틀
        text_Title = titleFont.render("Circle Test - 가장 완벽한 원을 그려라!", True, WHITE)
        text_Rect = text_Title.get_rect()
        text_Rect.centerx = round(screen_width/2)
        text_Rect.y = 50
        screen.blit(text_Title, text_Rect)
        pygame.draw.circle(screen, WHITE, (screen_width/2, 300), 100, 5)

        # 버튼들
        startButten = textButten("시작하기!", [screen_width/2, 675], lambda: changeScene(ingameScene))
        boardButten = textButten("점수판", [screen_width/2 + 350, 675])
        htpButten = textButten("게임 방법", [screen_width/2 - 350, 675])

class ingameScene: # 인게임 화면
    def __init__(self):
        pass
    def event(self, event):
        if event.type == pygame.MOUSEMOTION:
            print('1')
    def draw(self):
        pygame.draw.rect(screen, WHITE, [screen_width - 330, 30, 300, 600], 3)
        backButten = textButten("돌아가기", [screen_width - 180, 700], lambda: changeScene(titleScene))



#이벤트 루프
running = True #게임 진행 여부에 대한 변수 True : 게임 진행 중
game = titleScene()
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get(): #이벤트의 발생 여부에 따른 반복문
        if event.type == pygame.QUIT: #창을 닫는 이벤트가 발생했는가?
            running = False
        game.event(event)
    screen.fill((0, 0, 0))

    #screen.blit(background, (0, 0)) #배경에 이미지 그려주고 위치 지정
    game.draw()
    pygame.display.update()
    clock.tick(120)


#pygame 종료
pygame.quit()