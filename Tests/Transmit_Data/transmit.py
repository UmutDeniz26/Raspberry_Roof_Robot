import socket
import time

# Sensörden okunan veri için örnek fonksiyon
def read_distance_sensor():
    # Gerçek uygulamada burada sensörden veri okunacak
    # Örneğin: return some_sensor_library.read_distance()
    return "5 metre"

# Sunucu IP'si ve portu
host = '192.168.1.13'
port = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()

    print(f"Sunucu {host} üzerinde {port} portu dinleniyor...")

    conn, addr = s.accept()
    with conn:
        print(f"Bağlanan adres: {addr}")
        while True:
            try:
                # Sensörden mesafe verisini oku
                #distance = read_distance_sensor()
                # Veriyi gönder
                conn.sendall(f"Mesafe: {5}\n".encode('utf-8'))
                # Her saniyede bir güncelleme gönder
                time.sleep(1)
            except BrokenPipeError:
                # İstemci bağlantıyı keserse döngüyü kır
                print("İstemci bağlantıyı kesti.")
                break