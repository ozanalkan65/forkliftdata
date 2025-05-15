import matplotlib.pyplot as plt
import numpy as np
import math

def draw_background(alert=False):
    plt.xlim(-25, 25)
    plt.ylim(-25, 25)
    plt.axhline(0, color="black")
    plt.axvline(0, color="black")
    ax = plt.gca()
    ax.set_facecolor('lightcoral' if alert else 'white')
    for val in [25, -25]:
        plt.axhline(val, linestyle="dashed", color="red")
        plt.axvline(val, linestyle="dashed", color="red")

def simulate_noisy_distance():
    return np.random.normal(loc=0, scale=0.5) # +/- 50 cm için standart sapma yaklaşık 0.5m

def calculate_noisy_point(start_point, end_point, noisy_distance):
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    real_distance = math.hypot(dx, dy)
    if real_distance == 0:
        return start_point
    ratio = noisy_distance / real_distance
    noisy_x = start_point[0] + dx * ratio
    noisy_y = start_point[1] + dy * ratio
    return (noisy_x, noisy_y)

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
NUM_SIMULATIONS = 1000
FORKLIFT_LENGTH = 3
MAX_DISTANCE = 25
ANGLE_THRESHOLD_MN = 0.05 # m ve n için eşik değeri (ayarlanabilir)
DISTANCE_THRESHOLD = 0.8 # Bu eşik hala kullanılabilir, isteğe bağlı

cad_errors, dbc_errors, bda_errors, acb_errors = [], [], [], []
distance_list = []
angle_error_list = []
alert_counter = 0

for _ in range(NUM_SIMULATIONS):
    plt.cla()
    alert_condition = False

    # Forklift 1 (AB)
    A = (0, 0)
    angle_AB = np.random.uniform(0, 2 * math.pi)
    B = (A[0] + FORKLIFT_LENGTH * math.cos(angle_AB), A[1] + FORKLIFT_LENGTH * math.sin(angle_AB))

    # Forklift 2 (CD)
    center_CD_distance = np.random.uniform(0, MAX_DISTANCE)
    angle_to_CD = np.random.uniform(0, 2 * math.pi)
    center_CD = (center_CD_distance * math.cos(angle_to_CD), center_CD_distance * math.sin(angle_to_CD))
    angle_CD = np.random.uniform(0, 2 * math.pi)
    C = (center_CD[0] + (FORKLIFT_LENGTH / 2) * math.cos(angle_CD), center_CD[1] + (FORKLIFT_LENGTH / 2) * math.sin(angle_CD))
    D = (center_CD[0] - (FORKLIFT_LENGTH / 2) * math.cos(angle_CD), center_CD[1] - (FORKLIFT_LENGTH / 2) * math.sin(angle_CD))

    # Gerçek açılar
    angle_CAD_true = calculate_angle(C, A, D)
    angle_DBC_true = calculate_angle(D, B, C)
    angle_BDA_true = calculate_angle(B, D, A)
    angle_ACB_true = calculate_angle(A, C, B)

    # Hatalı pozisyonlar
    noisy_C_from_A = calculate_noisy_point(A, C, distance(A, C) + simulate_noisy_distance())
    noisy_D_from_A = calculate_noisy_point(A, D, distance(A, D) + simulate_noisy_distance())
    noisy_C_from_B = calculate_noisy_point(B, C, distance(B, C) + simulate_noisy_distance())
    noisy_D_from_B = calculate_noisy_point(B, D, distance(B, D) + simulate_noisy_distance())

    # Hatalı açılar
    noisy_CAD = calculate_angle(noisy_C_from_A, A, noisy_D_from_A)
    noisy_DBC = calculate_angle(noisy_D_from_B, B, noisy_C_from_B)
    noisy_BDA = calculate_angle(B, noisy_D_from_B, A)
    noisy_ACB = calculate_angle(A, noisy_C_from_A, B)

    # Açısal hatalar
    err_CAD = angular_error(angle_CAD_true, noisy_CAD)
    err_DBC = angular_error(angle_DBC_true, noisy_DBC)
    err_BDA = angular_error(angle_BDA_true, noisy_BDA)
    err_ACB = angular_error(angle_ACB_true, noisy_ACB)

    cad_errors.append(err_CAD)
    dbc_errors.append(err_DBC)
    bda_errors.append(err_BDA)
    acb_errors.append(err_ACB)

    distance_list.append(center_CD_distance)
    angle_error_list.append(math.degrees(angular_error(0, noisy_ACB - angle_ACB_true))) # Genel doğrultu hatası

    # m ve n değerlerinin hesabı ve eşik kontrolü
    ta = math.tan(angle_CAD_true)
    tb = math.tan(angle_DBC_true)
    tc = math.tan(angle_ACB_true)
    td = math.tan(angle_BDA_true)

    # NaN değerlerini kontrol etme (tanjant tanımsız olabilir)
    m = ta * tc * td if all(not np.isnan(x) for x in [ta, tc, td]) else float('inf')
    n = tb * tc * td if all(not np.isnan(x) for x in [tb, tc, td]) else float('inf')

    if abs(m) > ANGLE_THRESHOLD_MN or abs(n) > ANGLE_THRESHOLD_MN:
        alert_condition = True
    # İsteğe bağlı olarak mesafe eşiğini de kullanabilirsiniz
    # for p1 in [A, B]:
    #     for p2 in [C, D]:
    #         if distance(p1, p2) < DISTANCE_THRESHOLD:
    #             alert_condition = True

    if alert_condition:
        alert_counter += 1

    if _ < 50:
        draw_background(alert=alert_condition)
        plt.plot([A[0], B[0]], [A[1], B[1]], marker='o', color='blue', label='Forklift 1 (AB)')
        plt.plot([C[0], D[0]], [C[1], D[1]], marker='o', color='green', label='Forklift 2 (CD)')
        plt.plot([A[0], noisy_C_from_A[0]], [A[1], noisy_C_from_A[1]], '--r')
        plt.plot([A[0], noisy_D_from_A[0]], [A[1], noisy_D_from_A[1]], '--r')
        plt.plot([B[0], noisy_C_from_B[0]], [B[1], noisy_C_from_B[1]], '--r')
        plt.plot([B[0], noisy_D_from_B[0]], [B[1], noisy_D_from_B[1]], '--r')
        plt.title(f"Simülasyon Adımı: {_ + 1}, Alarm: {alert_condition}")
        plt.legend()
        plt.pause(0.2)

plt.show()

def deg_avg(errors): return np.mean(errors) if errors else 0
def deg_std(errors): return np.std(errors) if errors else 0
def deg_max(errors): return np.max(errors) if errors else 0

plt.figure(figsize=(10, 6))
plt.scatter(distance_list, angle_error_list, alpha=0.6, label='Ölçüm')
plt.xlabel("Forkliftler Arası Mesafe (Yaklaşık, m)")
plt.ylabel("Açısal Hata (AB'den CD'ye, Derece)")
plt.title("Mesafe ile Açısal Sapma Arasındaki İlişki (m ve n Eşiği Eklenmiş)")
plt.grid(True)
plt.legend()

# Bilgi kutusu için metin oluşturma
info_text = (
    f"Toplam Simülasyon Adımı: {NUM_SIMULATIONS}\n"
    f"Toplam Alarm Sayısı: {alert_counter}\n"
    f"Ortalama Açısal Hata: {deg_avg(angle_error_list):.2f}°\n"
    f"Standart Sapma: {deg_std(angle_error_list):.2f}°\n"
    f"Maksimum Hata: {deg_max(angle_error_list):.2f}°"
)

# Grafiğe bilgi kutusunu ekleme
plt.text(0.95, 0.95, info_text, transform=plt.gca().transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.8))

plt.show()