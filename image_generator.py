import io

from PIL import Image, ImageDraw, ImageFont

# Preload resources once at startup
try:
    # Try Segoe UI (Windows standard) for a more pleasing look, fallback to Arial
    try:
        FONT = ImageFont.truetype("segoeuib.ttf", 22)
        HEADER_FONT = ImageFont.truetype("segoeuib.ttf", 30)
    except IOError:
        FONT = ImageFont.truetype("arialbd.ttf", 22)
        HEADER_FONT = ImageFont.truetype("arialbd.ttf", 30)
except IOError:
    FONT = ImageFont.load_default()
    HEADER_FONT = ImageFont.load_default()

try:
    WASHER_ICON = Image.open("images/washer.png").convert("RGBA").resize((100, 100))
    DRYER_ICON = Image.open("images/dryer.png").convert("RGBA").resize((100, 100))
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

    def draw_section(header_text, start_y, machine_list, icon):
        # Draw Icon
        if icon:
            image.paste(icon, (50, start_y + 20), icon)

        # Draw Header Text below icon
        draw.text(
            (100, start_y + 130),
            header_text,
            fill=text_color,
            font=HEADER_FONT,
            anchor="mt",
        )

        # Grid settings
        grid_x = 200
        box_w, box_h = 100, 80
        gap = 15

        for i, machine in enumerate(machine_list):
            row = i // 5
            col = i % 5

            x = grid_x + col * (box_w + gap)
            y = start_y + row * (box_h + gap)

            # Determine color and text
            if machine.time_left == 0:
                color = (46, 204, 113)  # Green
                status = "Free"
            elif machine.time_left <= 10:
                color = (241, 196, 15)  # Orange
                status = f"{machine.time_left}m"
            else:
                color = (231, 76, 60)  # Red
                status = f"{machine.time_left}m"

            # Draw rounded box
            draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=10, fill=color)

            # Draw Machine Number (Top Left)
            draw.text(
                (x + 10, y + 5), str(machine.index), fill=(255, 255, 255), font=FONT
            )

            # Draw Status (Center)
            draw.text(
                (x + box_w / 2, y + box_h / 2 + 10),
                status,
                fill=(255, 255, 255),
                font=FONT,
                anchor="mm",
            )

    draw_section("Washers", 40, machines["washer"], WASHER_ICON)
    draw_section("Dryers", 260, machines["dryer"], DRYER_ICON)

    # Save to BytesIO object so we can send it without saving to disk
    bio = io.BytesIO()
    bio.name = "status.png"
    image.save(bio, "PNG")
    bio.seek(0)
    return bio
