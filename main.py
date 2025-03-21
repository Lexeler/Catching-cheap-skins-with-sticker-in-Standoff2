import time
import numpy as np
import pyautogui as pag
import easyocr
from PIL import Image

# Задаём координаты для разных областей экрана
COORDS = {
    'back': [287, 963],
    'click_galochka': [1080, 367],
    'buy_1': [1656, 462],
    'buy_2': [1030, 713],
    'price': [1352, 445, 168, 44],
    'button': [1617, 433, 200, 70],
    'galochka': [1050, 349, 45, 45],
}

# Создаем объект для распознавания текста
reader = easyocr.Reader(['en', 'ru'], gpu=True)

def click(coords, clicks=1, interval=0.2, button='left'):
    pag.click(coords[0], coords[1], clicks, interval, button)

def back():
    click(COORDS['back'])

def reload_screen():
    # Двойной клик по галочке для обновления
    click(COORDS['click_galochka'])
    click(COORDS['click_galochka'])

def buy():
    click(COORDS['buy_1'], clicks=1, interval=0.1)
    click(COORDS['buy_2'], clicks=1, interval=0.2)
    back()
    time.sleep(1)

def read_region(region):
    """Снимает скриншот указанной области и возвращает его в виде массива numpy"""
    screenshot = pag.screenshot(region=region)
    return np.array(screenshot)

def read_text_from_region(region):
    """Распознаёт текст в заданной области экрана"""
    image_np = read_region(region)
    texts = reader.readtext(image_np)
    return texts

def process_screen():
    """Получаем распознанный текст для цены и кнопки покупки"""
    text_price = read_text_from_region(COORDS['price'])
    text_button = read_text_from_region(COORDS['button'])
    return text_price, text_button

def main(threshold_price):
    counter = 0
    while True:
        counter += 1

        # Каждые 101 цикл обновляем экран двойным кликом по галочке
        if counter % 101 == 0:
            reload_screen()

        text_price, text_button = process_screen()

        # Если распознано не ровно по одному тексту в каждой области – пропускаем итерацию
        if len(text_price) != 1 or len(text_button) != 1:
            continue

        price_str = text_price[0][1].strip()[:-2]  # Отбрасываем последние 2 символа, если они не нужны
        button_text = text_button[0][1].strip()

        # Если кнопка не "КУПИТЬ", обновляем экран
        if button_text.upper() != 'КУПИТЬ':
            reload_screen()
            continue

        try:
            price = float(price_str)
            print('Price:', price)
        except ValueError:
            continue

        # Если цена меньше или равна пороговой – совершаем покупку
        if price <= threshold_price:
            print(f"Цена {price} меньше пороговой {threshold_price}, совершаем покупку!")
            buy()

        print("Итерация:", counter)

if __name__ == '__main__':
    # Задержка для переключения на нужное окно
    time.sleep(1)
    # Запрос пороговой цены у пользователя
    while True:
        try:
            threshold = float(input("Введите пороговую цену для покупки (например, 0.6): "))
            break
        except ValueError:
            print("Ошибка: введите корректное число.")

    main(threshold)
