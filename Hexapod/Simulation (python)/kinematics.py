import math
import config

def leg_inverse_kinematics(target_x, target_y, target_z):
    """
    Menghitung sudut Coxa, Femur, dan Tibia.
    Input: target_x, target_y, target_z (relatif terhadap pusat rotasi Coxa)
    Output: Dictionary sudut derajat untuk 3 motor stepper
    """

    # 1. Coxa Angle
    theta_c = math.degrees(math.atan2(target_y, target_x))
    
    # 2. Horizontal Reach
    r = math.sqrt(target_x**2 + target_y**2)
    r_relative = r - config.L_COXA
    
    # 3. Diagonal Distance (ld)
    ld = math.sqrt(r_relative**2 + target_z**2)
    
    # --- PENTING: Jika ld terlalu pendek/panjang, return None ---
    if ld > (config.L_FEMUR + config.L_TIBIA) or ld < abs(config.L_FEMUR - config.L_TIBIA):
        return None

    # 4. Law of Cosines untuk Tibia
    cos_t = (config.L_FEMUR**2 + config.L_TIBIA**2 - ld**2) / (2 * config.L_FEMUR * config.L_TIBIA)
    cos_t = max(-1, min(1, cos_t))
    theta_t = 180 - math.degrees(math.acos(cos_t))

    # 5. Law of Cosines untuk Femur
    alpha_1 = math.atan2(target_z, r_relative) # Sudut ke target
    cos_f = (config.L_FEMUR**2 + ld**2 - config.L_TIBIA**2) / (2 * config.L_FEMUR * ld)
    cos_f = max(-1, min(1, cos_f))
    alpha_2 = math.acos(cos_f) # Sudut internal segitiga
    
    # Sudut Geometri (dalam derajat)
    theta_f_geom = math.degrees(alpha_1 + alpha_2)
    
    # 6. PENERAPAN OFFSET & LIMIT
    # Tambahkan offset dari config (30.01 derajat)
    final_femur = theta_f_geom + config.FEMUR_ANGLE_OFFSET
    
    # LIMIT CHECK (Gunakan nilai ekstrem 90/-90 untuk tes)
    final_femur = max(config.FEMUR_MAX_DOWN, min(config.FEMUR_MAX_UP, final_femur))
    
    return {
        "coxa": round(theta_c, 2),
        "femur": round(final_femur, 2),
        "tibia": round(theta_t, 2)
    }