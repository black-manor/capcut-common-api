# CapCut Translate API Client

*[For English documentation, please scroll down](#english-guide)*

Script Python độc lập dùng để tương tác với API dịch tự động (Translate Sync) của CapCut. Script này hỗ trợ lấy nội dung từ file `.srt`, dịch hàng loạt các câu thoại sang ngôn ngữ mục tiêu và xuất thẳng ra file `.srt` mới.

## Cài đặt

Yêu cầu Python 3 và thư viện `requests`. Cài đặt bằng lệnh:

```bash
pip install requests
```

## Các tham số (Arguments)

- `--srt-file`: (Bắt buộc nếu không dùng utterances) Đường dẫn đến file `.srt` gốc cần dịch.
- `--target-language`: Ngôn ngữ đích cần dịch sang. Mặc định là `vi-VN` (Tiếng Việt). (Vd: `en`, `zh-CN`, `ja`, `ko`...).
- `--out-srt`: Đường dẫn file `.srt` xuất ra sau khi dịch xong.
- `--out`: (Tuỳ chọn) Đường dẫn để xuất kết quả trả về của API ra dạng JSON thô.
- `--utterances-file`: (Tuỳ chọn) File JSON chứa danh sách mảng `utterances` nếu bạn không muốn dùng SRT.
- `--source-language`: (Tuỳ chọn) Ngôn ngữ gốc của file, mặc định là `UNSPECIFIED` (tự động nhận diện).

## Hướng dẫn sử dụng

### 1. Dịch file SRT sang Tiếng Việt (mặc định)

Chạy lệnh đọc file `input.srt` và xuất ra `output_vi.srt`:

```bash
python capcut_translate_client.py --srt-file input.srt --out-srt output_vi.srt
```

### 2. Dịch file SRT sang Tiếng Anh

Chỉ định ngôn ngữ đích bằng `--target-language en`:

```bash
python capcut_translate_client.py --srt-file input.srt --target-language en --out-srt output_en.srt
```

### 3. Lưu kèm log JSON để debug

Nếu bạn muốn xem chi tiết các từ (words level) hoặc thông tin thêm từ API:

```bash
python capcut_translate_client.py --srt-file input.srt --target-language vi-VN --out-srt output.srt --out debug.json
```

## Cấu trúc hoạt động

1. **Đọc và Parse**: Tự động parse file `.srt`, bóc tách `start_time`, `end_time` và text.
2. **Ký Request**: Sinh `bind_id` và các thông số cần thiết để ký API, giả lập request xuất phát từ CapCut PC.
3. **Gọi API**: Đẩy toàn bộ cấu trúc câu lên `/lv/v1/common_task/sync` cùng với `req_key: cc_audio_subtitle_translate`.
4. **Build Kết Quả**: Đọc gói JSON trả về và map với timeline gốc, sinh file SRT đích theo định dạng chuẩn UTF-8.

## Ủng hộ dự án (Donate)

Nếu bạn thấy tool này hữu ích và giúp tiết kiệm thời gian, hãy cân nhắc ủng hộ mình nhé. Mọi đóng góp đều là động lực lớn để mình tiếp tục duy trì và phát triển các tool tiện ích hơn nữa! ❤️

**USDT (Mạng BSC - BEP20)**
`0xc422ca8e49e3047a30237b2ce0deefccd8af8929`

<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=0xc422ca8e49e3047a30237b2ce0deefccd8af8929" alt="Donate QR Code" width="200"/>

---

# English Guide

Standalone Python script for interacting with CapCut's automated translation API (Translate Sync). This script extracts content from `.srt` files, batches translation of utterances to the target language, and outputs directly to a new `.srt` file.

## Installation

Requires Python 3 and the `requests` library. Install it using:

```bash
pip install requests
```

## Arguments

- `--srt-file`: (Required if not using utterances) Path to the original `.srt` file to translate.
- `--target-language`: The target language for translation. Default is `vi-VN` (Vietnamese). (e.g., `en`, `zh-CN`, `ja`, `ko`...).
- `--out-srt`: The path to output the translated `.srt` file.
- `--out`: (Optional) The path to output the raw JSON API response.
- `--utterances-file`: (Optional) JSON file containing an array of `utterances` if you prefer not to use an SRT file.
- `--source-language`: (Optional) The source language of the file, default is `UNSPECIFIED` (auto-detect).

## Usage Examples

### 1. Translate SRT to Vietnamese (default)

Parse `input.srt` and output to `output_vi.srt`:

```bash
python capcut_translate_client.py --srt-file input.srt --out-srt output_vi.srt
```

### 2. Translate SRT to English

Specify the target language with `--target-language en`:

```bash
python capcut_translate_client.py --srt-file input.srt --target-language en --out-srt output_en.srt
```

### 3. Save JSON log for debugging

If you want to see word-level details or extra info returned by the API:

```bash
python capcut_translate_client.py --srt-file input.srt --target-language vi-VN --out-srt output.srt --out debug.json
```

## How It Works

1. **Read & Parse**: Automatically parses the `.srt` file, extracting `start_time`, `end_time`, and text.
2. **Sign Request**: Generates a `bind_id` and the necessary parameters to sign the API request, simulating a request from CapCut PC.
3. **Call API**: Pushes the entire utterance structure to `/lv/v1/common_task/sync` along with `req_key: cc_audio_subtitle_translate`.
4. **Build Result**: Reads the returned JSON package, maps it to the original timeline, and generates the target SRT file in standard UTF-8 format.

## Support / Donate

If you find this tool helpful and it saves you time, please consider buying me a coffee. Any support is greatly appreciated and motivates me to build more useful tools! ❤️

**USDT (BSC - BEP20 Network)**
`0xc422ca8e49e3047a30237b2ce0deefccd8af8929`

<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=0xc422ca8e49e3047a30237b2ce0deefccd8af8929" alt="Donate QR Code" width="200"/>
