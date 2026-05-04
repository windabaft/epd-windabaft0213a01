"""
epd_windabaft0213a01.py
=======================
対応パネル : epd_windabaft0213a01
ドライバIC : SEA330
解像度     : 250 x 122 ピクセル (黒 / 白 / 赤)
インターフェース: 4-Wire SPI
動作確認HAT: Waveshare e-Paper Driver HAT Rev2.3

MIT License
Copyright (c) 2024 Windabaft Co.,Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

■ 必要なライブラリ
    sudo apt install python3-gpiozero python3-spidev python3-pil fonts-noto-cjk

■ SPI有効化
    sudo raspi-config → Interface Options → SPI → Enable

■ GPIO ピン配置 (BCM番号)
    RST  : GPIO17 (物理ピン11)
    DC   : GPIO25 (物理ピン22)
    BUSY : GPIO24 (物理ピン18)
    PWR  : GPIO18 (物理ピン12)
    CS   : GPIO8  (SPI0 CE0、物理ピン24)
    SCLK : GPIO11 (SPI0 SCLK、物理ピン23)
    MOSI : GPIO10 (SPI0 MOSI、物理ピン19)

■ 基本的な使い方
    from epd_windabaft0213a01 import EPD
    from PIL import Image, ImageDraw

    epd = EPD()
    epd.init()

    # 画像サイズは (250, 122) で作成する
    # 白黒レイヤー: 白=255, 黒=0
    bw = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(bw)
    draw.text((10, 10), 'Hello!', fill=0)

    # 赤レイヤー: 赤なし=255, 赤あり=0
    red = Image.new('1', (250, 122), 255)
    draw_r = ImageDraw.Draw(red)
    draw_r.rectangle([(10, 50), (100, 80)], fill=0)

    epd.display(bw, red)
    epd.sleep()
    epd.close()
"""

import time
import spidev
import gpiozero

# ── GPIO ピン番号 (BCM) ──────────────────────────────────────────────
PIN_RST  = 17
PIN_DC   = 25
PIN_BUSY = 24
PIN_PWR  = 18

# ── 画面解像度 ────────────────────────────────────────────────────────
EPD_WIDTH  = 250   # 横方向
EPD_HEIGHT = 122   # 縦方向


class EPD:
    """epd_windabaft0213a01 e-Paper ディスプレイドライバ"""

    WIDTH  = EPD_WIDTH
    HEIGHT = EPD_HEIGHT

    def __init__(self):
        self._rst  = None
        self._dc   = None
        self._pwr  = None
        self._busy = None
        self._spi  = None
        self._bufsz = 250 * 15   # 3750バイト (250列 × 122行 ÷ 8bit)

    # ────────────────────────────────────────────────────────────────
    #  初期化 / 終了
    # ────────────────────────────────────────────────────────────────
    def init(self):
        """ディスプレイを初期化する。表示前に必ず呼ぶこと。"""
        self._gpio_open()
        self._spi_open()
        self._pwr.on()
        self._hw_reset()
        self._wait_busy()
        self._sw_reset()
        self._configure()

    def close(self):
        """GPIO/SPIリソースを解放する。使用後に呼ぶこと。"""
        if self._spi is not None:
            self._spi.close()
            self._spi = None
        for pin in [self._rst, self._dc, self._pwr, self._busy]:
            if pin is not None:
                pin.close()
        self._rst = self._dc = self._pwr = self._busy = None

    # ────────────────────────────────────────────────────────────────
    #  GPIO / SPI 低レベル操作
    # ────────────────────────────────────────────────────────────────
    def _gpio_open(self):
        self._rst  = gpiozero.LED(PIN_RST)
        self._dc   = gpiozero.LED(PIN_DC)
        self._pwr  = gpiozero.LED(PIN_PWR)
        self._busy = gpiozero.Button(PIN_BUSY, pull_up=False)

    def _spi_open(self):
        self._spi = spidev.SpiDev()
        self._spi.open(0, 0)
        self._spi.max_speed_hz = 4_000_000
        self._spi.mode = 0

    def _write_cmd(self, cmd: int):
        self._dc.off()
        self._spi.writebytes2([cmd])

    def _write_data(self, data):
        self._dc.on()
        if isinstance(data, int):
            self._spi.writebytes2([data])
        else:
            self._spi.writebytes2(list(data))

    def _hw_reset(self):
        self._rst.on();  time.sleep(0.02)
        self._rst.off(); time.sleep(0.002)
        self._rst.on();  time.sleep(0.02)

    def _wait_busy(self, timeout: float = 30.0):
        deadline = time.time() + timeout
        time.sleep(0.01)
        while self._busy.value == 1:
            if time.time() > deadline:
                raise TimeoutError("EPD: BUSY timeout")
            time.sleep(0.01)

    # ────────────────────────────────────────────────────────────────
    #  ドライバIC初期化シーケンス
    # ────────────────────────────────────────────────────────────────
    def _sw_reset(self):
        self._write_cmd(0x12)
        time.sleep(0.5)

    def _configure(self):
        self._write_cmd(0x01); self._write_data([0xF9, 0x00, 0x00])
        self._write_cmd(0x11); self._write_data(0x03)
        self._write_cmd(0x44); self._write_data([0x00, 0x0F])
        self._write_cmd(0x45); self._write_data([0x00, 0x00, 0xF9, 0x00])
        self._write_cmd(0x3C); self._write_data(0x05)
        self._write_cmd(0x21); self._write_data([0x00, 0x80])
        self._write_cmd(0x18); self._write_data(0x80)
        self._reset_cursor()
        time.sleep(0.1)

    def _reset_cursor(self):
        self._write_cmd(0x4E); self._write_data(0x00)
        self._write_cmd(0x4F); self._write_data([0x00, 0x00])

    # ────────────────────────────────────────────────────────────────
    #  画像バッファ変換
    # ────────────────────────────────────────────────────────────────
    @staticmethod
    def image_to_buffer(image) -> bytes:
        """
        PIL Image (250x122) → e-Paper用バイトバッファに変換する。
        画像は90度回転してから変換する。
        """
        img = image.convert('1').rotate(90, expand=True)
        return bytes(img.tobytes('raw'))

    # ────────────────────────────────────────────────────────────────
    #  表示
    # ────────────────────────────────────────────────────────────────
    def display(self, bw_image, red_image=None):
        """
        画像を表示する。

        bw_image  : 黒白レイヤー (PIL Image, サイズ 250x122)
                    白=255 → 白表示、黒=0 → 黒表示
        red_image : 赤レイヤー (PIL Image, サイズ 250x122、省略時は赤なし)
                    赤なし=255、赤あり=0
        """
        self._reset_cursor()

        bw_buf = self.image_to_buffer(bw_image)
        self._write_cmd(0x24)
        self._write_data(bw_buf)

        self._write_cmd(0x26)
        if red_image is not None:
            red_buf = self.image_to_buffer(red_image)
            self._write_data(bytes([~b & 0xFF for b in red_buf]))
        else:
            self._write_data([0x00] * self._bufsz)

        self._write_cmd(0x22)
        self._write_data(0xF7)
        self._write_cmd(0x20)
        self._wait_busy()

    def clear(self, white: bool = True):
        """画面をクリアする。white=True で白、False で黒。"""
        color = 0xFF if white else 0x00
        self._reset_cursor()
        self._write_cmd(0x24); self._write_data([color] * self._bufsz)
        self._write_cmd(0x26); self._write_data([0x00]  * self._bufsz)
        self._write_cmd(0x22); self._write_data(0xF7)
        self._write_cmd(0x20)
        self._wait_busy()

    def sleep(self):
        """Deep Sleepモードに移行する。再表示にはinit()が必要。"""
        self._write_cmd(0x10)
        self._write_data(0x01)
        time.sleep(0.1)
        if self._pwr is not None:
            self._pwr.off()


# ────────────────────────────────────────────────────────────────────
#  基本デモ (MITライセンス)
# ────────────────────────────────────────────────────────────────────
def demo_basic():
    """基本デモ: テキストと図形を3色で表示する"""
    from PIL import Image, ImageDraw, ImageFont

    print("=== epd_windabaft0213a01 e-Paper デモ ===")

    FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    try:
        f_large  = ImageFont.truetype(BOLD, 20)
        f_medium = ImageFont.truetype(FONT, 14)
        f_small  = ImageFont.truetype(FONT, 11)
    except OSError:
        f_large = f_medium = f_small = ImageFont.load_default()

    epd = EPD()
    print("初期化中...")
    epd.init()

    bw = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    d  = ImageDraw.Draw(bw)
    d.rectangle([(0,0),(EPD_WIDTH-1, EPD_HEIGHT-1)], outline=0, width=2)
    d.text((8,  8), 'epd_windabaft0213a01',     font=f_large,  fill=0)
    d.text((8, 36), '250×122  3色表示',   font=f_medium, fill=0)
    d.text((8, 58), 'Black / White / Red', font=f_small,  fill=0)
    d.line([(0, 76), (EPD_WIDTH, 76)],     fill=0, width=1)
    d.text((8, 82), 'Raspberry Pi Zero W', font=f_small,  fill=0)

    red = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    dr  = ImageDraw.Draw(red)
    dr.rectangle([(8, 96), (160, 116)], fill=0)
    dr.text((14, 99), '赤色エリア', font=f_small, fill=255)

    print("表示中（約20秒）...")
    epd.display(bw, red)
    print("完了！")
    epd.sleep()
    epd.close()


# ────────────────────────────────────────────────────────────────────
#  コマンドライン実行
# ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        epd = EPD()
        epd.init()
        epd.clear()
        epd.sleep()
        epd.close()
        print("クリア完了")
    else:
        demo_basic()
