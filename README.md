# Hexapod Rescue Robot

Proyek ini adalah sistem kontrol komprehensif untuk robot Hexapod 3-DOF (Degrees of Freedom) per kaki. Pengembangan dibagi menjadi dua fase: **Fase Simulasi Visual (Python)** dan **Fase Implementasi Hardware (C++ / Teensy 4.1)**. 

Sistem ini menggunakan perhitungan *Inverse Kinematics* (IK) dengan kompensasi sudut mekanik (*hardware offset*) dan dilengkapi dengan *Software Safety Limits* untuk mencegah kerusakan fisik pada motor servo tanpa menggunakan sensor arus eksternal.

## ⚙️ Spesifikasi Hardware Utama
- **Microcontroller**: Teensy 4.1 (600MHz, FPU aktif untuk komputasi IK real-time).
- **Servo Driver**: 2x PCA9685 (Daisy-chained via I2C, Address `0x40` dan `0x41`).
- **Aktuator**: 18x Motor Servo (3 per kaki: Coxa, Femur, Tibia).
- **Sensor**: IMU Yahboom (Kompas/Gyro) - *(Digunakan untuk fase keseimbangan dan rotasi selanjutnya)*.

---

## 📂 Struktur File dan Fungsinya

### Fase 1: Simulasi (Python / Pygame)
Fase ini digunakan untuk memvisualisasikan pergerakan robot dan menguji algoritma *Gait Engine* sebelum diaplikasikan ke hardware nyata.

* `config.py`: Menyimpan seluruh parameter fisik robot (panjang kaki, limit sudut, offset mekanik) dan variabel UI untuk simulasi.
* `kinematics.py`: Berisi fungsi matematika murni (`leg_inverse_kinematics`) menggunakan Hukum Cosinus untuk mengubah target (X, Y, Z) menjadi sudut derajat.
* `robot_model.py`: Otak pergerakan robot. Berisi *Gait Engine* (Tripod Gait), pengaturan fase *Swing/Stance*, dan rotasi matriks koordinat.
* `visualizer.py`: Sistem render grafis menggunakan Pygame. Menampilkan status kaki dari atas (Top-Down) dan samping (Side-View).
* `main.py`: Main loop simulasi. Menangani input *mouse* sebagai target arah jalan, mengkalkulasi vektor, dan mengupdate jejak lintasan (breadcrumbs).

### Fase 2: Hardware Control (C++ / Arduino IDE)
Fase ini adalah program yang di-*upload* langsung ke memori mikrokontroler Teensy 4.1.

* `Config.h`: Menggantikan `config.py`. Menyimpan parameter fisik sebagai konstan (`const float`) untuk efisiensi RAM, termasuk batas aman rotasi.
* `Kinematics.h` & `Kinematics.cpp`: Adaptasi logika IK ke dalam C++. Menggunakan `struct LegAngles` dan fitur komputasi *float* presisi tinggi dari chip Teensy.
* `RobotModel.h` & `RobotModel.cpp`: Modul jembatan antara logika dan hardware. Bertugas mengubah matriks global ke lokal, menerapkan offset mekanik, membatasi sudut ekstrim, dan mengirim sinyal PWM ke modul PCA9685.
* `Main.ino`: Program eksekusi utama. Menyediakan antarmuka Serial Monitor untuk input manual (X,Y,Z) dan mode pengetesan otomatis (*Auto Sweep*).

---

## 🧠 Cara Kerja dan Variabel yang Terpengaruh

Sistem ini bekerja melalui beberapa lapisan konversi, dari perintah abstrak hingga menjadi sinyal listrik pada motor:

### 1. Transformasi Koordinat (Global ke Lokal)
Saat robot diperintahkan maju ke koordinat tertentu, setiap kaki (yang dipasang dengan sudut berbeda: 0°, 60°, 120°, dsb) harus menerjemahkan arah "maju" tersebut.
* **Variabel Terpengaruh**: `LEG_ANGLES[6]`, `MOUNT_RADIUS`.
* **Proses**: Fungsi di `RobotModel.cpp` menghitung jarak target ke pangkal paha, lalu memutarnya dengan **Matrix Rotation** (`dx * cos + dy * sin`) sehingga sumbu X selalu berarti "menjauh dari badan" bagi kaki tersebut.

### 2. Inverse Kinematics (IK)
Menerjemahkan koordinat spasial (X, Y, Z) menjadi sudut putaran sendi.
* **Variabel Terpengaruh**: `L_COXA`, `L_FEMUR`, `L_TIBIA`.
* **Proses**: Menggunakan trigonometri `atan2()` untuk sudut Coxa (bahu), dan Hukum Cosinus (`acos()`) untuk menghitung sudut segitiga yang dibentuk oleh Femur (paha) dan Tibia (betis).

### 3. Kompensasi Offset Fisik (Mechanical Alignment)
Bentuk fisik bracket robot tidak lurus sempurna, sehingga nilai 0° di perhitungan matematika bukanlah 0° di dunia nyata.
* **Variabel Terpengaruh**: `FEMUR_ANGLE_OFFSET`, `COXA_ANGLE_OFFSET`.
* **Proses**: Menambahkan/mengurangkan nilai derajat hasil IK dengan nilai kompensasi ini agar tulang robot sejajar dengan orientasi yang diharapkan.

### 4. Software Safety Limits (Virtual Bumper)
Karena sistem tidak menggunakan deteksi lonjakan arus (*Current Sensing*), proteksi benturan murni mengandalkan batasan di dalam kode.
* **Variabel Terpengaruh**: `FEMUR_MAX_UP`, `FEMUR_MAX_DOWN`, `TIBIA_MAX`, `TIBIA_MIN`.
* **Proses**: Sebelum dikirim ke servo, sudut disaring oleh fungsi `constrain()`. Jika target melewati batas ini, nilai akan dipotong agar bracket tidak menghantam rangka badan.

### 5. Translasi Sinyal (Degrees to PWM)
Motor servo dikendalikan dengan panjang gelombang PWM, bukan derajat langsung.
* **Variabel Terpengaruh**: Rentang bit PCA9685 (biasanya `150` hingga `600`).
* **Proses**: Menggunakan fungsi `map()` untuk memetakan rentang 0° - 180° ke dalam rentang pulsa minimum dan maksimum servo. Sinyal kemudian disalurkan ke `pca1` atau `pca2` berdasarkan `legID`.

---

## 🔧 Panduan Kalibrasi (Penting!)
Sebelum menjalankan `Main.ino` untuk pertama kali dengan kaki terpasang:
1. Jalankan kode untuk menetapkan semua servo ke posisi `90` derajat.
2. Pasang *horn* servo sedemikian rupa sehingga Femur sejajar (horizontal) dengan tanah.
3. Lakukan tes manual secara bertahap via Serial Monitor untuk memastikan batasan `FEMUR_MAX_UP` dan `FEMUR_MAX_DOWN` sudah sesuai dengan titik benturan fisik robotmu.
