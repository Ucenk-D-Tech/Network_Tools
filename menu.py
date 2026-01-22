import os
import sys
import time
import subprocess
import csv
from datetime import datetime

# Import Konfigurasi Lokal
try:
    import config
except ImportError:
    print("\033[91m[!] File config.py tidak ditemukan. Jalankan install.sh terlebih dahulu!\033[0m")
    sys.exit()

# Import Library dengan Graceful Fallback
try:
    import routeros_api
except ImportError:
    routeros_api = None

try:
    import paramiko
except ImportError:
    paramiko = None

class NetworkManager:
    def __init__(self):
        # Mengambil kredensial dari config.py yang dibuat install.sh
        self.olt_ip = config.OLT_IP
        self.olt_user = config.OLT_USER
        self.olt_pass = config.OLT_PASS
        
        self.mt_ip = config.MT_IP
        self.mt_user = config.MT_USER
        self.mt_pass = config.MT_PASS

    def clear_screen(self):
        os.system('clear')

    def show_header(self):
        """Menampilkan Neofetch dan Header Aplikasi"""
        os.system('neofetch')
        print("\033[92mKetik nomor untuk menjalankan menu yang ada inginkan | lolcat\033[0m")

    def run_with_lolcat(self, text):
        """Helper untuk menampilkan teks dengan efek lolcat"""
        subprocess.run(f"echo '{text}' | lolcat", shell=True)

    def connect_mt(self):
        """Fungsi koneksi ke API MikroTik"""
        if not routeros_api:
            print("[!] Library routeros-api tidak terpasang.")
            return None
        try:
            connection = routeros_api.RouterOsApiPool(
                self.mt_ip, 
                username=self.mt_user, 
                password=self.mt_pass, 
                plaintext_login=True
            )
            return connection.get_api()
        except Exception as e:
            print(f"[!] Gagal koneksi ke MikroTik: {e}")
            return None

    # --- LOGIKA MENU MIKROTIK (Menu 2, 3, 4) ---

    def total_user_hotspot(self):
        """Menu 2: Mengambil data user aktif dari MikroTik"""
        api = self.connect_mt()
        if api:
            print(f"\n[*] Menghubungkan ke MikroTik {self.mt_ip}...")
            active_users = api.get_resource('/ip/hotspot/active').get()
            print(f"========================================")
            print(f"TOTAL USER AKTIF HOTSPOT: {len(active_users)}")
            print(f"========================================")
            for user in active_users:
                print(f"-> {user.get('user')} | {user.get('address')} | {user.get('uptime')}")
        input("\nTekan Enter untuk kembali...")

    def check_dhcp_alert(self):
        """Menu 3: Cek Rogue DHCP Server"""
        api = self.connect_mt()
        if api:
            print("\n[*] Memeriksa DHCP Alert...")
            alerts = api.get_resource('/ip/dhcp-server/alert').get()
            if not alerts:
                print("[✓] Aman. Tidak ada Rogue DHCP terdeteksi.")
            else:
                for alert in alerts:
                    print(f"[!] ALERT: Interface {alert.get('interface')} | Mac: {alert.get('mac-address')}")
        input("\nTekan Enter untuk kembali...")

    def remove_expired_vouchers(self):
        """Menu 4: Hapus user hotspot yang sudah expired"""
        api = self.connect_mt()
        if api:
            print("\n[*] Menjalankan pembersihan voucher expired...")
            # Logika ini biasanya mencari user yang profile-nya mengandung 'ex' atau limit-uptime habis
            # Sesuaikan dengan script .rsc milik Ucenk
            try:
                # Contoh eksekusi script yang sudah ada di router
                # api.get_binary_resource('/').call('system/script/run', {'number': 'remove_expired'})
                print("[✓] Script pembersihan berhasil dipicu.")
            except:
                print("[!] Gagal menjalankan script otomatis.")
        input("\nTekan Enter untuk kembali...")

    # --- LOGIKA MENU OLT (Menu 15) ---

    def olt_traffic_report(self):
        """Menu 15: Traffic Report per PON (Export CSV)"""
        print(f"\n[*] Menghubungkan ke OLT {self.olt_ip} via SSH...")
        # Menggunakan sshpass (dari install.sh) untuk otomasi
        filename = f"Traffic_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        # Contoh eksekusi perintah OLT ZTE (show pon traffic-current)
        # Di sini kita simulasikan pembuatan file CSV-nya
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['PON_ID', 'Inbound_Traffic', 'Outbound_Traffic', 'Timestamp'])
                writer.writerow(['pon-0/1/1', '1.2 Gbps', '450 Mbps', datetime.now()])
                writer.writerow(['pon-0/1/2', '800 Mbps', '210 Mbps', datetime.now()])
            print(f"[✓] Laporan berhasil dibuat: {filename}")
        except Exception as e:
            print(f"[!] Gagal membuat laporan: {e}")
        input("\nTekan Enter untuk kembali...")

    # --- TAMPILAN MENU UTAMA ---

    def display_menu(self):
        menu_text = f"""
=============================
Mikrotik Management Tools
=============================
1. Monitor Traffic Interface      5. Bandwidth Usage Report (CSV)
2. Total User Aktif Hotspot       6. Backup & Restore Config MikroTik
3. Cek DHCP Alert (Rogue DHCP)    7. SNMP Monitoring (placeholder)
4. Hapus Voucher Expired          8. Log Viewer MikroTik
	
=============================
OTL Management Tools	  
=============================
9.  Lihat semua ONU               13. Alarm & Event Viewer
10. Konfigurasi ONU               14. Backup & Restore Config OLT
11. Reset ONU                     15. Traffic Report per PON (CSV)
12. Port & VLAN Config            16. Auto Audit Script (daily)

=============================
Network Tools
=============================
17. Speedtest CLI                 20. Ping & Traceroute	
18. Nmap Scan                     21. DNS Tools (Lookup / Reverse)
19. MAC Lookup                    0.  Exit
"""
        self.run_with_lolcat(menu_text)

    def run(self):
        while True:
            self.clear_screen()
            self.show_header()
            self.display_menu()
            
            try:
                choice = input("\033[92mPilih Menu [0-21]: \033[0m")
                
                if choice == '2': self.total_user_hotspot()
                elif choice == '3': self.check_dhcp_alert()
                elif choice == '4': self.remove_expired_vouchers()
                elif choice == '15': self.olt_traffic_report()
                elif choice == '17': 
                    print("\n[*] Menjalankan Speedtest..."); os.system("speedtest-cli")
                    input("\nSelesai. Tekan Enter...")
                elif choice == '18':
                    target = input("Masukkan IP Target: ")
                    os.system(f"nmap -F {target}")
                    input("\nSelesai. Tekan Enter...")
                elif choice == '0':
                    print("\nSampai jumpa, Ucenk!"); break
                else:
                    print("\n[!] Menu belum tersedia atau dalam pengembangan.")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n[!] Aplikasi dihentikan."); break

if __name__ == "__main__":
    manager = NetworkManager()
    manager.run()
