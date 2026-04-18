import random
import time
import logging
import requests

# --- Ayarlar ---
MACHINE_ID = "MAKINE_001"
SEND_INTERVAL = 2       # saniye cinsinden gönderim aralığı
MAX_RETRIES = 5
RETRY_DELAY = 3         # yeniden deneme bekleme süresi (saniye)

API_URL = "http://10.52.10.188:8000/measurements"

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def fake_data() -> dict:
    return {
        "machine_id":   MACHINE_ID,
        "voltage":      round(random.uniform(218.0, 223.0), 2),
        "current":      round(random.uniform(2.0, 5.0), 3),
        "power":        round(random.uniform(500.0, 1100.0), 2),
        "energy":       round(random.uniform(0.5, 10.0), 3),
        "frequency":    round(random.uniform(49.8, 50.2), 2),
        "power_factor": round(random.uniform(0.90, 1.00), 3),
    }


def send_with_retry(payload: dict):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            if response.status_code == 200:
                log.info("Gönderildi (HTTP %d) -> %s", response.status_code, payload)
                return
            else:
                log.warning(
                    "Sunucu hatası (deneme %d/%d): HTTP %d - %s",
                    attempt, MAX_RETRIES, response.status_code, response.text,
                )
        except requests.exceptions.ConnectionError as exc:
            log.warning("Bağlantı hatası (deneme %d/%d): %s", attempt, MAX_RETRIES, exc)
        except requests.exceptions.Timeout:
            log.warning("Zaman aşımı (deneme %d/%d)", attempt, MAX_RETRIES)
        except Exception as exc:
            log.error("Beklenmedik hata (deneme %d/%d): %s", attempt, MAX_RETRIES, exc)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    log.error("Veri gönderilemedi, atlanıyor: %s", payload)


def main():
    log.info("Veri gönderimi başlıyor -> %s", API_URL)
    while True:
        payload = fake_data()
        log.info("Ölçüm: %s", payload)
        send_with_retry(payload)
        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
