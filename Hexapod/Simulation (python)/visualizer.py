import pygame
import config
import math

class Visualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Hexapod Radial Simulator - IK Verification")
        self.clock = pygame.time.Clock()

    def world_to_screen(self, x, y):
        """Konversi koordinat mm ke pixel layar (0,0 di tengah)"""
        screen_x = int(config.SCREEN_WIDTH / 2 + x * config.SCALE)
        screen_y = int(config.SCREEN_HEIGHT / 2 - y * config.SCALE)
        return screen_x, screen_y

    def draw_robot(self, hexapod):
        self.screen.fill(config.COLOR_BG)
        
        # 1. Gambar Body (Dodecagon sederhana)
        points = []
        for leg in hexapod.legs:
            points.append(self.world_to_screen(leg.mount_x, leg.mount_y))
        if len(points) > 2:
            pygame.draw.polygon(self.screen, config.COLOR_BODY, points, 2)

        # 2. Gambar Setiap Kaki
        for leg in hexapod.legs:
            # Titik pangkal (Mount)
            p1 = self.world_to_screen(leg.mount_x, leg.mount_y)
            
            # Hitung posisi sendi berdasarkan sudut (Forward Kinematics sederhana untuk visual)
            # Ini hanya untuk melihat apakah IK-nya logis
            angle_total = leg.mount_angle + math.radians(leg.angles['coxa'])
            
            # Titik akhir Coxa
            cx = leg.mount_x + config.L_COXA * math.cos(angle_total)
            cy = leg.mount_y + config.L_COXA * math.sin(angle_total)
            p2 = self.world_to_screen(cx, cy)
            
            # Titik ujung kaki (Foot)
            p3 = self.world_to_screen(leg.foot_pos[0], leg.foot_pos[1])
            
            # Gambar garis paha dan betis
            pygame.draw.line(self.screen, config.COLOR_LEG, p1, p2, 4) # Coxa
            pygame.draw.line(self.screen, config.COLOR_LEG, p2, p3, 2) # Femur + Tibia (Top View)
            
            # Gambar joint
            pygame.draw.circle(self.screen, (255, 0, 0), p1, 4)
            pygame.draw.circle(self.screen, (0, 255, 0), p2, 3)
            pygame.draw.circle(self.screen, config.COLOR_TARGET, p3, 5)

        pygame.display.flip()

    def draw_side_view(self, hexapod):
        panel_x_start = config.SCREEN_WIDTH * 0.6
        spacing_y = config.SCREEN_HEIGHT / 7 
        

        for i, leg in enumerate(hexapod.legs):
            origin_x = panel_x_start + 100
            origin_y = (i + 1) * spacing_y
            
            # --- TITIK 1: Coxa Joint (Origin) ---
            p1 = (origin_x, origin_y)

            # --- TITIK 2: Femur Joint (Ujung Coxa) ---
            # Coxa diasumsikan horizontal di pandangan samping lokal
            p2_x = origin_x + config.L_COXA * config.SCALE
            p2_y = origin_y

            # --- TITIK 3: Tibia Joint (Ujung Femur) ---
            # AMBIL SUDUT DARI HASIL IK:
            # Kita harus mengurangi OFFSET agar sudut 0 derajat adalah horizontal
            angle_f_deg = leg.angles['femur'] - config.FEMUR_ANGLE_OFFSET

            # buat ngetes sudut femur
            # angle_f_raw = leg.angles['femur']
            # print(angle_f_raw)
            rad_f = math.radians(angle_f_deg)
            
            p3_x = p2_x + config.L_FEMUR * math.cos(rad_f) * config.SCALE
            p3_y = p2_y - config.L_FEMUR * math.sin(rad_f) * config.SCALE # Pygame Y terbalik

            # --- TITIK 4: Foot (Ujung Tibia) ---
            # Sudut Tibia dihitung relatif terhadap perpanjangan garis Femur
            angle_t_deg = angle_f_deg + (leg.angles['tibia'] - 180)
            rad_t = math.radians(angle_t_deg)
            
            p4_x = p3_x + config.L_TIBIA * math.cos(rad_t) * config.SCALE
            p4_y = p3_y - config.L_TIBIA * math.sin(rad_t) * config.SCALE

            # --- GAMBAR SEGMEN ---
            # Coxa (Merah ke Hijau)
            pygame.draw.line(self.screen, (200, 100, 100), p1, (p2_x, p2_y), 4)
            # Femur (Hijau ke Biru) - HARUSNYA TERLIHAT BERGERAK
            pygame.draw.line(self.screen, (100, 200, 100), (p2_x, p2_y), (p3_x, p3_y), 4)
            # Tibia (Biru ke Putih)
            pygame.draw.line(self.screen, (255, 255, 255), (p3_x, p3_y), (p4_x, p4_y), 4)
            