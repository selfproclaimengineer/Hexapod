#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ======================================================
// CONFIGURATION: HEXAPOD PHYSICAL PARAMETERS (Units in mm)
// ======================================================

// 1. Panjang Segmen Kaki
// Catatan: Di C++ untuk mikrokontroler, lebih efisien menggunakan 
// hasil akhir (pre-calculated) daripada menyuruh chip menghitung sqrt/atan2 saat booting.
// Data diambil dari perhitungan config.py sebelumnya.
const float L_COXA  = 61.846;    // Hasil dari sqrt((-19.39370)^2 + 58.72800^2)
const float L_FEMUR = 54.017;    // Hasil dari sqrt(46.76537^2 + 27.00000^2)
const float L_TIBIA = 67.68181;

// 2. Offset Geometri (Kompensasi Bracket Melengkung)
const float FEMUR_ANGLE_OFFSET = 30.01;  // +- 30.01 derajat
const float COXA_ANGLE_OFFSET  = 108.27; // +- 108.27 derajat

// 3. Dimensi Badan (Radial/Symmetrical Design)
const float MOUNT_RADIUS = 90.0;  
const float LEG_ANGLES[6] = {0.0, 60.0, 120.0, 180.0, 240.0, 300.0}; // Array derajat kaki

// 4. Software Safety Limits (Derajat)
const float FEMUR_MAX_UP   = 19.5;   // Batas dongak ke atas
const float FEMUR_MAX_DOWN = -70.0;  // Batas tekuk ke bawah
const float TIBIA_MAX      = 150.0;  // Batas maksimal betis menekuk
const float TIBIA_MIN      = 20.0;   // Batas minimal betis menjulur
const float STAND_Z        = -100.0; // Tinggi default saat berdiri

#endif
