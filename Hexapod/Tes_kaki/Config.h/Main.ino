#include <Arduino.h>
#include "RobotModel.h"

// Inisialisasi objek robot
RobotModel robot;

void setup() {
  // Teensy 4.1 Serial sangat cepat, gunakan baudrate tinggi
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Tunggu serial siap
  
  Serial.println("========================================");
  Serial.println("   HEXAPOD TEENSY 4.1 CONTROL UTILITY   ");
  Serial.println("========================================");
  
  // Inisialisasi PCA9685 dan hardware lainnya
  robot.begin();
  
  Serial.println("Sistem Siap.");
  Serial.println("Perintah Manual: L,X,Y,Z  (Contoh: 0,150,0,-100)");
  Serial.println("Perintah Auto: 'sweep' untuk tes gerakan loop.");
  Serial.println("----------------------------------------");
}

/**
 * Memproses input dari Serial Monitor
 * Format: ID_Kaki, X, Y, Z
 */
void handleManualInput(String input) {
  int firstComma = input.indexOf(',');
  int secondComma = input.indexOf(',', firstComma + 1);
  int thirdComma = input.indexOf(',', secondComma + 1);
  
  if (firstComma == -1 || secondComma == -1 || thirdComma == -1) {
    Serial.println("Error: Format salah. Gunakan L,X,Y,Z");
    return;
  }
  
  int legID = input.substring(0, firstComma).toInt();
  float x = input.substring(firstComma + 1, secondComma).toFloat();
  float y = input.substring(secondComma + 1, thirdComma).toFloat();
  float z = input.substring(thirdComma + 1).toFloat();
  
  if (legID >= 0 && legID < 6) {
    Serial.printf("Kaki %d -> Target X:%.1f Y:%.1f Z:%.1f\n", legID, x, y, z);
    robot.moveLeg(legID, x, y, z);
  } else {
    Serial.println("Error: ID Kaki tidak valid (0-5)");
  }
}

/**
 * Tes gerakan otomatis untuk memastikan kelancaran mekanik
 */
void runAutoSweep() {
  Serial.println("Memulai Auto Sweep di Kaki 0...");
  float start_x = L_COXA + L_FEMUR;
  
  // Gerakan naik turun (Z-Axis)
  for (int repeat = 0; repeat < 2; repeat++) {
    for (float z = -70; z >= -130; z -= 2) {
      robot.moveLeg(0, start_x + 30, 0, z);
      delay(20);
    }
    for (float z = -130; z <= -70; z += 2) {
      robot.moveLeg(0, start_x + 30, 0, z);
      delay(20);
    }
  }
  Serial.println("Sweep Selesai. Kembali ke mode manual.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.equalsIgnoreCase("sweep")) {
      runAutoSweep();
    } else {
      handleManualInput(command);
    }
  }
}
