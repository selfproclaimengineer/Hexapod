#include "RobotModel.h"
#include <math.h>

RobotModel::RobotModel() : pca1(0x40), pca2(0x41) {}

void RobotModel::begin() {
    pca1.begin();
    pca1.setPWMFreq(50); // Frekuensi 50Hz untuk servo analog/digital standar
    pca2.begin();
    pca2.setPWMFreq(50);
}

// x, y, z di sini adalah target koordinat RELATIF terhadap pusat badan robot
void RobotModel::moveLeg(int legID, float x, float y, float z) {
    if (legID < 0 || legID >= 6) {
        Serial.print("ERROR: Invalid leg ID ");
        Serial.println(legID);
        return;
    }
    
    // 1. Ambil sudut pemasangan kaki dari Config.h
    float mount_angle_rad = radians(LEG_ANGLES[legID]);
    
    // 2. Hitung posisi pangkal paha (mount point)
    float mount_x = MOUNT_RADIUS * cos(mount_angle_rad);
    float mount_y = MOUNT_RADIUS * sin(mount_angle_rad);
    
    // 3. Translasi: Jarak target ke pangkal paha
    float dx = x - mount_x;
    float dy = y - mount_y;
    
    // 4. Rotasi: Ubah ke sumbu lokal kaki (Matrix Rotation)
    // PENTING: Offset geometri COXA diterapkan di sini untuk sinkronisasi matriks rotasi
    float leg_local_angle = mount_angle_rad + radians(COXA_ANGLE_OFFSET);
    
    float local_x = dx * cos(leg_local_angle) + dy * sin(leg_local_angle);
    float local_y = -dx * sin(leg_local_angle) + dy * cos(leg_local_angle);
    float local_z = z; // Z tidak berubah (Top-Down)

    LegAngles targetAngles;
    
    // Panggil IK dengan koordinat lokal
    if (calculateIK(local_x, local_y, local_z, targetAngles)) {
        writeToServo(legID, targetAngles);
    } else {
        Serial.print("Target di luar jangkauan untuk Kaki ");
        Serial.println(legID);
    }
}

void RobotModel::writeToServo(int legID, LegAngles angles) {
    if (legID < 0 || legID >= 6) {
        Serial.print("ERROR: Invalid leg ID in writeToServo: ");
        Serial.println(legID);
        return;
    }
    
    Adafruit_PWMServoDriver &targetPCA = (legID < 4) ? pca1 : pca2;
    int basePin = (legID < 4) ? (legID * 3) : ((legID - 4) * 3);

    // 1. Aplikasikan offset geometri Femur saja di sini
    //    COXA offset sudah diterapkan saat konversi koordinat di moveLeg()
    float final_coxa  = 90.0 + angles.coxa;                       // Tanpa offset
    float final_femur = 90.0 + angles.femur + FEMUR_ANGLE_OFFSET; // Dengan offset geometri
    float final_tibia = 90.0 + angles.tibia;                      // Tanpa offset

    // 2. SAFETY FILTER: Pastikan dalam range servo yang valid (0-180°)
    final_coxa  = constrain(final_coxa, 0, 180);
    final_femur = constrain(final_femur, 0, 180);
    final_tibia = constrain(final_tibia, 0, 180);

    // DEBUG: Uncomment untuk verifikasi kalkulasi
    // Serial.printf("Leg %d | IK: C=%.1f° F=%.1f° T=%.1f° | Final: C=%.1f° F=%.1f° T=%.1f°\n",
    //     legID, angles.coxa, angles.femur, angles.tibia, final_coxa, final_femur, final_tibia);

    // 3. Konversi ke PWM Pulse (Kalibrasi rentang 150-600 sesuai servomu)
    int pwm_c = map(final_coxa, 0, 180, 150, 600);
    int pwm_f = map(final_femur, 0, 180, 150, 600);
    int pwm_t = map(final_tibia, 0, 180, 150, 600);

    // Safety check PWM bounds
    if (pwm_c < 0 || pwm_c > 4095 || pwm_f < 0 || pwm_f > 4095 || pwm_t < 0 || pwm_t > 4095) {
        Serial.printf("ERROR: PWM out of bounds for leg %d (C:%d F:%d T:%d)\n", legID, pwm_c, pwm_f, pwm_t);
        return;
    }

    // 4. Kirim sinyal ke I2C PCA9685
    targetPCA.setPWM(basePin, 0, pwm_c);
    targetPCA.setPWM(basePin + 1, 0, pwm_f);
    targetPCA.setPWM(basePin + 2, 0, pwm_t);
}
