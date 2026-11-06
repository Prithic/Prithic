"""Generate the profile's small, looping coffee support banner."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
font = ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf', 27)
small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 15)
frames = []
for i in range(48):
    phase = i * math.tau / 48
    image = Image.new('RGB', (560, 150), '#0d1117')
    d = ImageDraw.Draw(image)
    glow = int(100 + 45 * math.sin(phase))
    d.rounded_rectangle((3, 3, 556, 146), radius=24, fill='#101b2b', outline=(28, glow, 180), width=2)
    y = int(64 + 4 * math.sin(phase))
    d.ellipse((37, 119, 142, 128), fill='#192d43')
    d.rounded_rectangle((111, y+6, 139, y+39), radius=11, outline='#ffdd00', width=7)
    d.rounded_rectangle((49, y, 119, y+51), radius=13, fill='#ffdd00')
    d.ellipse((50, y-5, 118, y+9), fill='#fff1a0')
    d.ellipse((57, y-2, 111, y+5), fill='#573a24')
    for j in range(3):
        points = [(int(67+j*17+4*math.sin(phase+k/7+j)), int(y-13-k)) for k in range(24)]
        d.line(points, fill='#8ba6bc', width=2)
    d.text((171, 28), 'FUEL THE NEXT BUILD', font=small, fill='#7dd3fc')
    d.rounded_rectangle((167, 56, 524, 105), radius=13, fill='#ffdd00')
    d.text((194, 61), 'Buy me a coffee', font=font, fill='#17202d')
    d.text((174, 116), 'prithic  /  code, coffee & curiosity', font=small, fill='#a9bbce')
    frames.append(image)
output = ROOT / 'assets' / 'coffee-support.gif'
output.parent.mkdir(exist_ok=True)
frames[0].save(output, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
print(f'{output}: {output.stat().st_size:,} bytes, {len(frames)} frames')
