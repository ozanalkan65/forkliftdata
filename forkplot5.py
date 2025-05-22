import matplotlib.pyplot as plt
import numpy as np
import math

def draw_background(alert=False):
    plt.xlim(-14, 14)
    plt.ylim(-14, 14)
    plt.axhline(0, color="black")
    plt.axvline(0, color="black")
    ax = plt.gca()
    ax.set_facecolor('lightcoral' if alert else 'white')
    for val in [28, -28]:
        plt.axhline(val, linestyle="dashed", color="red")
        plt.axvline(val, linestyle="dashed", color="red")

def simulate_noisy_distance():
    return np.random.normal(loc=0, scale=0.5)

def calculate_noisy_point(start, end, noisy_dist):
    dx, dy = end[0] - start[0], end[1] - start[1]
    real_dist = math.hypot(dx, dy)
    if real_dist == 0: return start
    ratio = noisy_dist / real_dist
    return (start[0] + dx * ratio, start[1] + dy * ratio)

def angular_error(true, measured):
    diff = abs(true - measured)
    return min(diff, 2 * math.pi - diff)

def calculate_angle(p1, p2, p3):
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    det = v1[0]*v2[1] - v1[1]*v2[0]
    angle = math.atan2(det, dot)
    return angle if angle >= 0 else angle + 2 * math.pi

# Sabit forklift AB
FORKLIFT_LENGTH = 3
A = (0, 0)
angle_AB = 0  # sabit yön
B = (A[0] + FORKLIFT_LENGTH * math.cos(angle_AB),
     A[1] + FORKLIFT_LENGTH * math.sin(angle_AB))

# Parametreler
max_distance = 28.0
step_distance = 0.5
step_rotation = 10  # derece
total_steps = 0
distance_list = []
angle_error_list = []
center_AB = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)

for dist in np.arange(3.5, max_distance + 0.01, step_distance):
    for center_rotation_deg in range(0, 360, step_rotation):
        center_rotation_rad = math.radians(center_rotation_deg)
        center_x = center_AB[0] + dist * math.cos(center_rotation_rad)
        center_y = center_AB[1] + dist * math.sin(center_rotation_rad)
        center_CD = (center_x, center_y)

        for cd_angle_deg in range(0, 360, step_rotation):
            total_steps += 1
            angle_CD = math.radians(cd_angle_deg)

            # Gerçek C-D noktaları
            C = (center_CD[0] + (FORKLIFT_LENGTH/2) * math.cos(angle_CD),
                 center_CD[1] + (FORKLIFT_LENGTH/2) * math.sin(angle_CD))
            D = (center_CD[0] - (FORKLIFT_LENGTH/2) * math.cos(angle_CD),
                 center_CD[1] - (FORKLIFT_LENGTH/2) * math.sin(angle_CD))

            # Gerçek ve gürültülü ACB açısı
            angle_ACB_true = calculate_angle(A, C, B)
            noisy_C = calculate_noisy_point(A, C, math.hypot(C[0]-A[0], C[1]-A[1]) + simulate_noisy_distance())
            noisy_D = calculate_noisy_point(A, D, math.hypot(D[0]-A[0], D[1]-A[1]) + simulate_noisy_distance())

            noisy_angle = calculate_angle(A, noisy_C, B)

            error_deg = math.degrees(angular_error(angle_ACB_true, noisy_angle))
            distance_list.append(dist)
            angle_error_list.append(error_deg)

            #alert_condition = error_deg > 15

            if total_steps <= 10000:
                plt.cla()

                center_AB = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
                center_CD = ((C[0] + D[0]) / 2, (C[1] + D[1]) / 2)
                
                plt.cla()
                draw_background(alert=False)
                
                # Forklift AB
                plt.plot([A[0], B[0]], [A[1], B[1]], marker='o', color='blue', label='Forklift 1 (AB)')
                
                # Forklift CD
                plt.plot([C[0], D[0]], [C[1], D[1]], marker='o', color='green', label='Forklift 2 (CD)')
                
                plt.plot([center_AB[0], center_CD[0]], [center_AB[1], center_CD[1]], 'k--', label='Merkezler arası')
                plt.plot([A[0], C[0]], [A[1], C[1]], 'r--')
                plt.plot([A[0], D[0]], [A[1], D[1]], 'r--')
                plt.plot([B[0], C[0]], [B[1], C[1]], 'r--')
                plt.plot([B[0], D[0]], [B[1], D[1]], 'r--')
                plt.title(f"Simülasyon Adımı: {total_steps}")
                plt.legend(loc='upper right')
                plt.pause(0.001)

plt.show()

# Sonuç grafiği
plt.figure(figsize=(10,6))
plt.scatter(distance_list, angle_error_list, s=5, alpha=0.6)
plt.xlabel("Forkliftler Arası Mesafe (m)")
plt.ylabel("Açısal Hata (°)")
plt.title("Sistematik Tarama ile Açısal Hata Analizi")
plt.grid(True)

plt.text(0.95, 0.95,
         f"Toplam Simülasyon: {total_steps}\n"
         f"Ortalama Hata: {np.mean(angle_error_list):.2f}°\n"
         f"Standart Sapma: {np.std(angle_error_list):.2f}°\n"
         f"Maksimum Hata: {np.max(angle_error_list):.2f}°",
         transform=plt.gca().transAxes,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(facecolor='white', alpha=0.8))

plt.show()
