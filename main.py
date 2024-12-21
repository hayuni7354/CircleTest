import pygame
import math
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
GRAY = (127, 127, 127)

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

def angleSubtract(angle1, angle2): #angle1에서 angle2을 뺌 (라디안)
    sub = angle1 - angle2
    if(math.copysign(1, angle1) == math.copysign(1, angle2)): # 부호가 같거나 하나가 0이면
        return sub
    else:
        if(abs(angle1 - angle2) > math.pi):
            return (sub - math.copysign(2*math.pi, sub))
        else:
            return sub


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
        #모든 각은 라디안
        self.drawing = [] # 그린 위치들
        self.isDrawMode = False # 그리는 중 여부
        self.isDrawOverHalf = False # 원을 절반 넘게 그렸는지 여부
        self.isDrawClockwise = None # 그리는 방향이 시계방향인지 여부
        self.firstPointAngle = None # 중점에 대한 첫 위치의 편각
        self.lastPointAngle = None # 가장 그리는 방향으로 많이 돈 위치의 편각
    def event(self, event):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if(event.type == pygame.MOUSEBUTTONDOWN):
            if((mouse[0] - screen_height/2)**2 + abs(mouse[1] - screen_height/2)**2 < 90**2): # 중점에서 반경 90픽셀 원 안 -> 너무 가까움
                print('tooclose')
            self.__init__()
            self.isDrawMode = True
        if(event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION):
            if(click[0] and self.isDrawMode):
                if((mouse[0] - screen_height/2)**2 + abs(mouse[1] - screen_height/2)**2 < 30**2): # 중점에서 반경 30픽셀 원 안 -> 너무 가까움
                    print('tooclose')
                elif(not (40 < mouse[0] < screen_height - 50 and 40 < mouse[1] < screen_height - 50)): # 그릴수 있는 하얀 박스 밖 -> 너무 멂
                    print('toofar')
                else:
                    if(not self.drawing):
                        self.firstPointAngle = math.atan2(-(mouse[1] - screen_height/2), mouse[0] - screen_height/2)
                        self.lastPointAngle = self.firstPointAngle

                    # angle = 중점을 원점으로 한 좌표평면에서 마우스 좌표의 편각 (라디안)
                    angle = math.atan2(-(mouse[1] - screen_height/2), mouse[0] - screen_height/2)
                    # angleDiff = firstPointAngle과의 각 (도)
                    angleDiff = math.degrees(angleSubtract(angle, self.firstPointAngle))
                    if(self.isDrawClockwise is None):
                        if(angleDiff < -1): # +-1도 이상 벗어남 -> 도는방향 결정
                            self.isDrawClockwise = True
                        elif(angleDiff > 1):
                            self.isDrawClockwise = False
                    elif(175 < angleDiff < 185): # 180도 돔 (범위 +-5도)
                        self.isDrawOverHalf = True
                    
                    # angleDiff = lastPointAngle과의 각 (도)
                    angleDiff = math.degrees(angleSubtract(angle, self.lastPointAngle))
                    if(self.isDrawClockwise):
                        if(angleDiff < 0): # 도는방향과 같은방향으로 더 돌음 -> 값 업데이트
                            self.lastPointAngle = angle
                        if(angleDiff > 1): # 도는방향과 반대방향으로 1도 벗어남 -> 잘못된 방향
                            print('wrongway')
                    elif(self.isDrawClockwise is False):
                        if(angleDiff > 0):
                            self.lastPointAngle = angle
                        elif(angleDiff < -1):
                            print('wrongway')

                    self.drawing.append(mouse)
        if(event.type == pygame.MOUSEBUTTONUP):
            pass
    def draw(self):
        for i in range(len(self.drawing)): # 그림
            pygame.draw.circle(screen, WHITE, self.drawing[i], 10, 10)
            if(i != 0):
                pygame.draw.line(screen, WHITE, self.drawing[i-1], self.drawing[i], 24)
        pygame.draw.circle(screen, GRAY, [screen_height/2, screen_height/2], 10, 10) # 중점
        pygame.draw.rect(screen, WHITE, [30, 30, screen_height - 70, screen_height - 70], 3) # 그릴수 있는 하얀 박스
        pygame.draw.rect(screen, WHITE, [screen_width - 330, 30, 300, 600], 3) # 리더보드
        backButten = textButten("돌아가기", [screen_width - 180, 700], lambda: changeScene(titleScene)) # 돌아가기 버튼


#이벤트 루프
running = True #게임 진행 여부에 대한 변수 True : 게임 진행 중
game = titleScene()
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get(): #이벤트의 발생 여부에 따른 반복문
        if event.type == pygame.QUIT: #창을 닫는 이벤트가 발생했는가?
            running = False
        game.event(event) # 이벤트 발생시 처리
    screen.fill((0, 0, 0))

    #screen.blit(background, (0, 0)) #배경에 이미지 그려주고 위치 지정
    game.draw() # 화면 그리기 처리
    pygame.display.update()
    clock.tick(120)


#pygame 종료
pygame.quit()