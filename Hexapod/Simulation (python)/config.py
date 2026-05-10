import math

# ======================================================
# CONFIGURATION: HEXAPOD PHYSICAL PARAMETERS (Units in mm)
# ======================================================

# 1. Panjang Segmen Kaki (Berdasarkan Hasil Akar Kuadrat Vektor)
# Jarak efektif antara pusat rotasi ke pusat rotasi berikutnya  
L_COXA  = math.sqrt((-19.39370)**2 + 58.72800**2)  # +- 61.85 mm
L_FEMUR = math.sqrt(46.76537**2 + 27.00000**2)     # +- 54.02 mm
L_TIBIA = 67.68181                                # Pucuk kaki ke pusat Tibia

# 2. Offset Geometri (Kompensasi Bracket Melengkung)
# Karena poros motor tidak lurus horizontal, kita butuh sudut kompensasi
# atan2(z, x)
FEMUR_ANGLE_OFFSET = math.degrees(math.atan2(27.0, 46.76537)) # +- 30.01 derajat
COXA_ANGLE_OFFSET  = math.degrees(math.atan2(58.728, -19.39370)) # +- 108.27 derajat

# 3. Dimensi Badan (Radial/Symmetrical Design)
# Berdasarkan jarak antar pusat coxa berseberangan = 180mm
MOUNT_RADIUS = 90.0  
LEG_ANGLES   = [0, 60, 120, 180, 240, 300] # Sudut pemasangan 6 kaki (derajat)

# 4. Software Safety Limits (Derajat)
# Berdasarkan perhitungan titik tabrak (68.05, 31.00) -> elevasi 24.5 deg
# Kita beri margin aman (safety factor) agar tidak benar-benar menyentuh body
FEMUR_MAX_UP   = 19.5   # Batas dongak ke atas agar bracket tidak nabrak body
FEMUR_MAX_DOWN = -70.0  # Batas tekuk ke bawah
TIBIA_MAX      = 150.0  # Batas maksimal betis menekuk
TIBIA_MIN      = 20.0   # Batas minimal betis menjulur
STAND_Z = -100.0

# 5. Dimensi Visualisasi (Untuk Pygame)
# Skala mm ke pixel agar pas di layar laptop
SCALE = 2.0  
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 800

# 6. Parameter Gait (Langkah)
GAIT_STEP_LENGTH = 40.0   # Jarak langkah (mm)
GAIT_STEP_HEIGHT = 30.0   # Tinggi angkatan kaki (mm)
GAIT_SPEED = 0.05         # Kecepatan (0.01 - 0.1)

# Warna Visualisasi
COLOR_BG     = (30, 30, 30)
COLOR_BODY   = (100, 100, 255)
COLOR_LEG    = (200, 200, 200)
COLOR_TARGET = (255, 165, 0) # Oranye untuk target visi
COLOR_PATH = (80, 80, 100)