import matplotlib.pyplot as plt
import numpy as np
import math

segments = []

with open("segments_for_geogebra_short.txt", "r") as file:
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

def noisy_point(p1, p2, target_distance):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    norm = math.hypot(dx, dy)
    if norm == 0:
        return p1
    dx /= norm
    dy /= norm
    return (p1[0] + dx * target_distance, p1[1] + dy * target_distance)

def simulate_noisy_measurement(p1, p2):
    true_dist = distance(p1, p2)
    noisy_dist = np.random.normal(loc=true_dist, scale=0.5)
    return noisy_point(p1, p2, noisy_dist), true_dist

def angular_error(true_angle, noisy_angle):
    error = abs(true_angle - noisy_angle)
    return min(error, 2 * math.pi - error)

def calculate_angle(p1, p2, p3):
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    det = v1[0] * v2[1] - v1[1] * v2[0]
    angle = math.atan2(det, dot)
    return angle if angle >= 0 else angle + 2 * math.pi

def distance(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])

# Konfigürasyon
DISTANCE_THRESHOLD = 0.8
ANGLE_THRESHOLD = 0.05
step_counter = 0
alert_counter = 0
cad_errors, dbc_errors = [], []
bda_errors, acb_errors = [], []

distance_list = []
angle_error_list = []

# Forklift simülasyonu
for i in range(0, len(segments), 2):
    plt.cla()
    step_counter += 1
    seg1 = segments[i]
    A, B = seg1

    alert_condition = False

    if i + 1 < len(segments):
        seg2 = segments[i + 1]
        C, D = seg2

        angle_CAD = calculate_angle(C, A, D)
        angle_DBC = calculate_angle(D, B, C)
        angle_BDA = calculate_angle(B, D, A)
        angle_ACB = calculate_angle(A, C, B)

        C_a, dist_CA = simulate_noisy_measurement(A, C)
        D_a, dist_DA = simulate_noisy_measurement(A, D)
        C_b, dist_CB = simulate_noisy_measurement(B, C)
        D_b, dist_DB = simulate_noisy_measurement(B, D)
        A_c, dist_AC = simulate_noisy_measurement(C, A)
        B_d, dist_BD = simulate_noisy_measurement(D, B)

        noisy_CAD = calculate_angle(C_a, A, D_a)
        noisy_DBC = calculate_angle(D_b, B, C_b)
        noisy_BDA = calculate_angle(B, D_b, A)
        noisy_ACB = calculate_angle(A_c, C, B_d)

        err_CAD = angular_error(angle_CAD, noisy_CAD)
        err_DBC = angular_error(angle_DBC, noisy_DBC)
        err_BDA = angular_error(angle_BDA, noisy_BDA)
        err_ACB = angular_error(angle_ACB, noisy_ACB)

        cad_errors.append(err_CAD)
        dbc_errors.append(err_DBC)
        bda_errors.append(err_BDA)
        acb_errors.append(err_ACB)

        distance_list += [dist_CA, dist_DA, dist_CB, dist_DB, dist_AC, dist_BD]
        angle_error_list += [err_CAD, err_CAD, err_DBC, err_DBC, err_BDA, err_ACB]

        ta = math.tan(angle_CAD)
        tb = math.tan(angle_DBC)
        tc = math.tan(angle_ACB)
        td = math.tan(angle_BDA)

        m = ta * tc * td
        n = tb * tc * td

        if abs(m) > ANGLE_THRESHOLD or abs(n) > ANGLE_THRESHOLD:
            alert_condition = True

        for p1 in [A, B]:
            for p2 in [C, D]:
                if distance(p1, p2) < DISTANCE_THRESHOLD:
                    alert_condition = True
        if alert_condition:
            alert_counter += 1

        info = (
            f"CAD hata: {math.degrees(err_CAD):.2f}°\n"
            f"DBC hata: {math.degrees(err_DBC):.2f}°\n"
            f"BDA hata: {math.degrees(err_BDA):.2f}°\n"
            f"ACB hata: {math.degrees(err_ACB):.2f}°\n"
            f"Step: {step_counter}, Alerts: {alert_counter}"
        )
        plt.text(-12, 12, info, fontsize=9, bbox=dict(facecolor='white', alpha=0.7))

    draw_background(alert=alert_condition)
    x1, y1 = zip(*seg1)
    plt.plot(x1, y1, marker='o', color='blue', label='Forklift 1 (A-B)')
    plt.text(A[0], A[1], 'A', fontsize=12, color='red')
    plt.text(B[0], B[1], 'B', fontsize=12, color='red')

    if i + 1 < len(segments):
        x2, y2 = zip(*seg2)
        plt.plot(x2, y2, marker='o', color='green', label='Forklift 2 (C-D)')
        plt.text(C[0], C[1], 'C', fontsize=12, color='red')
        plt.text(D[0], D[1], 'D', fontsize=12, color='red')

    plt.title(f"Case {i // 2 + 1}")
    plt.legend()
    plt.pause(0.001)

plt.show()

def deg_avg(errors): return math.degrees(np.mean(errors)) if errors else 0

print(f"Toplam adim: {step_counter}")
print(f"Toplam alarm: {alert_counter}")
print(f"Ortalama CAD acisal sapma: {deg_avg(cad_errors):.2f}°")
print(f"Ortalama DBC acisal sapma: {deg_avg(dbc_errors):.2f}°")
print(f"Ortalama BDA acisal sapma: {deg_avg(bda_errors):.2f}°")
print(f"Ortalama ACB acisal sapma: {deg_avg(acb_errors):.2f}°")

# Açısal sapma vs mesafe grafiği
plt.figure(figsize=(10, 6))
plt.scatter(distance_list, [math.degrees(err) for err in angle_error_list], alpha=0.6, label='Ölçüm')
plt.xlabel("Gerçek Mesafe (m)")
plt.ylabel("Açısal Hata (derece)")
plt.title("acisal hata grafigi")
plt.grid(True)
plt.legend()
plt.show()
