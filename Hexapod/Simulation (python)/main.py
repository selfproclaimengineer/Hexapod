import math
import pygame
import config
import time
from robot_model import Hexapod
from visualizer import Visualizer

def main():
    robot = Hexapod()
    view = Visualizer()
    
    # List untuk menyimpan jejak: [[x, y, timestamp], ...]
    path_dots = []
    
    running = True
    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Hitung Target & Arah
        mx, my = pygame.mouse.get_pos()
        # Koordinat world untuk logika
        target_x = (mx - config.SCREEN_WIDTH * 0.3) / config.SCALE
        target_y = -(my - config.SCREEN_HEIGHT / 2) / config.SCALE
        
        # Hitung sudut arah (Direction)
        dx = mx - (config.SCREEN_WIDTH * 0.3)
        dy = -(my - (config.SCREEN_HEIGHT / 2))
        direction = math.degrees(math.atan2(dy, dx))

        # 2. Tambahkan titik jejak baru (posisi badan robot saat ini)
        # Kita simpan posisi (0,0) relatif karena badan selalu di tengah layar
        path_dots.append([0, 0, current_time])
        
        # 3. Hapus jejak yang sudah lebih dari 5 detik
        path_dots = [dot for dot in path_dots if current_time - dot[2] < 5.0]

        # 4. Update Gerakan Robot
        robot.walk_tripod(direction_deg=direction)

        # 5. Render
        view.screen.fill(config.COLOR_BG)
        
        # Gambar Garis Pembatas Panel
        pygame.draw.line(view.screen, (100, 100, 100), (config.SCREEN_WIDTH * 0.6, 0), (config.SCREEN_WIDTH * 0.6, config.SCREEN_HEIGHT), 2)
        
        # --- DRAW VISUAL Tambahan (DI PANEL KIRI) ---
        center_screen_x = int(config.SCREEN_WIDTH * 0.3)
        center_screen_y = int(config.SCREEN_HEIGHT / 2)

        # A. Update dan Gambar Jejak (Dots)
        # Hitung kecepatan gerak titik (disesuaikan dengan GAIT_SPEED robot)
        move_speed = config.GAIT_SPEED * 50 # Faktor skala visual
        move_x = math.cos(math.radians(direction)) * move_speed
        move_y = -math.sin(math.radians(direction)) * move_speed # Y balik di pygame

        for dot in path_dots:
            # Gerakkan titik ke arah berlawanan dari jalan robot agar terlihat tertinggal
            dot[0] -= move_x
            dot[1] -= move_y
            
            # Konversi koordinat relatif ke posisi layar
            dot_screen_x = int(center_screen_x + dot[0])
            dot_screen_y = int(center_screen_y + dot[1])
            
            # Gambar titik kecil (hanya jika masih di area panel kiri)
            if dot_screen_x < config.SCREEN_WIDTH * 0.6:
                # Transparansi sederhana berdasarkan waktu (opsional)
                pygame.draw.circle(view.screen, (150, 150, 150), (dot_screen_x, dot_screen_y), 2)

        # B. Gambar Garis Arah ke Mouse
        center_pos = (center_screen_x, center_screen_y)
        pygame.draw.line(view.screen, config.COLOR_TARGET, center_pos, (mx, my), 1)
        pygame.draw.circle(view.screen, config.COLOR_TARGET, (mx, my), 4)

        # 6. Render Robot & Side View
        view.draw_robot(robot)        
        view.draw_side_view(robot)   

        pygame.display.flip()
        view.clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()