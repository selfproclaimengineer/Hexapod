import pygame
import math
import sys

# ==========================================
# 1. KONFIGURASI PARAMETER FISIK (Real World)
# Satuan: Milimeter (mm)
# ==========================================
BODY_WIDTH = 120   # Lebar badan
BODY_LENGTH = 200  # Panjang badan
L_COXA = 40        # Panjang Coxa
L_FEMUR = 60       # Panjang Femur (Proyeksi 2D)
L_TIBIA = 80       # Panjang Tibia (Proyeksi 2D)

# ==========================================
# 2. KONFIGURASI PYGAME (Screen Space)
# ==========================================
WIDTH, HEIGHT = 800, 600
FPS = 60
SCALE = 1.5  # Skala: 1 mm = 1.5 pixel di layar

# Warna (RGB)
BG_COLOR = (30, 30, 40)
BODY_COLOR = (100, 150, 200)
LEG_COLOR = (200, 200, 200)
JOINT_COLOR = (255, 100, 100)
TARGET_COLOR = (255, 165, 0) # Warna Oranye untuk target

class Hexapod:
    def __init__(self, x, y):
        # Posisi pusat robot di layar
        self.cx = x
        self.cy = y
        self.heading = 0 # Sudut hadap robot (derajat)

        # Definisi titik kumpul kaki relatif terhadap pusat badan (cx, cy)
        # Format: (offset_X, offset_Y)
        hw = BODY_WIDTH / 2
        hl = BODY_LENGTH / 2
        
        self.leg_mounts = [
            (hw, -hl),   # Kanan Depan (RF)
            (hw, 0),     # Kanan Tengah (RM)
            (hw, hl),    # Kanan Belakang (RB)
            (-hw, -hl),  # Kiri Depan (LF)
            (-hw, 0),    # Kiri Tengah (LM)
            (-hw, hl)    # Kiri Belakang (LB)
        ]
        
        # Sudut default Coxa saat diam (Home Position)
        self.default_coxa_angles = [
            -45,  0,  45,  # Kanan (Depan, Tengah, Belakang)
            -135, 180, 135 # Kiri (Depan, Tengah, Belakang)
        ]

    def draw(self, surface):
        # Menggambar Badan Robot (Kotak)
        # Kita konversi dimensi mm ke pixel menggunakan SCALE
        rect_width = BODY_WIDTH * SCALE
        rect_height = BODY_LENGTH * SCALE
        rect_x = self.cx - (rect_width / 2)
        rect_y = self.cy - (rect_height / 2)
        
        pygame.draw.rect(surface, BODY_COLOR, (rect_x, rect_y, rect_width, rect_height), 2)
        pygame.draw.circle(surface, BODY_COLOR, (int(self.cx), int(self.cy)), 5) # Pusat badan

        # Menggambar Keenam Kaki
        for i in range(6):
            # 1. Cari koordinat pangkal kaki di layar
            mount_x = self.cx + (self.leg_mounts[i][0] * SCALE)
            mount_y = self.cy + (self.leg_mounts[i][1] * SCALE)
            
            # Gambar titik sendi Coxa
            pygame.draw.circle(surface, JOINT_COLOR, (int(mount_x), int(mount_y)), 6)

            # 2. Gambar garis Coxa (Pangkal ke Paha)
            angle_rad = math.radians(self.default_coxa_angles[i])
            coxa_end_x = mount_x + (math.cos(angle_rad) * L_COXA * SCALE)
            coxa_end_y = mount_y + (math.sin(angle_rad) * L_COXA * SCALE)
            
            pygame.draw.line(surface, LEG_COLOR, (mount_x, mount_y), (coxa_end_x, coxa_end_y), 4)
            pygame.draw.circle(surface, JOINT_COLOR, (int(coxa_end_x), int(coxa_end_y)), 4)

            # 3. Gambar garis Proyeksi Femur + Tibia (Disatukan sementara untuk 2D Top-Down)
            # Di simulasi nyata, ini akan dipengaruhi oleh sudut Z (Inverse Kinematics)
            total_leg_len = (L_FEMUR + L_TIBIA) * 0.7 # 0.7 adalah asumsi kaki menekuk ke bawah
            leg_end_x = coxa_end_x + (math.cos(angle_rad) * total_leg_len * SCALE)
            leg_end_y = coxa_end_y + (math.sin(angle_rad) * total_leg_len * SCALE)

            pygame.draw.line(surface, LEG_COLOR, (coxa_end_x, coxa_end_y), (leg_end_x, leg_end_y), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hexapod Rescue Simulator - Top View")
    clock = pygame.time.Clock()

    # Inisialisasi Robot di tengah layar
    robot = Hexapod(WIDTH // 2, HEIGHT // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Dapatkan posisi mouse untuk simulasi "Target Oranye"
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update Layar
        screen.fill(BG_COLOR)
        
        # Gambar Target (Simulasi Visi Kamera)
        pygame.draw.circle(screen, TARGET_COLOR, (mouse_x, mouse_y), 15)
        pygame.draw.line(screen, (80, 80, 80), (robot.cx, robot.cy), (mouse_x, mouse_y), 1)

        # Gambar Robot
        robot.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()