import pygame
import math
import time
import numpy as np
from sortedcontainers import SortedList
import copy
pygame.init() #초기화

#화면 크기 설정
g_screen_width = 1280 # 가로 크기
g_screen_height = 1024 # 세로 크기
g_screen = pygame.display.set_mode((g_screen_width, g_screen_height), pygame.SCALED)

#화면 타이틀 설정
pygame.display.set_caption("CircleTest")

#폰트, 색상 설정
TITLEFONT = pygame.font.SysFont( "malgungothic", 50, True, False)
TEXTFONT = pygame.font.SysFont( "malgungothic", 30, False, False)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0) 
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (127, 127, 127)
LIGHT_RED = (255, 127, 127)

#게임 설정
MAXSCORE = 999 # 최대 점수

#전역변수들
g_bestAcc = 0 # 최고 정확도
g_bestDrawPoints = [] # 최고 정확도를 얻은 원
g_buttenCoolTime = 0 # 버튼 누르고 쿨타임

# numpy float 출력 옵션 변경(소수점 3자리까지 출력, array의 원소 값 자체가 변경되지는 않음)
#np.set_printoptions(precision=3, suppress=True)

#TODO : 마우스를 누른 채로 버튼 위로 올려도 버튼이 눌리는 문제 해결
class TextButten: # 글자 버튼
    def __init__(self, text, center, action = None, condition = True, size = [300,100]):
        if(condition):
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            color = None
            if(abs(mouse[0] - center[0]) < size[0]/2 and abs(mouse[1] - center[1]) < size[1]/2):
                global g_buttenCoolTime
                color = YELLOW
                if(click[0] and (action != None) and g_buttenCoolTime == 0):
                    g_buttenCoolTime = 30
                    time.sleep(0.001)
                    action()
            else:
                color = WHITE
        else:
            color = GRAY
        text_Title = TEXTFONT.render(text, True, color)
        text_Rect = text_Title.get_rect()
        text_Rect.center = center
        g_screen.blit(text_Title, text_Rect)
        pygame.draw.rect(g_screen, color, [center[0] - size[0]/2, center[1] - size[1]/2, size[0], size[1]], 3)

class ScoreBoard:
    def __init__(self):
        self.data = SortedList(key = lambda x: (-x['acc'] , x['id']))
        self.nextID = 0
    def __len__(self):
        return len(self.data)
    def add(self, acc, drawPoints, namePoints): # 정확도, 그림, 이름으로 점수 등록
        #self.data.add([-acc, drawPoints, namePoints, self.nextID])
        self.data.add({'acc' : acc, 'id' : self.nextID, 'drawPoints' : drawPoints, 'namePoints' : namePoints})
        self.nextID += 1
        return self.nextID
    def indexWhenInserted(self, acc): # acc가 점수표에 추가된다면 몇 등일지를 반환
        temp = {'acc' : acc, 'id' : -1, 'drawPoints' : [], 'namePoints' : []}
        self.data.add(temp)
        rank = self.data.bisect_left(temp) + 1 # 1등부터 시작
        self.data.remove(temp)
        return rank
    def rangeQuery(self, m, n): # m등부터 n등까지의 값 반환 (m,n등 포함, m<n), 누락된 등수는 None으로 채움
        temp = list(self.data.islice(m - 1, n)) # ex: 1등~5등 -> 0,1,2,3,4
        for i in range(len(temp), n - m + 1):
            temp.append(None)
        return temp



g_scoreBoard = ScoreBoard()

def changeScene(scene): # 인자는 인스턴스가 아닌 클래스로 주어져야 한다
    global g_game
    g_game = scene()
    pygame.display.flip()

def angleSubtract(angle1, angle2): #angle1에서 angle2을 뺌 (라디안)
    sub = angle1 - angle2
    if(math.copysign(1, angle1) == math.copysign(1, angle2)): # 부호가 같거나 하나가 0이면
        return sub
    else:
        if(abs(angle1 - angle2) > math.pi): # 각의 차이가 180도를 넘으면
            return (sub - math.copysign(2*math.pi, sub)) # 특수한 경계 넘었다고 생각, 보정
        else:
            return sub
        
def toScore(acc):
    if(0.8 < acc < 1):
        score = -100*math.log2(5*(1-acc))
        if(score > MAXSCORE):
            return MAXSCORE
        else:
            return score
    elif(acc == 1):
        return MAXSCORE
    else:
        return 0


class TitleScene: # 타이틀 화면
    def __init__(self):
        pass
    def event(self, event):
        pass
    def draw(self):
        # 타이틀
        text_Title = TITLEFONT.render("Circle Test - 가장 완벽한 원을 그려라!", True, WHITE)
        text_Rect = text_Title.get_rect()
        text_Rect.centerx = round(g_screen_width/2)
        text_Rect.y = 50
        g_screen.blit(text_Title, text_Rect)
        pygame.draw.circle(g_screen, WHITE, (g_screen_width/2, 300), 100, 5)

        # 버튼들
        startButten = TextButten("시작하기!", [g_screen_width/2, 675], lambda: changeScene(IngameScene))
        boardButten = TextButten("점수판", [g_screen_width/2 + 350, 675], lambda: changeScene(ScoreBoardScene))
        creditButten = TextButten("크레딧", [g_screen_width/2 - 350, 675])

class IngameScene: # 인게임 화면
    def __init__(self):
        self.drawPoints = [] # 그린 위치들
        self.calcPoints = [] # 계산되는 위치들

        self.isDrawMode = False # 그리는 중 여부
        self.gameEndID = -1 # 게임 종료 아이디 (-1 : 게임중 or 초기상태 / 0 : 정상종료 / 1 : 너무 가까움 / 2 : 상자 벗어남 / 3 : 잘못된 방향 / 4 : 그리다 멈춤)
        self.isNewRecord = False # 게임 종료시 신기록 달성 여부

        #모든 각은 라디안
        self.isDrawOverHalf = False # 원을 절반 넘게 그렸는지 여부
        self.isDrawClockwise = None # 그리는 방향이 시계방향인지 여부
        self.firstPointAngle = None # 중점에 대한 첫 위치의 편각
        self.lastPointAngle = None # 가장 그리는 방향으로 많이 돈 위치의 편각

    def event(self, event):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if(event.type == pygame.MOUSEBUTTONDOWN and (40 < mouse[0] < g_screen_height - 100 and 40 < mouse[1] < g_screen_height - 100)):
            if((mouse[0] - g_screen_height/2)**2 + abs(mouse[1] - g_screen_height/2)**2 < 90**2): # 중점에서 반경 90픽셀 원 안 -> 너무 가까움
                self.gameEndID = 1
                self.isDrawMode = False
            self.__init__()
            self.isDrawMode = True
        if(event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION):
            if(click[0] and self.isDrawMode):
                if((mouse[0] - g_screen_height/2)**2 + abs(mouse[1] - g_screen_height/2)**2 < 30**2): # 중점에서 반경 30픽셀 원 안 -> 너무 가까움
                    self.gameEndID = 1
                    self.isDrawMode = False
                elif(not (40 < mouse[0] < g_screen_height - 100 and 40 < mouse[1] < g_screen_height - 100)): # 그릴수 있는 하얀 박스 밖 -> 상자 벗어남
                    self.gameEndID = 2
                    self.isDrawMode = False
                else:
                    if(not self.drawPoints):
                        self.firstPointAngle = math.atan2(-(mouse[1] - g_screen_height/2), mouse[0] - g_screen_height/2)
                        self.lastPointAngle = self.firstPointAngle

                    # angle = 중점을 원점으로 한 좌표평면에서 마우스 좌표의 편각 (라디안)
                    angle = math.atan2(-(mouse[1] - g_screen_height/2), mouse[0] - g_screen_height/2)
                    # angleDiff = firstPointAngle과의 각 (도)
                    angleDiff = math.degrees(angleSubtract(angle, self.firstPointAngle))
                    if(self.isDrawClockwise is None):
                        if(angleDiff < -1): # +-1도 이상 벗어남 -> 도는방향 결정
                            self.isDrawClockwise = True
                        elif(angleDiff > 1):
                            self.isDrawClockwise = False
                    elif(170 < angleDiff or angleDiff < -170): # 180도 돔 (범위 +-10도)
                        self.isDrawOverHalf = True
                    # 한바퀴에서 10도 초과로 넘침 -> 다 그린 것으로
                    if(self.isDrawOverHalf):
                        if(self.isDrawClockwise and -165 < angleDiff < -10):
                            self.gameEnd0()
                        elif(self.isDrawClockwise is False and 165 > angleDiff > 10):
                            self.gameEnd0()
                    
                    # angleDiff = lastPointAngle과의 각 (도)
                    angleDiff = math.degrees(angleSubtract(angle, self.lastPointAngle))
                    if(self.isDrawClockwise):
                        if(angleDiff < 0): # 도는방향과 같은방향으로 더 돌음 -> 값 업데이트
                            self.lastPointAngle = angle
                        if(angleDiff > 1): # 도는방향과 반대방향으로 1도 벗어남 -> 잘못된 방향
                            self.gameEndID = 3
                            self.isDrawMode = False
                    elif(self.isDrawClockwise is False):
                        if(angleDiff > 0):
                            self.lastPointAngle = angle
                        elif(angleDiff < -1):
                            self.gameEndID = 3
                            self.isDrawMode = False

                    # 그린 점 추가
                    self.calcPoints.append([mouse[0] - g_screen_height/2, -(mouse[1] - g_screen_height/2)])
                    if(self.drawPoints):
                        #직전 점과 거리 멀 경우 -> 2픽셀당 점 1개씩 추가
                        pCount = ((self.drawPoints[-1][0] - mouse[0])**2 + (self.drawPoints[-1][1] - mouse[1])**2)**0.5 // 2
                        for i in range(1, int(pCount + 1)):
                            #그리는 점과 직전 점을 i : (pCount - i)로 내분
                            coord = [(i*self.drawPoints[-1][0] + (pCount - i)*mouse[0])/pCount, (i*self.drawPoints[-1][1] + (pCount - i)*mouse[1])/pCount]
                            self.calcPoints.append([coord[0] - g_screen_height/2, -(coord[1] - g_screen_height/2)])
                    self.drawPoints.append(mouse)

        if(event.type == pygame.MOUSEBUTTONUP and self.isDrawMode):
            if(self.isDrawOverHalf):
                # angle = 중점을 원점으로 한 좌표평면에서 마우스 좌표의 편각 (라디안)
                angle = math.atan2(-(mouse[1] - g_screen_height/2), mouse[0] - g_screen_height/2)
                # angleDiff = firstPointAngle과의 각 (도)
                angleDiff = math.degrees(angleSubtract(angle, self.firstPointAngle))

                # 한바퀴에서 10도 미만으로 모자람 -> 다 그린 것으로
                if(self.isDrawClockwise and angleDiff < 10):
                    self.gameEnd0()
                    return
                elif(self.isDrawClockwise is False and angleDiff > -10):
                    self.gameEnd0()
                    return
            self.gameEndID = 4 # 다안그렸는데 뗌 -> 그리다 멈품
            self.isDrawMode = False

    def draw(self):
        for i in range(len(self.drawPoints)): # 그림
            pygame.draw.circle(g_screen, WHITE, self.drawPoints[i], 10, 10)
            if(i != 0):
               pygame.draw.line(g_screen, WHITE, self.drawPoints[i-1], self.drawPoints[i], 24)
        #for i in range(len(self.calcPoints)): # 계산된 점 그림(디버그용)
        #    pygame.draw.circle(screen, [255,255,0], [self.calcPoints[i][0] + screen_height/2, screen_height/2 - self.calcPoints[i][1]], 1, 1)
        pygame.draw.circle(g_screen, GRAY, [g_screen_height/2, g_screen_height/2], 10, 10) # 중점
        pygame.draw.rect(g_screen, WHITE, [30, 30, g_screen_height - 120, g_screen_height - 120], 3) # 그릴수 있는 하얀 박스

        # 정확도 글자
        acc = self.getAcc()
        color = None
        if(self.isNewRecord): color = RED
        else: color = GREEN
        if(not math.isnan(acc)):
            #TODO : 텍스트 관련 변수들 이름 앞 acc 제거
            accText = TEXTFONT.render(f'{math.floor(self.getAcc()*1000)/10}%', True, color)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2 - 5
            accTextRect.centery = g_screen_height/2 - 50
            g_screen.blit(accText, accTextRect)

        if(self.gameEndID == 0):
        #if(not math.isnan(acc)):
            accText = TEXTFONT.render(f'{math.floor(toScore(self.getAcc()))}점', True, color)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2
            accTextRect.centery = g_screen_height/2 + 50
            g_screen.blit(accText, accTextRect)

            if(self.isNewRecord):
                accText = TEXTFONT.render('NEW RECORD!', True, color)
                accTextRect = accText.get_rect()
                accTextRect.centerx = g_screen_height/2
                accTextRect.centery = g_screen_height/2 + 100
                g_screen.blit(accText, accTextRect)

                accText = TEXTFONT.render('점수를 저장하려면 점수등록 버튼을 눌러주세요', True, RED)
                accTextRect = accText.get_rect()
                accTextRect.centerx = g_screen_height/2
                accTextRect.centery = g_screen_height/2 + 180
                g_screen.blit(accText, accTextRect)

        elif(self.gameEndID == -1 and not self.isDrawMode):
            accText = TEXTFONT.render('회색 점을 중심으로 여기에 그려주세요', True, WHITE)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2
            accTextRect.centery = g_screen_height/2 + 50
            g_screen.blit(accText, accTextRect)
        elif(self.gameEndID == 1):
            accText = TEXTFONT.render('점과 거리를 두고 그려주세요', True, LIGHT_RED)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2
            accTextRect.centery = g_screen_height/2 + 50
            g_screen.blit(accText, accTextRect)
        elif(self.gameEndID == 2):
            accText = TEXTFONT.render('흰 상자 안에 그려주세요', True, LIGHT_RED)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2
            accTextRect.centery = g_screen_height/2 + 50
            g_screen.blit(accText, accTextRect)
        elif(self.gameEndID == 3):
            accText = TEXTFONT.render('한쪽 방향으로만 그려주세요', True, LIGHT_RED)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2
            accTextRect.centery = g_screen_height/2 + 50
            g_screen.blit(accText, accTextRect)
        elif(self.gameEndID == 4):
            accText = TEXTFONT.render('원을 끝까지 그려주세요', True, LIGHT_RED)
            accTextRect = accText.get_rect()
            accTextRect.centerx = g_screen_height/2
            accTextRect.centery = g_screen_height/2 + 50
            g_screen.blit(accText, accTextRect)

        pygame.draw.rect(g_screen, WHITE, [g_screen_width - 330, 30, 300, 600], 3) # 리더보드
        backButten = TextButten("돌아가기", [g_screen_width - 180, 700], lambda: changeScene(TitleScene)) # 돌아가기 버튼
        postScoreButten = TextButten("점수등록", [g_screen_width - 180, 820], lambda: changeScene(PostScoreScene), self.gameEndID == 0) # 점수등록 버튼

    def getAcc(self): # calcPoints로 정확도를 계산하는 함수
        if(len(self.calcPoints) <= 1):
            return math.nan
        distances = []
        for i in range(len(self.calcPoints)):
            distances.append((self.calcPoints[i][0]**2 + self.calcPoints[i][1]**2)**0.5)
        return 1 - np.std(distances)/np.mean(distances)
    
    def gameEnd0(self): # 게임 정상 종료 시 처리를 하는 함수
        self.gameEndID = 0
        self.isDrawMode = False
        acc = self.getAcc()
        global g_bestAcc
        global g_bestDrawPoints
        if(acc > g_bestAcc):
            self.isNewRecord = True
            g_bestAcc = acc
            g_bestDrawPoints = self.drawPoints

class PostScoreScene: # 점수등록 화면
    def __init__(self):
        self.namePoints = [] # 이름 쓴 위치들
        self.rank = g_scoreBoard.indexWhenInserted(g_bestAcc) # 최고점수가 추가될 경우의 순위
    def event(self, event):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if(event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION):
            if(click[0]):
                if((40 < mouse[0] < 780 and 660 < mouse[1] < 900 and len(self.namePoints) < 10000)): # 그릴수 있는 하얀 박스 밖 -> 상자 벗어남
                    # 그린 점 추가
                    self.namePoints.append([mouse[0] - 30, mouse[1] - 650])
    def draw(self):
        for i in range(len(g_bestDrawPoints)): # 그림(1/2 축척, (15,15) 평행이동)
            pygame.draw.circle(g_screen, WHITE, [g_bestDrawPoints[i][0]/2 + 15, g_bestDrawPoints[i][1]/2+ 15], 5, 5)
            if(i != 0):
               pygame.draw.line(g_screen, WHITE, [g_bestDrawPoints[i-1][0]/2 + 15, g_bestDrawPoints[i-1][1]/2 + 15], [g_bestDrawPoints[i][0]/2 + 15, g_bestDrawPoints[i][1]/2 + 15], 12)
        pygame.draw.circle(g_screen, GRAY, [g_screen_height/4 + 15, g_screen_height/4 + 15], 5, 5) # 중점
        pygame.draw.rect(g_screen, WHITE, [30, 30, (g_screen_height - 70)/2  + 15, (g_screen_height - 70)/2 + 15], 3) # 그릴수 있는 하얀 박스(였던것)

        accText = TITLEFONT.render(f'최고 정확도 : {math.floor(g_bestAcc*1000)/10}%', True, WHITE)
        g_screen.blit(accText, ((g_screen_height - 70)/2 + 80, 100))
        accText = TITLEFONT.render(f'최고 점수 : {math.floor(toScore(g_bestAcc))}점', True, WHITE)
        g_screen.blit(accText, ((g_screen_height - 70)/2 + 80, 180))
        accText = TITLEFONT.render(f'현재 순위 : {self.rank}등', True, WHITE)
        g_screen.blit(accText, ((g_screen_height - 70)/2 + 80, 260))

        accText = TITLEFONT.render('이름을 써 주세요', True, WHITE)
        g_screen.blit(accText, (50, 550))
        pygame.draw.rect(g_screen, WHITE, [30, 650, 760, 260], 3) #이름 쓰는 하얀 박스
        for i in range(len(self.namePoints)): # 이름
            pygame.draw.circle(g_screen, WHITE, [self.namePoints[i][0] + 30, self.namePoints[i][1] + 650], 5, 5)

        nameResetButten = TextButten("이름 초기화", [g_screen_width - 180, 580], lambda: self.resetName()) # 이름리셋 버튼
        backButten = TextButten("돌아가기", [g_screen_width - 180, 700], lambda: changeScene(IngameScene)) # 돌아가기 버튼
        postScoreButten = TextButten("이름등록", [g_screen_width - 180, 820], lambda: self.postScore(), self.namePoints) # 등록완료 버튼
    def resetName(self):
        self.namePoints = []
    def postScore(self): # 점수 등록
        global g_scoreBoard
        global g_bestAcc
        global g_bestDrawPoints
        g_scoreBoard.add(g_bestAcc, g_bestDrawPoints, self.namePoints)
        g_bestAcc = 0
        g_bestDrawPoints = []
        print(len(self.namePoints))
        changeScene(TitleScene)

class ScoreBoardScene():
    def __init__(self):
        self.page = 1 # 1부터 시작
        self.maxPage = len(g_scoreBoard) // 6
        if(self.maxPage < 1): self.maxPage = 1
        self.viewingScores = g_scoreBoard.rangeQuery(1,6)
    def event(self, event):
        pass
    def draw(self):
        backButten = TextButten("돌아가기", [g_screen_width - 180, 920], lambda: changeScene(TitleScene)) # 돌아가기 버튼
        # 페이지 이동 버튼들 (<<, <, >, >>)
        TextButten("<<", [80, 920], lambda: self.addPageNum(-10), True, [100, 100])
        TextButten("<", [210, 920], lambda: self.addPageNum(-1), True, [100, 100])
        TextButten(">", [340, 920], lambda: self.addPageNum(1), True, [100, 100])
        TextButten(">>", [470, 920], lambda: self.addPageNum(10), True, [100, 100])

        text = TITLEFONT.render(f'{self.page} / {self.maxPage}', True, YELLOW) # 순위
        textRect = text.get_rect()
        textRect.centerx = 735
        textRect.centery = 920
        g_screen.blit(text, textRect)

        pygame.draw.rect(g_screen, WHITE, [30, 30, g_screen_width - 60, g_screen_height - 220], 3) # 점수표 상자
        for i in range(6):
            if(not self.viewingScores[i] is None): # None일 경우 누락된 순위 -> 표시 X
                text = TITLEFONT.render(f'{6*(self.page - 1) + i + 1}', True, YELLOW) # 순위
                textRect = text.get_rect()
                textRect.centerx = 130
                textRect.y = 90 + 120*i
                g_screen.blit(text, textRect)

            
                name = self.viewingScores[i]['namePoints']
                pygame.draw.rect(g_screen, WHITE, [230, 90 + 120*i, 760/3, 260/3], 3) # 이름 상자
                for j in range(len(name)): # 이름
                    pygame.draw.circle(g_screen, WHITE, [name[j][0]/3 + 230, name[j][1]/3 + 90 + 120*i], 2, 2)

                draw = self.viewingScores[i]['drawPoints']
                pygame.draw.circle(g_screen, GRAY, [590 + 260/3*(512/934), 90 + 260/3*(512/934) + 120*i], 1, 1) # 중점
                pygame.draw.rect(g_screen, WHITE, [590, 90 + 120*i, 260/3, 260/3], 3) # 그림 상자
                for j in range(len(draw)): # 그림
                    pygame.draw.circle(g_screen, WHITE, [(draw[j][0] - 30)*260/((g_screen_height - 120)*3) + 590, (draw[j][1] - 30)*260/((g_screen_height - 120)*3) + 90 + 120*i], 2, 2)

                text = TITLEFONT.render(f'{math.floor(toScore(self.viewingScores[i]["acc"]))}점', True, WHITE) # 점수
                textRect = text.get_rect()
                textRect.centerx = 850
                textRect.y = 90 + 120*i
                g_screen.blit(text, textRect)

                text = TITLEFONT.render(f'{math.floor(self.viewingScores[i]["acc"]*1000)/10}%', True, WHITE) # 정확도
                textRect = text.get_rect()
                textRect.centerx = 1080
                textRect.y = 90 + 120*i
                g_screen.blit(text, textRect)
    def addPageNum(self, num): # num이 양수면 오른쪽으로, 음수면 왼쪽으로 절댓값만큼 점수표 넘김
        self.page += num
        if(self.page < 1):
            self.page = 1
        if(self.page > self.maxPage):
            self.page = self.maxPage
        self.viewingScores = g_scoreBoard.rangeQuery(6*(self.page - 1) + 1, 6*(self.page - 1) + 6)


#이벤트 루프
g_running = True #게임 진행 여부에 대한 변수 True : 게임 진행 중
g_game = TitleScene()
g_clock = pygame.time.Clock()

while g_running:
    for event in pygame.event.get(): #이벤트의 발생 여부에 따른 반복문
        if event.type == pygame.QUIT: #창을 닫는 이벤트가 발생했는가?
            g_running = False
        g_game.event(event) # 이벤트 발생시 처리
    g_screen.fill((0, 0, 0))

    #screen.blit(background, (0, 0)) #배경에 이미지 그려주고 위치 지정
    g_game.draw() # 화면 그리기 처리
    pygame.display.update()
    if(g_buttenCoolTime > 0):
        g_buttenCoolTime -= 1
    g_clock.tick(120)


#pygame 종료
pygame.quit()