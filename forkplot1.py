import matplotlib.pyplot as plt
import math
import time

segments = []

with open("segments_for_geogebra.txt", "r") as file:
    for line in file:
        line = line.strip()
        if not line.startswith("Segment[") or not line.endswith("]"):
            continue 
        coords_part = line[len("Segment["):-1]
        points = coords_part.split('), (')
        try:
            p1 = points[0].replace('(', '').replace(')', '')
            p2 = points[1].replace('(', '').replace(')', '')
            x1, y1 = map(float, p1.split(','))
            x2, y2 = map(float, p2.split(','))
            segments.append(((x1, y1), (x2, y2)))
        except (ValueError, IndexError):
            continue  

def draw_background(alert=False):
    plt.xlim(-15, 15)
    plt.ylim(-15, 15)
    plt.axhline(0, color="black")
    plt.axvline(0, color="black")
    ax = plt.gca()
    ax.set_facecolor('lightcoral' if alert else 'white')
    for val in [15, -15]:
        plt.axhline(val, linestyle="dashed", color="red")
        plt.axvline(val, linestyle="dashed", color="red")

def calculate_angle(p1, p2, p3):
    """Üç nokta arasındaki açıyı hesaplar (radyan cinsinden)"""
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    det = v1[0] * v2[1] - v1[1] * v2[0]
    angle = math.atan2(det, dot)
    return angle if angle >= 0 else angle + 2 * math.pi

def distance(p, q):
    return math.sqrt((p[0] - q[0])**2 + (p[1] - q[1])**2)

DISTANCE_THRESHOLD = 0.8
ANGLE_THRESHOLD = 0.05
step_counter = 0
alert_counter = 0
# Forklift animation
for i in range(0, len(segments), 2):
    plt.cla() 
    step_counter += 1
    seg1 = segments[i]
    x1, y1 = zip(*seg1)
    A = (x1[0], y1[0])
    B = (x1[1], y1[1])

    alert_condition = False

    if i + 1 < len(segments):
        seg2 = segments[i + 1]
        x2, y2 = zip(*seg2)
        C = (x2[0], y2[0])
        D = (x2[1], y2[1])

        # Angles
        angle_CAD = calculate_angle(C, A, D)
        angle_DBC = calculate_angle(D, B, C)
        angle_ACB = calculate_angle(A, C, B)
        angle_BDA = calculate_angle(B, D, A)

        ta = math.tan(angle_CAD)
        tb = math.tan(angle_DBC)
        tc = math.tan(angle_ACB)
        td = math.tan(angle_BDA)

        m = ta * tc * td
        n = tb * tc * td

        # Angle treshold
        if abs(m) > ANGLE_THRESHOLD or abs(n) > ANGLE_THRESHOLD:
            alert_condition = True

        # Dist treshold
        for p1 in [A, B]:
            for p2 in [C, D]:
                if distance(p1, p2) < DISTANCE_THRESHOLD:
                    alert_condition = True
        if alert_condition:
            alert_counter += 1
        # Infobox
        info = (
            f"Step: {step_counter}, Alerts: {alert_counter}\n\n"
            f"ta (tan(CAD)) = {ta:.2f}\n"
            f"tb (tan(DBC)) = {tb:.2f}\n"
            f"tc (tan(ACB)) = {tc:.2f}\n"
            f"td (tan(BDA)) = {td:.2f}\n"
            f"m = {m:.2f}, n = {n:.2f}\n"
        )
        for p1 in [A, B]:
            for p2 in [C, D]:
                info += f"dist({p1}, {p2}) = {distance(p1, p2):.2f}\n"

        plt.text(-14, 14, info, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

    # Drawing
    draw_background(alert=alert_condition)
    plt.plot(x1, y1, marker='o', color='blue', label='Forklift 1 (A-B)')
    plt.text(A[0], A[1], 'A', fontsize=12, ha='right', va='bottom', color='red')
    plt.text(B[0], B[1], 'B', fontsize=12, ha='right', va='bottom', color='red')

    if i + 1 < len(segments):
        plt.plot(x2, y2, marker='o', color='green', label='Forklift 2 (C-D)')
        plt.text(C[0], C[1], 'C', fontsize=12, ha='right', va='bottom', color='red')
        plt.text(D[0], D[1], 'D', fontsize=12, ha='right', va='bottom', color='red')

    plt.title(f"Adım {i // 2 + 1}")
    plt.legend()
    plt.pause(0.001)

plt.show()

print(f"Total step: {step_counter}")
print(f"Total alert: {alert_counter}")