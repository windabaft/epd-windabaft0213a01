# epd-windabaft0213a01

Python driver for 2.13 inch e-Paper display (250×122, Black/White/Red)

## Features
- 3-color display (Black / White / Red)
- Pure Python: gpiozero + spidev only
- No Waveshare library dependency
- MIT License — free to use, modify, and distribute

## Hardware
| Item | Detail |
|------|--------|
| Panel | epd-windabaft0213a01 2.13 inch |
| Resolution | 250 × 122 px |
| Interface | 4-Wire SPI |
| Tested HAT | Waveshare e-Paper Driver HAT Rev2.3 |
| Board | Raspberry Pi Zero W |

## Installation
```bash
sudo apt install python3-gpiozero python3-spidev python3-pil fonts-noto-cjk
```

## Quick Start
```python
from epd_windabaft0213a01 import EPD
from PIL import Image, ImageDraw

epd = EPD()
epd.init()

bw  = Image.new('1', (250, 122), 255)
red = Image.new('1', (250, 122), 255)
ImageDraw.Draw(bw).text((10, 10), 'Hello!', fill=0)
ImageDraw.Draw(red).rectangle([(10,50),(200,90)], fill=0)

epd.display(bw, red)
epd.sleep()
epd.close()
```

## GPIO Wiring (BCM)
| Signal | GPIO | Physical Pin |
|--------|------|-------------|
| RST    | 17   | 11          |
| DC     | 25   | 22          |
| BUSY   | 24   | 18          |
| PWR    | 18   | 12          |
| CS     | 8    | 24          |
| SCLK   | 11   | 23          |
| MOSI   | 10   | 19          |

## License
MIT License — see [LICENSE](LICENSE)

## Manufacturer
[Windabaft Co., Ltd.](https://windabaft.co.jp)
