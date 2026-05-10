#include "Kinematics.h"
#include <math.h>

bool calculateIK(float target_x, float target_y, float target_z, LegAngles &result) {
    // 1. Hitung Sudut Coxa (Sumbu Z)
    // Menggunakan atan2 untuk mendapatkan sudut horizontal
    result.coxa = degrees(atan2(target_y, target_x));

    // 2. Hitung Jangkauan Horizontal (r)
    float r = sqrt(target_x * target_x + target_y * target_y);
    // Jarak relatif setelah dikurangi panjang Coxa
    float r_relative = r - L_COXA;

    // 3. Jarak Diagonal (ld) dari poros Femur ke ujung kaki
    float ld = sqrt(r_relative * r_relative + target_z * target_z);

    // --- CHECK REACHABILITY ---
    // Jika target terlalu jauh atau terlalu dekat, batalkan perhitungan
    if (ld > (L_FEMUR + L_TIBIA) || ld < abs(L_FEMUR - L_TIBIA)) {
        return false; 
    }

    // 4. Perhitungan Sudut Tibia (Hukum Cosinus)
    // cos_t = (a^2 + b^2 - c^2) / (2ab)
    float cos_t = (L_FEMUR * L_FEMUR + L_TIBIA * L_TIBIA - ld * ld) / (2 * L_FEMUR * L_TIBIA);
    cos_t = constrain(cos_t, -1.0, 1.0); // Safety clipping
    // Sudut interior dibalik agar sesuai dengan arah tekukan robot
    result.tibia = 180.0 - degrees(acos(cos_t));

    // 5. Perhitungan Sudut Femur (Hukum Cosinus + atan2)
    // alpha_1: Sudut elevasi dari poros ke target
    float alpha_1 = atan2(target_z, r_relative);
    // alpha_2: Sudut internal antara Femur dan garis ld
    float cos_f = (L_FEMUR * L_FEMUR + ld * ld - L_TIBIA * L_TIBIA) / (2 * L_FEMUR * ld);
    cos_f = constrain(cos_f, -1.0, 1.0);
    float alpha_2 = acos(cos_f);

    // Hasil akhir Femur dalam derajat
    result.femur = degrees(alpha_1 + alpha_2);

    return true;
}
