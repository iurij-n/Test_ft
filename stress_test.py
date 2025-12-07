import requests
from concurrent.futures import ThreadPoolExecutor


URL = "http://127.0.0.1:8000/api/transfer/"
TOTAL_REQUESTS = 10
AMOUNT = "100.00"


def make_transfer(_):
    payload = {
        "from_user_id": 2,   # alice
        "to_user_id": 3,     # bob
        "amount": AMOUNT
    }
    try:
        response = requests.post(URL, json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            return True, data.get("new_balance", "???")
        else:
            return False, f"Error {response.status_code} → {response.text[:200]}"
    except Exception as e:
        return False, f"Исключение: {e}"


if __name__ == "__main__":
    print(f"Запускаем {TOTAL_REQUESTS} одновременных переводов по {AMOUNT} u. с Alice → Bob\n")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(make_transfer, range(TOTAL_REQUESTS)))

    success = sum(1 for ok, _ in results if ok)
    print(f"\nУСПЕШНО: {success}/{TOTAL_REQUESTS}")

    for i, (ok, info) in enumerate(results):
        status = "OK" if ok else "FAIL"
        print(f"  Запрос {i+1}: {status} → новый баланс Alice: {info}")
