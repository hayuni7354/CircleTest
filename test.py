import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# 다각형의 꼭짓점들 (polygon 배열)
polygon = np.array([
    [1, 2],  # 점 1
    [2, 1],  # 점 2
    [2, -1],  # 점 3
    [1, -4],  # 점 4
    [-1, -2],  # 점 1
    [-2, -1],  # 점 2
    [-2, 4],  # 점 3
    [-1, 3],  # 점 4
    
])

# 두 점 사이를 일정 간격으로 나누는 함수
def generate_points_on_edge(p1, p2, num_points=10):
    """ 두 점 p1, p2 사이에 num_points 개의 점을 생성 """
    x_vals = np.linspace(p1[0], p2[0], num_points)
    y_vals = np.linspace(p1[1], p2[1], num_points)
    return np.vstack([x_vals, y_vals]).T

# 다각형의 변을 따라 점을 생성
def generate_points_from_polygon(polygon, num_points_per_edge=10):
    points = []
    n = len(polygon)
    for i in range(n):
        # 각 변을 정의 (꼭짓점 i와 i+1을 잇는 변)
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        points_on_edge = generate_points_on_edge(p1, p2, num_points=num_points_per_edge)
        points.append(points_on_edge)
    return np.vstack(points)

# 중심이 원점인 원에 피팅할 함수 (반지름을 찾기 위해)
def residuals(params, points):
    r = params[0]  # 원의 반지름 r (중심은 (0, 0)으로 고정)
    distances = np.sqrt(points[:, 0]**2 + points[:, 1]**2)  # 각 점과 원점 (0,0)까지의 거리 계산
    return distances - r  # 거리와 반지름의 차이를 계산

# 최소 제곱법을 사용하여 반지름을 찾음
def fit_circle_to_polygon(polygon, num_points_per_edge=10):
    # 다각형의 변 위의 점들도 포함하여 점들을 생성
    points = generate_points_from_polygon(polygon, num_points_per_edge)

    # 다각형의 모든 점들로부터 초기 추정값을 계산
    r_init = np.mean(np.sqrt(points[:, 0]**2 + points[:, 1]**2))  # 원점 (0, 0)에서 각 점까지의 평균 거리로 초기화

    # 최소 제곱법을 사용하여 원의 반지름을 추정 (중심은 (0, 0)으로 고정)
    result = least_squares(residuals, [r_init], args=(points,))
    
    # 원의 반지름 r 반환
    r = result.x[0]
    return r, points

# 원에 맞는 반지름을 찾고, 다각형 점들과 변 위의 점들을 생성
radius, all_points = fit_circle_to_polygon(polygon)

# 시각화
def plot_polygon_and_circle(polygon, radius, points):
    fig, ax = plt.subplots()

    # 다각형 그리기
    polygon = np.vstack([polygon, polygon[0]])  # 다각형을 닫히도록 마지막 점을 첫 점에 추가
    ax.plot(polygon[:, 0], polygon[:, 1], 'b-', label='Polygon (Vertices)', linewidth=2)

    # 변 위의 점들 그리기
    ax.scatter(points[:, 0], points[:, 1], c='orange', s=10, label='Points on edges', alpha=0.7)

    # 원 그리기 (중심이 (0, 0)인 원)
    circle = plt.Circle((0, 0), radius, color='r', fill=False, linestyle='--', label='Fitted Circle')
    ax.add_artist(circle)

    # 원점 그리기
    ax.plot(0, 0, 'go', label='Center of Fitted Circle')

    # 축 설정
    ax.set_aspect('equal', 'box')
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Polygon and Fitted Circle (Centered at (0, 0))')

    plt.grid(True)
    plt.show()

# 시각화 함수 호출
plot_polygon_and_circle(polygon, radius, all_points)
