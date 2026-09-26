"""Воспроизводимые учебные PNG из геометрических примитивов (только stdlib)."""
from pathlib import Path
import struct
import zlib


def png(path, width, height, pixel):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend(pixel(x, y))
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(bytes(rows), 9))
        + chunk(b'IEND', b'')
    )


def landscape(x, y):
    if (x - 345) ** 2 + (y - 55) ** 2 < 28 ** 2:
        return (255, 207, 91, 255)
    if y > 235 - x * 0.18:
        return (36, 109, 128, 255)
    if y > 70 + abs(x - 280) * 0.62:
        return (63, 116, 153, 255)
    if y > 50 + abs(x - 145) * 0.85:
        if y < 90:
            return (245, 249, 252, 255)
        return (85, 140, 179, 255)
    return (188 - y // 8, 222 - y // 14, 245, 255)


def skin(x, y):
    radius = 100
    cx = min(max(x, radius), 679 - radius)
    cy = min(max(y, radius), 479 - radius)
    if (x - cx) ** 2 + (y - cy) ** 2 > radius ** 2:
        return (0, 0, 0, 0)
    return (218 + y // 24, 235, 253, 225)


if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    png(folder / 'landscape.png', 440, 240, landscape)
    png(folder / 'window_skin.png', 680, 480, skin)
