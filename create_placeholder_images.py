"""
Скрипт для создания placeholder изображений для работ
"""
import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(filename, width=400, height=400, text="", bg_color=(240, 240, 240), text_color=(100, 100, 100)):
    """Создает placeholder изображение"""
    # Создаем изображение
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт
    try:
        # Для macOS
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        try:
            # Для Linux
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            # Используем стандартный шрифт
            font = ImageFont.load_default()
    
    # Рисуем текст по центру
    if text:
        # Получаем размер текста
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Позиционируем текст по центру
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=text_color, font=font)
    
    # Сохраняем изображение
    img.save(filename, 'JPEG', quality=85)
    print(f"✅ Создано: {filename}")

def main():
    # Определяем путь к папке с изображениями
    basedir = os.path.abspath(os.path.dirname(__file__))
    works_folder = os.path.join(basedir, "static", "works")
    
    # Создаем папку, если её нет
    os.makedirs(works_folder, exist_ok=True)
    
    # Создаем 15 placeholder изображений
    for i in range(1, 16):
        filename = os.path.join(works_folder, f"work{i}.jpg")
        text = f"Work {i}"
        create_placeholder_image(filename, text=text)
    
    print(f"\n✅ Создано 15 placeholder изображений в {works_folder}")

if __name__ == "__main__":
    main()
