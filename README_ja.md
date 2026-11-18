# epd_windabaft0213a01 e-Paper ドライバ セットアップガイド

## ファイル構成と入手先

| ファイル | ライセンス | 内容 | 入手先 |
|---------|-----------|------|--------|
| `epd_windabaft0213a01.py` | MIT | e-Paperドライバ本体 | GitHub（本リポジトリ） |
| `demo_price_tag.py` | 独自ライセンス（再配布不可） | 電子棚札サンプル（パネル購入者向け） | https://windabaft.co.jp/epd/ |

- ドライバは本リポジトリで公開しています。自由に使用・改変・再配布できます（MIT）。
- 電子棚札サンプル `demo_price_tag.py` は**パネル購入者向け**です。パネルに同梱の紙のQRコード、または上記URLからダウンロードしてください。再配布はできません。
- 基本デモ（3色表示の確認）はドライバ単体で動作します。電子棚札サンプルは不要です。

---

## ハードウェア要件

| 項目 | 内容 |
|------|------|
| パネル | epd_windabaft0213a01 |
| 対応HAT | Waveshare e-Paper Driver HAT Rev2.3 |
| 対応ボード | Raspberry Pi Zero W / Zero 2W |
| 電源 | 2A以上のアダプター + **データ通信対応** MicroUSBケーブル |

> ⚠️ **充電専用USBケーブルは使用禁止です。** e-paperリフレッシュ時の電流スパイクでRaspberry Piが再起動します。

---

## GPIO ピン配置 (BCM番号)

| 信号 | GPIO | 物理ピン |
|------|------|----------|
| RST  | 17   | 11       |
| DC   | 25   | 22       |
| BUSY | 24   | 18       |
| PWR  | 18   | 12       |
| CS   | 8    | 24       |
| SCLK | 11   | 23       |
| MOSI | 10   | 19       |

---

## セットアップ手順

### 1. SPIを有効化する

```bash
sudo raspi-config
```
`Interface Options` → `SPI` → `Enable` を選択して再起動。

### 2. 必要なライブラリをインストール

```bash
sudo apt install python3-gpiozero python3-spidev python3-pil fonts-noto-cjk
pip install python-barcode --break-system-packages
```

### 3. Antonフォントをインストール（電子棚札サンプル使用時）

**Macのターミナルで：**
```bash
curl -L "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf" \
     -o ~/Downloads/Anton-Regular.ttf
scp ~/Downloads/Anton-Regular.ttf pi@<RPiのIPアドレス>:/tmp/
```

**RPiで：**
```bash
sudo mkdir -p /usr/share/fonts/truetype/anton
sudo mv /tmp/Anton-Regular.ttf /usr/share/fonts/truetype/anton/
sudo fc-cache -f
```

### 4. ドライバをダウンロード

**RPiで：**
```bash
curl -L "https://github.com/windabaft/epd-windabaft0213a01/raw/main/epd_windabaft0213a01.py" \
     -o ~/epd_windabaft0213a01.py
```

### 5. 電子棚札サンプルをダウンロード（購入者向け・任意）

https://windabaft.co.jp/epd/ からダウンロードします。

**RPiで直接取得する場合：**
```bash
curl -L "https://windabaft.co.jp/epd/download.php" -o ~/demo_price_tag.py
```

**Macでダウンロードして転送する場合：**
```bash
scp demo_price_tag.py pi@<RPiのIPアドレス>:~/
```

> 基本デモだけ試す場合は、この手順は不要です。

---

## 実行方法

### 基本デモ（3色表示確認）

```bash
python3 -B ~/epd_windabaft0213a01.py
```

### 画面クリア

```bash
python3 -B ~/epd_windabaft0213a01.py clear
```

### 電子棚札デモ（手順5でサンプルを取得した場合）

```bash
python3 -B ~/demo_price_tag.py
```

---

## 電子棚札のカスタマイズ

`demo_price_tag.py` 末尾の `main()` 内の変数を変更するだけです：

```python
def main():
    show_price_tag(
        header      = 'お買得品',       # ヘッダーテキスト
        product     = '商品名',          # 商品名
        unit        = '700ML',           # 単位
        price_excl  = '1,200',          # 税抜価格
        price_incl  = '1,320',          # 税込価格
        point_lines = ['10コで', '割引', '10％'],  # ポイント情報（最大3行）
        jan_code    = '4580386986571',  # JANコード13桁
    )
```

---

## EPDクラスの直接使用

```python
from epd_windabaft0213a01 import EPD
from PIL import Image, ImageDraw, ImageFont

epd = EPD()
epd.init()

# 画像サイズは必ず (250, 122) で作成
bw  = Image.new('1', (250, 122), 255)  # 白背景
red = Image.new('1', (250, 122), 255)  # 赤なし

draw   = ImageDraw.Draw(bw)
draw_r = ImageDraw.Draw(red)

# 黒テキスト
draw.text((10, 10), 'Hello!', fill=0)

# 赤い四角
draw_r.rectangle([(10, 50), (200, 90)], fill=0)

epd.display(bw, red)   # 表示（約20秒）
epd.sleep()            # Deep Sleep
epd.close()            # リソース解放
```

### EPDクラスのメソッド一覧

| メソッド | 説明 |
|---------|------|
| `init()` | 初期化（表示前に必ず呼ぶ） |
| `display(bw_image, red_image=None)` | 画像を表示する |
| `clear(white=True)` | 画面をクリアする |
| `sleep()` | Deep Sleepモードに移行 |
| `close()` | GPIO/SPIリソースを解放 |

---

## トラブルシューティング

| 症状 | 原因 | 解決策 |
|------|------|--------|
| 実行時にRPiが再起動する | 充電専用USBケーブル | データ通信対応ケーブルに交換 |
| 画像が逆向きに表示される | バッファ回転なし | `EPD.image_to_buffer()`を使用 |
| 赤色が表示されない | 赤RAMのビット反転なし | `display()`メソッドが自動処理 |
| ModuleNotFoundError | ライブラリ未インストール | セットアップ手順2を実行 |
| Antonフォントエラー | フォント未インストール | セットアップ手順3を実行 |

---

## お問い合わせ

電子棚札アプリケーションのカスタマイズ・導入支援については
別途お問い合わせください。
