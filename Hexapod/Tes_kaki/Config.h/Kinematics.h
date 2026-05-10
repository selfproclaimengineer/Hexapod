#ifndef KINEMATICS_H
#define KINEMATICS_H

#include "Config.h"

// Struktur untuk menyimpan hasil sudut 3 motor paha
struct LegAngles {
    float coxa;
    float femur;
    float tibia;
};

/**
 * Menghitung Inverse Kinematics untuk satu kaki.
 * @param x, y, z Koordinat target relatif terhadap pusat rotasi Coxa.
 * @param result Referensi ke struct LegAngles untuk menyimpan hasil.
 * @return true jika target dapat dicapai (reachable), false jika tidak.
 */
bool calculateIK(float target_x, float target_y, float target_z, LegAngles &result);

#endif
