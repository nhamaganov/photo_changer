from PIL import Image, ImageDraw, ImageFont
import sys


def make_square_canvas(img: Image.Image) -> Image.Image:
    """Делает изображение квадратным по большей стороне."""
    w, h = img.size
    side = max(w, h)    # Выбираем максимальную сторону из возможных
    square = Image.new("RGB", (side, side), (255, 255, 255))
    square.paste(img, ((side - w) // 2, (side - h) // 2))   # Создаёт белый квадрат, в цет которого вставляется изображение лекарства
    return square


def draw_price_badge(image, price_number: str):
    """Создает прямоугольную плашку с ценой, прижатую к правому краю."""
    draw = ImageDraw.Draw(image)
    w, h = image.size

    # Размеры прямоугольника
    badge_width = int(w * 0.37)
    badge_height = int(h * 0.09)


    # Отступ только снизу
    margin_bottom = int(h * 0.13)

    x1 = w - badge_width      # вплотную к правому краю
    y1 = h - badge_height - margin_bottom
    x2 = w
    y2 = h - margin_bottom

    badge_color = (0, 94, 184)
    # --- скругление левых углов ---
    radius = badge_height // 2.8  # мягкое скругление слева

    # --- рисуем основное тело прямоугольника ---
    draw.rectangle((x1 + radius, y1, x2, y2), fill=badge_color)


    # верхний левый угол
    draw.pieslice(
        [x1, y1, x1 + radius * 2, y1 + radius * 2],
        180, 270,
        fill=badge_color
    )

    # нижний левый угол
    draw.pieslice(
        [x1, y2 - radius * 2, x1 + radius * 2, y2],
        90, 180,
        fill=badge_color
    )

    # прямоугольник между полукругами
    draw.rectangle((x1, y1 + radius, x1 + radius, y2 - radius), fill=badge_color)

    # --- Текст цены ---
    price_text = f"₽{price_number}"

    font_size = int(badge_height * 0.7)
    try:
        # font = ImageFont.truetype("fonts/RobotoCondensed-Regular.ttf", font_size)
        font = ImageFont.truetype("fonts/RobotoCondensed-Bold.ttf", font_size)
        # font = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), price_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = x1 + radius // 2 + (badge_width - text_w) // 2
    text_y = y1 + (badge_height - text_h) // 3.7

    draw.text((text_x, text_y), price_text, font=font, fill="white")


def draw_bottom_logo(image, bottom_logo_path: str):
    """Вставляет логотип с надписью 'Аптека низких цен' слева снизу."""
    w, h = image.size

    bottom_logo = Image.open(bottom_logo_path).convert("RGBA")
    bw, bh = bottom_logo.size

    # Масштаб: примерно 25–30% ширины итогового изображения
    target_width = int(w * 0.50)
    scale = target_width / bw
    target_height = int(bh * scale)

    bottom_logo_resized = bottom_logo.resize((target_width, target_height), Image.LANCZOS)

    margin_x = int(w * 0.035)
    margin_y = int(h * 0.09)

    x = margin_x
    y = h - target_height - margin_y

    image.paste(bottom_logo_resized, (x, y), bottom_logo_resized)


def make_image(
    product_path: str,
    price_number: str,
    output_path: str = "result.png",
    padding: int = 70,
    margin: int = 15,
    logo_scale: float = 0.90
):
    """
    Итог:
    - лекарство в центре
    - верхний логотип сверху
    - нижний логотип (с надписью) слева снизу
    - цена справа снизу
    - квадрат
    """

    top_logo_path = "logos/pharmacy_logo.png"
    bottom_logo_path = "logos/apteka.png"

    # ЛЕКАРСТВО
    product_img = Image.open(product_path).convert("RGBA")
    pw, ph = product_img.size

    # ХОЛСТ
    canvas = Image.new("RGB", (pw + 2 * padding, ph + 2 * padding), (255, 255, 255))
    canvas.paste(product_img, (padding, padding), product_img)

    # ВЕРХНИЙ ЛОГОТИП
    logo_img = Image.open(top_logo_path).convert("RGBA")
    lw, lh = logo_img.size

    target_logo_width = int(canvas.size[0] * logo_scale * 0.9)
    scale = target_logo_width / lw
    target_logo_height = int(lh * scale)
    
    logo_resized = logo_img.resize((target_logo_width, target_logo_height), Image.LANCZOS)
    logo_x = (canvas.size[0] - target_logo_width) // 2
    canvas.paste(logo_resized, (logo_x, margin), logo_resized)

    # КВАДРАТ
    square_canvas = make_square_canvas(canvas)

    # НИЖНИЙ ЛОГОТИП (с текстом)
    draw_bottom_logo(square_canvas, bottom_logo_path)

    # ЦЕНА
    draw_price_badge(square_canvas, price_number)

    # СОХРАНЕНИЕ
    square_canvas.save(output_path)
    print(f"Готово! Изображение сохранено: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python script.py <лекарство> <цена> [результат.png]")
        sys.exit(1)

    product_path = sys.argv[1]
    price_number = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) >= 4 else "result.png"

    make_image(product_path, price_number, output_path)
