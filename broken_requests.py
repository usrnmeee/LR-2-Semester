import requests

url = "https://httpbin.org/delay/10"   # имитируем медленный ответ

# BUG: нет timeout, нет проверки статуса, нет try/except
r = requests.get(url)

data = r.json()  # может упасть, если ответ не JSON
print("ok:", data["url"])