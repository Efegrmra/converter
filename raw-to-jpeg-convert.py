import subprocess
import re
import numpy as np
import cv2
import sys
from pathlib import Path

def wsq_to_jpeg(wsq_path):
    wsq_path = Path(wsq_path)
    raw_path = wsq_path.with_suffix(".raw")
    jpg_path = wsq_path.with_suffix(".jpg")

    # 1. rdimgwh.exe ile width ve height değerlerini al
    try:
        result = subprocess.run(
            ["C:\\DevPrograms\\NBIS-old\\NBIS\\imgtools\\bin\\rdimgwh.exe", str(wsq_path)],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print("rdimgwh.exe çalıştırılamadı:", e)
        sys.exit(1)

    # Çıktı örneği: "test.wsq w=312 h=350"
    match = re.search(r"w=(\d+)\s+h=(\d+)", result.stdout)
    if not match:
        print("Genişlik / yükseklik okunamadı.")
        sys.exit(1)

    width, height = int(match.group(1)), int(match.group(2))
    print(f"Boyut: {width}x{height}")

    # 2. dwsq.exe ile WSQ -> RAW dönüştür
    try:
        subprocess.run(
            ["C:\\DevPrograms\\NBIS-old\\NBIS\\imgtools\\bin\\dwsq.exe", "raw", str(wsq_path), "-raw_out"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("dwsq.exe çalıştırılamadı:", e)
        sys.exit(1)

    # dwsq çıktısı muhtemelen test.raw adında oluşur
    if not raw_path.exists():
        raw_path = wsq_path.with_suffix(".raw")
        if not raw_path.exists():
            print("RAW dosyası bulunamadı.")
            sys.exit(1)

    # 3. RAW dosyasını oku ve JPEG olarak kaydet
    img = np.fromfile(raw_path, dtype=np.uint8)
    img = img.reshape((height, width))
    cv2.imwrite(str(jpg_path), img)
    print(f"JPEG kaydedildi: {jpg_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python wsq_to_jpeg.py test.wsq")
        sys.exit(1)

    wsq_to_jpeg(sys.argv[1])