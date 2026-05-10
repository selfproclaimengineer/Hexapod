#ifndef ROBOTMODEL_H
#define ROBOTMODEL_H

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include "Kinematics.h"

class RobotModel {
private:
    // Dua modul PCA9685 karena kita butuh 18 pin (6 kaki x 3)
    Adafruit_PWMServoDriver pca1; // Alamat 0x40 (Kaki 1-4)
    Adafruit_PWMServoDriver pca2; // Alamat 0x41 (Kaki 5-6)

    // Menyimpan posisi kaki saat ini
    LegAngles currentAngles[6];

public:
    RobotModel();
    void begin();
    
    // Fungsi untuk menggerakkan satu kaki berdasarkan ID (0-5)
    void moveLeg(int legID, float x, float y, float z);
    
    // Fungsi pembantu untuk memetakan ID kaki ke Pin PCA yang benar
    void writeToServo(int legID, LegAngles angles);
};

#endif
