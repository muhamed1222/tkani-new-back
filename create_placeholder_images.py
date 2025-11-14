"""
Скрипт для создания placeholder изображений для работ
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(filename, text, width=800, height=600):
    """Создает placeholder изображение с текстом"""
    # Создаем изображение
    img = Image.new('RGB', (width, height), color='#F1F0EE')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать шрифт, если доступен
    try:
        # Для macOS
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        try:
            # Альтернативный шрифт
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            # Используем стандартный шрифт
            font = ImageFont.load_default()
    
    # Получаем размер текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Центрируем текст
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Рисуем текст
    draw.text((x, y), text, fill='#888888', font=font)
    
    # Сохраняем изображение
    img.save(filename)
    print(f"Создано: {filename}")

def main():
    # Путь к папке с изображениями
    basedir = os.path.abspath(os.path.dirname(__file__))
    works_folder = os.path.join(basedir, "static", "works")
    
    # Создаем папку, если не существует
    os.makedirs(works_folder, exist_ok=True)
    
    # Создаем placeholder изображения для всех работ
    for i in range(1, 16):
        filename = os.path.join(works_folder, f"work{i}.jpg")
        text = f"Work {i}\nPlaceholder"
        create_placeholder_image(filename, text)
    
    print(f"\n✅ Создано 15 placeholder изображений в {works_folder}")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
        main()
    except ImportError:
        print("❌ Ошибка: Pillow не установлен")
        print("Установите: pip install Pillow")
        print("\nАльтернатива: создайте изображения вручную в папке static/works/")

