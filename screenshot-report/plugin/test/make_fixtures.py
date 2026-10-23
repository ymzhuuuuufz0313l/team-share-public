from PIL import Image, ImageDraw, ImageFont
import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"); os.makedirs(F, exist_ok=True)
mono = lambda s: ImageFont.truetype("C:/Windows/Fonts/consola.ttf", s)

# f_white_rect.png : 1000x700 白底，黑实心矩形，精确覆盖 x=100..299 / y=50..149（200x100 px）
img = Image.new("RGB", (1000, 700), (255, 255, 255))
ImageDraw.Draw(img).rectangle([100, 50, 299, 149], fill=(0, 0, 0))
img.save(os.path.join(F, "f_white_rect.png"))

# f_small.png : 400x300 灰噪底 + 黑字 "SMALL"（短边<480 → too_small）
img = Image.new("RGB", (400, 300), (200, 200, 200))
ImageDraw.Draw(img).text((120, 130), "SMALL", font=mono(36), fill=(0, 0, 0))
img.save(os.path.join(F, "f_small.png"))

# f_table.png : 900x420 白底，3x4 表格（黑线框 + Consolas 28 黑字）
img = Image.new("RGB", (900, 420), (255, 255, 255)); d = ImageDraw.Draw(img)
cells = [["Corner", "WNS", "TNS", "NVP"],
         ["setup", "-0.012", "-1.234", "3"],
         ["hold", "0.045", "0.000", "0"],
         ["trans", "-0.301", "-9.870", "12"]]
for r in range(4):
    for c in range(4):
        x, y = 60 + c * 200, 60 + r * 80
        d.rectangle([x, y, x + 190, y + 70], outline=(0, 0, 0), width=2)
        d.text((x + 12, y + 18), cells[r][c], font=mono(28), fill=(0, 0, 0))
img.save(os.path.join(F, "f_table.png"))

# f_thin.png : 4000x480 白底 + 一排黑矩形（短边恰 480 不触 short_edge；aspect 8.33>8 只触 aspect_gt_8）
img = Image.new("RGB", (4000, 480), (255, 255, 255)); d = ImageDraw.Draw(img)
for i in range(20):
    d.rectangle([100 + i * 190, 160, 160 + i * 190, 320], fill=(0, 0, 0))
img.save(os.path.join(F, "f_thin.png"))
print("fixtures written to", F)
