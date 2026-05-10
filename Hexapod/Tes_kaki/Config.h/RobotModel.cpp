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
    // 1. Ambil sudut pemasangan kaki dari Config.h
    float mount_angle_rad = radians(LEG_ANGLES[legID]);
    
    // 2. Hitung posisi pangkal paha (mount point)
    float mount_x = MOUNT_RADIUS * cos(mount_angle_rad);
    float mount_y = MOUNT_RADIUS * sin(mount_angle_rad);
    
    // 3. Translasi: Jarak target ke pangkal paha
    float dx = x - mount_x;
    float dy = y - mount_y;
    
    // 4. Rotasi: Ubah ke sumbu lokal kaki (Matrix Rotation)
    // Supaya fungsi IK mengerti "maju" nya kaki sesuai arah hadapnya
    float local_x = dx * cos(mount_angle_rad) + dy * sin(mount_angle_rad);
    float local_y = -dx * sin(mount_angle_rad) + dy * cos(mount_angle_rad);
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
    Adafruit_PWMServoDriver &targetPCA = (legID < 4) ? pca1 : pca2;
    int basePin = (legID < 4) ? (legID * 3) : ((legID - 4) * 3);

    // 1. Tambahkan Offset Geometri dari Config.h (Asumsi Servo Tengah = 90 derajat)
    // Tibia mungkin perlu di +/- tergantung arah fisik pemasangan servo
    float final_coxa  = 90.0 + angles.coxa + COXA_ANGLE_OFFSET; 
    float final_femur = 90.0 + angles.femur + FEMUR_ANGLE_OFFSET;
    float final_tibia = 90.0 + angles.tibia; 

    // 2. SAFETY FILTER: Pastikan sudut tidak kurang dari 0 dan lebih dari 180
    final_coxa  = constrain(final_coxa, 0, 180);
    final_femur = constrain(final_femur, 0, 180);
    final_tibia = constrain(final_tibia, 0, 180);

    // 3. Konversi ke PWM Pulse (Kalibrasi rentang 150-600 sesuai servomu)
    int pwm_c = map(final_coxa, 0, 180, 150, 600);
    int pwm_f = map(final_femur, 0, 180, 150, 600);
    int pwm_t = map(final_tibia, 0, 180, 150, 600);

    // 4. Kirim sinyal ke I2C PCA9685
    targetPCA.setPWM(basePin, 0, pwm_c);
    targetPCA.setPWM(basePin + 1, 0, pwm_f);
    targetPCA.setPWM(basePin + 2, 0, pwm_t);
}
