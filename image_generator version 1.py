import io

from PIL import Image, ImageDraw, ImageFont

# Preload resources once at startup
try:
    # Try Segoe UI (Windows standard) for a more pleasing look, fallback to Arial
    try:
        FONT = ImageFont.truetype("segoeuib.ttf", 26)
        HEADER_FONT = ImageFont.truetype("segoeuib.ttf", 30)
    except IOError:
        FONT = ImageFont.truetype("arialbd.ttf", 26)
        HEADER_FONT = ImageFont.truetype("arialbd.ttf", 30)
except IOError:
    FONT = ImageFont.load_default()
    HEADER_FONT = ImageFont.load_default()

try:
    WASHER_ICON = Image.open("images/washer.png").convert("RGBA").resize((55, 55))
    DRYER_ICON = Image.open("images/dryer.png").convert("RGBA").resize((55, 55))
except IOError:
    WASHER_ICON = None
    DRYER_ICON = None


def create_status_image(machines):
    """Generates an image representation of the machine statuses."""
    # Image settings
    width, height = 800, 500
    bg_color = (40, 44, 52)  # Night mode background
    text_color = (220, 223, 228)  # Night mode text

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Draw Washers Header
    draw.text((50, 15), "Washers", fill=text_color, font=HEADER_FONT)

    # Helper to draw a machine row
    def draw_machine(x, y, machine, icon):
        # Determine color based on status
        if machine.time_left == 0:
            color = (46, 204, 113)  # Green
        elif machine.time_left <= 10:
            color = (241, 196, 15)  # Orange
        else:
            color = (231, 76, 60)  # Red

        # Draw Icon or Fallback
        if icon:
            image.paste(icon, (x, y), icon)
            # Draw status dot
            draw.ellipse(
                [x + 35, y + 35, x + 59, y + 59], fill=color, outline=bg_color, width=3
            )
        else:
            # Fallback: Draw a colored circle if icon is missing
            draw.ellipse([x, y, x + 52, y + 52], fill=color, outline=text_color)

        # Draw Machine Number Centered Below
        draw.text(
            (x + 28, y + 62),
            str(machine.index),
            fill=text_color,
            font=FONT,
            anchor="mt",
        )

        # Draw Time to the Right
        if machine.time_left > 0:
            draw.text(
                (x + 65, y + 26),
                f"{machine.time_left}m",
                fill=text_color,
                font=FONT,
                anchor="lm",
            )

    # Draw Washers (Grid 2 rows x 5 cols)
    for i, washer in enumerate(machines["washer"]):
        row = i // 5
        col = i % 5
        x = 50 + col * 150
        y = 70 + row * 90
        draw_machine(x, y, washer, WASHER_ICON)

    # Draw Dryers Header
    draw.text((50, 255), "Dryers", fill=text_color, font=HEADER_FONT)

    # Draw Dryers (Grid 2 rows x 5 cols)
    for i, dryer in enumerate(machines["dryer"]):
        row = i // 5
        col = i % 5
        x = 50 + col * 150
        y = 310 + row * 90
        draw_machine(x, y, dryer, DRYER_ICON)

    # Save to BytesIO object so we can send it without saving to disk
    bio = io.BytesIO()
    bio.name = "status.png"
    image.save(bio, "PNG")
    bio.seek(0)
    return bio
