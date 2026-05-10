import math
import config
from kinematics import leg_inverse_kinematics

class Leg:
    def __init__(self, leg_id, mount_angle):
        self.leg_id = leg_id
        # Konversi sudut pemasangan kaki ke radian (0, 60, 120, dst)
        self.mount_angle = math.radians(mount_angle)
        
        # Posisi pangkal kaki (Coxa) relatif terhadap pusat robot (0,0,0)
        self.mount_x = config.MOUNT_RADIUS * math.cos(self.mount_angle)
        self.mount_y = config.MOUNT_RADIUS * math.sin(self.mount_angle)
        
        # Sudut motor saat ini (default 0)
        self.angles = {"coxa": 0, "femur": 0, "tibia": 0}
        # Posisi ujung kaki saat ini (relatif terhadap pusat robot)
        self.foot_pos = [0, 0, 0]

    def compute_ik(self, target_world_x, target_world_y, target_world_z):
        """
        Mengubah target koordinat World (pusat robot) ke koordinat Local (kaki)
        lalu menghitung sudut motornya.
        """
        # 1. Geser koordinat agar (0,0) berada di pangkal paha (mount_x, mount_y)
        dx = target_world_x - self.mount_x
        dy = target_world_y - self.mount_y
        dz = target_world_z
        
        # 2. Rotasi koordinat Local: Mengubah arah World (X,Y) ke arah hadap kaki
        # Ini supaya rumus IK di kinematics.py yang 2D bisa bekerja untuk semua kaki
        lx = dx * math.cos(-self.mount_angle) - dy * math.sin(-self.mount_angle)
        ly = dx * math.sin(-self.mount_angle) + dy * math.cos(-self.mount_angle)
        
        # 3. Hitung IK
        result = leg_inverse_kinematics(lx, ly, dz)
        
        if result:
            self.angles = result
            self.foot_pos = [target_world_x, target_world_y, target_world_z]
            return True
        return False

class Hexapod:
    def __init__(self):
        # Membuat 6 objek kaki berdasarkan sudut di config
        self.legs = []
        for i, angle in enumerate(config.LEG_ANGLES):
            self.legs.append(Leg(i, angle))
        
        # Posisi "Home" kaki (posisi berdiri standar)
        # Kita taruh kaki 150mm keluar dari pusat robot, dan 100mm di bawah badan
        self.stand_radius = 160.0 
        self.stand_z = -100.0 # Robot berdiri setinggi 100mm
        self.body_offset_x = 0
        self.body_offset_y = 0
        self.body_offset_z = config.STAND_Z  # Default -100
        
        # Simpan posisi "jejak kaki" permanen di tanah
        self.footprints = []
        for leg in self.legs:
            # Posisi berdiri awal tiap kaki
            hx = (config.MOUNT_RADIUS + 80) * math.cos(leg.mount_angle)
            hy = (config.MOUNT_RADIUS + 80) * math.sin(leg.mount_angle)
            self.footprints.append([hx, hy, config.STAND_Z]) # 0 adalah permukaan tanah
        
        # Variabel baru untuk Gait
        self.step_phase = 0.0 # 0.0 sampai 1.0
        # Grup A: Kaki 0, 2, 4 | Grup B: Kaki 1, 3, 5
        self.group_a = [0, 2, 4]
        self.group_b = [1, 3, 5]

    def reset_to_home(self):
        """Menempatkan semua kaki di posisi berdiri standar"""
        for leg in self.legs:
            # Hitung posisi target berdiri untuk tiap kaki secara radial
            hx = self.stand_radius * math.cos(leg.mount_angle)
            hy = self.stand_radius * math.sin(leg.mount_angle)
            leg.compute_ik(hx, hy, self.stand_z)

    def update_all_legs(self, foot_targets):
        """
        foot_targets: List koordinat [[x1,y1,z1], [x2,y2,z2], ...] untuk 6 kaki
        """
        for i in range(6):
            # Mengambil target [x, y, z] untuk kaki ke-i
            tx, ty, tz = foot_targets[i]
            success = self.legs[i].compute_ik(tx, ty, tz)
            if not success:
                # Jika target di luar jangkauan, kaki tetap di posisi terakhirnya
                pass

    def update_body_rotation(self, roll_deg, pitch_deg, tx, ty, tz):
        roll = math.radians(roll_deg)
        pitch = math.radians(pitch_deg)

        for i in range(6):
            # 1. Koordinat pangkal paha (mount point) awal relatif terhadap pusat badan
            # Di sini z paha awal dianggap 0
            mx = self.legs[i].mount_x
            my = self.legs[i].mount_y
            mz = 0 

            # 2. Rotasi 3D pada Pangkal Paha (Body Rotation)
            # Rotasi Pitch (Sumbu Y)
            x_p = mx * math.cos(pitch) + mz * math.sin(pitch)
            z_p = -mx * math.sin(pitch) + mz * math.cos(pitch)
            
            # Rotasi Roll (Sumbu X)
            y_r = my * math.cos(roll) - z_p * math.sin(roll)
            z_r = my * math.sin(roll) + z_p * math.cos(roll)

            # 3. Posisi Baru Pangkal Paha (setelah rotasi + translasi badan)
            new_mount_x = x_p + tx
            new_mount_y = y_r + ty
            new_mount_z = z_r + tz

            # 4. Target Kaki di Dunia (Fixed on ground)
            world_x = self.footprints[i][0]
            world_y = self.footprints[i][1]
            world_z = self.footprints[i][2]

            # 5. Hitung Vektor IK (Target - Posisi Pangkal Paha Baru)
            rel_x = world_x - new_mount_x
            rel_y = world_y - new_mount_y
            rel_z = world_z - new_mount_z

            self.legs[i].compute_ik(rel_x, rel_y, rel_z)

    def walk_tripod(self, direction_deg=0):
        """Logika melangkah Tripod"""
        self.step_phase += config.GAIT_SPEED
        if self.step_phase > 1.0:
            self.step_phase = 0.0

        angle_rad = math.radians(direction_deg)
        
        for i in range(6):
            # Tentukan fase kaki (Grup B berlawanan dengan Grup A)
            leg_phase = self.step_phase
            if i in self.group_b:
                leg_phase = (self.step_phase + 0.5) % 1.0
            
            # Ambil posisi "Home" kaki di tanah
            base_x = self.footprints[i][0]
            base_y = self.footprints[i][1]
            base_z = self.footprints[i][2]

            # --- TRAJECTORY PLANNING ---
            if leg_phase < 0.5:
                # SWING PHASE (Kaki di udara, bergerak maju)
                # Normalisasi fase swing ke 0.0 - 1.0
                s_phase = leg_phase / 0.5 
                
                # Gerakan Horizontal (Maju dari -Length/2 ke +Length/2)
                offset_len = (s_phase - 0.5) * config.GAIT_STEP_LENGTH
                tx = base_x + math.cos(angle_rad) * offset_len
                ty = base_y + math.sin(angle_rad) * offset_len
                
                # Gerakan Vertikal (Parabola: naik lalu turun)
                # Menggunakan rumus sin(pi * phase) untuk lengkungan mulus
                tz = base_z + math.sin(s_phase * math.pi) * config.GAIT_STEP_HEIGHT
            else:
                # STANCE PHASE (Kaki di tanah, mendorong badan)
                # Normalisasi fase stance ke 0.0 - 1.0
                st_phase = (leg_phase - 0.5) / 0.5
                
                # Gerakan Horizontal (Mundur dari +Length/2 ke -Length/2)
                offset_len = (0.5 - st_phase) * config.GAIT_STEP_LENGTH
                tx = base_x + math.cos(angle_rad) * offset_len
                ty = base_y + math.sin(angle_rad) * offset_len
                
                tz = base_z # Tetap di tanah

            # Eksekusi IK
            self.legs[i].compute_ik(tx, ty, tz)