import math

def angleSubtract(angle1, angle2): #angle1에서 angle2을 뺌
    if(math.copysign(1, angle1) == math.copysign(1, angle2)): # 부호가 같거나 하나가 0이면
        return (angle2 - angle1)
    else:
        if(abs(angle1 - angle2) > math.pi):
            return (angle2 - angle1 - math.copysign(2*math.pi, (angle2 - angle1)))
        else:
            return (angle2 - angle1)
        
print(angleSubtract(-7/8*math.pi, 7/8*math.pi))
print(angleSubtract(-1/8*math.pi, 1/8*math.pi))