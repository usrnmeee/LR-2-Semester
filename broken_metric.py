# pseudo-example: осадки в мм, но кто-то решил, что это метры.
precipitation_mm = 12.0

# BUG: неверное преобразование единиц
precipitation_m = precipitation_mm / 1000  # ок
precipitation_mm_wrong = precipitation_m * 1000 * 1000  # стало в 1000 раз больше

print(precipitation_mm_wrong)

precipitation_mm_back = precipitation_m * 1000
print(precipitation_mm_back)

assert abs(precipitation_mm_back - precipitation_mm) < 1e-9, "Unit conversion mismatch!"