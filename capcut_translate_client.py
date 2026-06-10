#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import time
import uuid
from copy import deepcopy
from urllib.parse import urlencode, urlsplit

try:
    import requests
except ImportError:
    requests = None


BASE = "https://editor-api-sg.capcutapi.com"

DEFAULT_DEVICE = {
    "aid": "359289",
    "app_name": "CapCut",
    "appvr": "8.7.0",
    "version_name": "8.7.0",
    "version_code": "8.7.0",
    "channel": "capcutpc_google",
    "device_platform": "mac",
    "device_type": "MacBookPro17,1",
    "device_brand": "MacBookPro17,1",
    "os_version": "15.7.4",
    "device_id": "7647183892936328721",
    "iid": "7647185302080423697",
    "region": "VN",
    "loc": "VN",
    "lan": "vi-VN",
    "pf": "3",
    "tdid": "7647183892936328721",
}


def compact_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def load_json(path, default=None):
    if not path:
        return deepcopy(default) if default is not None else {}
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(obj, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def make_x_ss_stub(body_text):
    return hashlib.md5(body_text.encode("utf-8")).hexdigest()


def make_trace_id():
    seed = uuid.uuid4().hex[:32]
    return f"00-{seed}-{seed[:16]}-01"


def make_sign_header(url, appvr, device_time, tdid):
    path = url.split("?", 1)[0]
    sign_str = f"9e2c|{path[-7:]}|3|{appvr}|{device_time}|{tdid}|11ac"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()


def common_query(device, babi_param=None, include_region=True):
    q = {
        "app_name": device["app_name"],
        "device_type": device["device_type"],
        "os_version": device["os_version"],
        "channel": device["channel"],
        "version_name": device["version_name"],
        "device_brand": device["device_brand"],
        "device_id": device["device_id"],
        "iid": device["iid"],
        "version_code": device["version_code"],
        "device_platform": device["device_platform"],
        "aid": device["aid"],
    }
    if include_region:
        q["region"] = device["region"]
    if babi_param is not None:
        q["babi_param"] = compact_json(babi_param)
    return q


def base_headers(device, body_text, appid=False):
    now = str(int(time.time()))
    headers = {
        "content-type": "application/json",
        "appvr": device["appvr"],
        "ch": device["channel"],
        "device-time": now,
        "lan": device["lan"],
        "loc": device["loc"],
        "pf": device["pf"],
        "sign-ver": "1",
        "tdid": device["tdid"],
        "x-ss-stub": make_x_ss_stub(body_text),
        "x-ss-dp": device["aid"],
        "x-khronos": now,
        "x-tt-trace-id": make_trace_id(),
        "user-agent": "Cronet/TTNetVersion:1d7cc3b1 2025-07-16 QuicVersion:52c2b40d 2025-04-03",
        "accept-encoding": "gzip, deflate",
        "store-country-code": device["loc"].lower(),
        "store-country-code-src": "did",
        "is-dispatch-us-ttp": "0",
        "is-app-region-us-ttp": "0",
    }
    if appid:
        headers["app-sdk-version"] = device["appvr"]
        headers["appid"] = device["aid"]
    return headers


def parse_srt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content.strip())
    utterances = []
    time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})')

    for block in blocks:
        lines = [line.strip() for line in block.strip().split('\n')]
        if len(lines) < 3:
            continue
        time_line = lines[1]
        match = time_pattern.search(time_line)
        if not match:
            continue

        def to_ms(h, m, s, ms):
            return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

        start_time = to_ms(*match.groups()[0:4])
        end_time = to_ms(*match.groups()[4:8])
        text = " ".join(lines[2:]).strip()
        if text:
            utterances.append({"start_time": start_time, "end_time": end_time, "text": text})

    return utterances


def ms_to_srt_time(ms):
    seconds_total = ms // 1000
    milliseconds = ms % 1000
    hours = seconds_total // 3600
    minutes = (seconds_total % 3600) // 60
    seconds = seconds_total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def utterances_to_srt(utterances, text_key="translation_text"):
    srt = ""
    for i, u in enumerate(utterances):
        srt += f"{i + 1}\n"
        srt += f"{ms_to_srt_time(u.get('start_time', 0))} --> {ms_to_srt_time(u.get('end_time', 0))}\n"
        srt += f"{u.get(text_key, u.get('text', ''))}\n\n"
    return srt


def translate_sync_body(utterances, target_language, source_language="UNSPECIFIED"):
    body = {
        "bind_id": str(uuid.uuid4()).upper(),
        "enter_from": "asr",
        "tasks": [
            {
                "payload": {
                    "source_language": source_language,
                    "target_languages": [target_language],
                    "utterances": utterances,
                },
                "req_key": "cc_audio_subtitle_translate"
            }
        ],
    }
    return body


def build_request(args):
    device = deepcopy(DEFAULT_DEVICE)
    device.update(load_json(args.device_json, {}))

    if args.srt_file:
        utterances = parse_srt(args.srt_file)
    elif args.utterances_file:
        utterances = load_json(args.utterances_file)
        if isinstance(utterances, dict) and "utterances" in utterances:
            utterances = utterances["utterances"]
    else:
        raise SystemExit("need --srt-file or --utterances-file")

    body = translate_sync_body(
        utterances,
        args.target_language,
        args.source_language
    )
    
    path = "/lv/v1/common_task/sync"
    query = common_query(device, None, include_region=False)
    
    body_text = compact_json(body)
    url = BASE + path + "?" + urlencode(query)
    headers = base_headers(device, body_text, appid=True)
    
    lower_headers = {k.lower(): v for k, v in headers.items()}
    if "sign" not in lower_headers:
        headers["sign"] = make_sign_header(url, device["appvr"], lower_headers["device-time"], device["tdid"])
        
    return url, headers, body_text


def main():
    ap = argparse.ArgumentParser(description="Call CapCut Translate Sync API")
    ap.add_argument("--device-json", help="override device/query values")
    ap.add_argument("--dry-run", action="store_true", help="print request only")
    ap.add_argument("--out", help="write response JSON")
    ap.add_argument("--out-srt", help="write response translation to SRT file")

    ap.add_argument("--srt-file", help="SRT file to parse and translate")
    ap.add_argument("--utterances-file", help="JSON file containing utterances list for translate-sync")
    ap.add_argument("--source-language", default="UNSPECIFIED")
    ap.add_argument("--target-language", default="vi-VN")

    args = ap.parse_args()

    url, headers, body_text = build_request(args)
    req_dump = {"url": url, "headers": headers, "body": json.loads(body_text)}
    
    if args.dry_run:
        print(json.dumps(req_dump, ensure_ascii=False, indent=2))
        return

    if requests is None:
        raise SystemExit("pip install requests")

    resp = requests.post(url, headers=headers, data=body_text.encode("utf-8"), timeout=60)
    print(f"Status Code: {resp.status_code}")
    try:
        data = resp.json()
        try:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except UnicodeEncodeError:
            print(json.dumps(data, ensure_ascii=True, indent=2))
        if args.out:
            save_json(data, args.out)

        if args.out_srt:
            try:
                payload_str = data.get("data", {}).get("tasks", [{}])[0].get("payload", "{}")
                payload = json.loads(payload_str)
                lang_data = payload.get("translation", {}).get(args.target_language, [])
                if lang_data:
                    srt_content = utterances_to_srt(lang_data)
                    with open(args.out_srt, "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"Saved translated SRT to: {args.out_srt}")
                else:
                    print("No translation data found in payload for the target language.")
            except Exception as e:
                print(f"Failed to generate SRT: {e}")

    except Exception:
        try:
            print(resp.text)
        except UnicodeEncodeError:
            print(resp.text.encode('utf-8', 'replace').decode('cp1252', 'ignore'))


if __name__ == "__main__":
    main()
