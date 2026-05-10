import pygame
import config
from robot_model import Hexapod
from visualizer import Visualizer

def main():
    robot = Hexapod()
    view = Visualizer()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input Mouse untuk translasi X, Y, dan Z
        mx, my = pygame.mouse.get_pos()
        
        # Area kiri (Top View) mengontrol X, Y badan
        if mx < config.SCREEN_WIDTH * 0.6:
            tx = (mx - config.SCREEN_WIDTH * 0.3) / config.SCALE
            ty = -(my - config.SCREEN_HEIGHT / 2) / config.SCALE
            tz = 0
            roll, pitch = 0, 0
        else:
            # Area kanan mengontrol Z (tinggi badan) lewat posisi Y mouse
            tx, ty = 0, 0
            tz = -(my / config.SCREEN_HEIGHT) * 150 - 20
            roll = (mx - config.SCREEN_WIDTH * 0.8) / 10.0
            pitch = (my - config.SCREEN_HEIGHT / 2) / 10.0
        
        robot.update_body_rotation(roll, pitch, tx, ty, tz)

        # Update semua kaki (Body Morphing)
        # Sesuai permintaanmu, IMU/Rotasi dihilangkan dulu
        for i in range(6):
            wx = robot.footprints[i][0]
            wy = robot.footprints[i][1]
            wz = robot.footprints[i][2] # Biasanya 0 (lantai)
            
            # Hitung posisi relatif ujung kaki terhadap badan yang bergeser
            # Jika badan naik ke +tx, +ty, +tz, maka kaki relatif ke -tx, -ty, -tz
            robot.legs[i].compute_ik(wx - tx, wy - ty, wz - tz)

        # Render
        view.screen.fill(config.COLOR_BG)
        
        # Gambar pembatas panel
        pygame.draw.line(view.screen, (100, 100, 100), (config.SCREEN_WIDTH * 0.6, 0), (config.SCREEN_WIDTH * 0.6, config.SCREEN_HEIGHT), 2)
        
        view.draw_robot(robot)        # Panel Kiri
        view.draw_side_view(robot)   # Panel Kanan (Gallery 6 kaki)

        pygame.display.flip()
        view.clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()