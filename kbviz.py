#!/usr/bin/env python3
import argparse
import html
import json
import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple

KEY_W = 56
KEY_H = 56
GAP = 8
MARGIN = 24
FONT_SIZE = 15
TITLE_SIZE = 24
LAYER_NAMES_JSON = "layer_names.json"
LAYER_NAMES_TXT = "layer-names.txt"

TRANSPARENT_TOKENS = {"KC_TRNS", "KC_TRANSPARENT", "_______", "___", "TRNS"}
NO_TOKENS = {"KC_NO", "XXXXXXX", "XXX", "NO"}


@dataclass
class Layer:
    index: int
    name: str
    keys: List[str]


@dataclass
class Key:
    x: float
    y: float
    w: float = KEY_W
    h: float = KEY_H


@dataclass
class KeyboardSpec:
    name: str
    layout_macro: str
    key_count: int
    geometry_func: Callable[[int], List[Key]]


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)
    return text


def collect_defines(text: str) -> dict:
    defines = {}
    for line in text.splitlines():
        m = re.match(r"\s*#define\s+(\w+)\s+(.+?)\s*$", line)
        if m:
            defines[m.group(1)] = m.group(2).strip()
    return defines


def extract_balanced(text: str, open_paren_index: int) -> Tuple[str, int]:
    depth = 0
    for i in range(open_paren_index, len(text)):
        ch = text[i]
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return text[open_paren_index + 1 : i], i
    raise ValueError("Unbalanced parentheses while parsing layout macro")


def split_top_level_commas(text: str) -> List[str]:
    return [token for token, _, _ in split_top_level_commas_with_positions(text)]


def split_top_level_commas_with_positions(text: str) -> List[Tuple[str, int, int]]:
    parts: List[Tuple[str, int, int]] = []
    current = []
    paren = brace = bracket = 0
    line = 1
    col = 0
    token_line = None
    token_col = None

    def flush():
        nonlocal current, token_line, token_col
        part = ''.join(current).strip()
        if part and token_line is not None and token_col is not None:
            parts.append((normalize_ws(part), token_line, token_col))
        current = []
        token_line = None
        token_col = None

    for ch in text:
        if token_line is None and not ch.isspace():
            token_line = line
            token_col = col
        if ch == ',' and paren == brace == bracket == 0:
            flush()
            col += 1
            continue
        current.append(ch)
        if ch == '(':
            paren += 1
        elif ch == ')':
            paren -= 1
        elif ch == '{':
            brace += 1
        elif ch == '}':
            brace -= 1
        elif ch == '[':
            bracket += 1
        elif ch == ']':
            bracket -= 1
        if ch == '\n':
            line += 1
            col = 0
        else:
            col += 1
    flush()
    return parts


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def parse_layers(text: str, layout_macro: str) -> List[Layer]:
    stripped = strip_comments(text)
    layers = []
    pattern = re.compile(rf"\[\s*([^\]]+?)\s*\]\s*=\s*{re.escape(layout_macro)}\s*\(", re.S)
    for index, match in enumerate(pattern.finditer(stripped)):
        name = normalize_ws(match.group(1))
        body, _ = extract_balanced(stripped, match.end() - 1)
        keys = split_top_level_commas(body)
        layers.append(Layer(index=index, name=name, keys=keys))
    if not layers:
        raise ValueError(f"No [LAYER] = {layout_macro}(...) blocks found")
    key_count = len(layers[0].keys)
    for layer in layers:
        if len(layer.keys) != key_count:
            raise ValueError(f"Layer {layer.name} has {len(layer.keys)} keys, expected {key_count}")
    return layers


def resolve_alias(token: str, defines: dict) -> str:
    seen = set()
    value = token
    while value in defines and value not in seen:
        seen.add(value)
        candidate = normalize_ws(defines[value])
        if not candidate:
            break
        if re.search(r"[\s{};,]", candidate):
            break
        value = candidate
    return value


def is_transparent(token: str, defines: dict) -> bool:
    return resolve_alias(token, defines) in TRANSPARENT_TOKENS


def compact_label(token: str, defines: dict) -> str:
    raw = resolve_alias(token, defines)
    compact = {
        "KC_TAB": "↹",
        "KC_SPACE": "␠",
        "KC_SPC": "␠",
        "KC_ENTER": "↵",
        "KC_ENT": "↵",
        "KC_ESCAPE": "Esc",
        "KC_ESC": "Esc",
    }
    if raw in compact:
        return compact[raw]
    return human_label(token, defines).replace("\n", " ")


def classify_token(token: str, defines: dict) -> str:
    raw = resolve_alias(token, defines)
    if re.match(r"^(MO|OSL|TO|TG|DF|TT|LT)\(", token):
        return "layer"
    if raw in {
        "KC_LCTL", "KC_RCTL", "KC_LEFT_CTRL", "KC_RIGHT_CTRL",
        "KC_LSFT", "KC_RSFT", "KC_LEFT_SHIFT", "KC_RIGHT_SHIFT",
        "KC_LALT", "KC_RALT", "KC_LEFT_ALT", "KC_RIGHT_ALT",
        "KC_LGUI", "KC_RGUI", "KC_LEFT_GUI", "KC_RIGHT_GUI",
        "SC_LSPO", "SC_RSPC",
    }:
        return "modifier"
    if raw.startswith("RGB_") or raw.startswith("UG_") or raw in {"LED_LEVEL", "TOGGLE_LAYER_COLOR", "QK_BOOT", "QK_AUDIO_ON", "QK_AUDIO_OFF", "MU_TOGG", "CW_TOGG", "CW_TOGGLE"}:
        return "system"
    if raw.startswith("KC_MS_") or raw.startswith("MS_") or raw.startswith("KC_WWW_") or raw in {"KC_MY_COMPUTER", "KC_MPLY", "KC_MSTP", "KC_MPRV", "KC_MNXT", "KC_VOLU", "KC_VOLD", "KC_MUTE"}:
        return "media"
    return "default"


def key_colors(token: str, defines: dict, overridden: bool, colorful: bool) -> Tuple[str, str]:
    if not overridden:
        return "#f6f7f2", "#d7dbd0"
    if not colorful:
        return "#d9ffde", "#7fd98c"
    category = classify_token(token, defines)
    palette = {
        "default": ("#d9ffde", "#7fd98c"),
        "layer": ("#dff4ff", "#3f96cc"),
        "modifier": ("#f8eeff", "#a14fc4"),
        "system": ("#ffdfe5", "#cf5f7b"),
        "media": ("#fff5d8", "#d8c17a"),
    }
    return palette.get(category, palette["default"])


def human_label(token: str, defines: dict) -> str:
    raw = resolve_alias(token, defines)
    if raw in TRANSPARENT_TOKENS:
        return ""
    if raw in NO_TOKENS:
        return "No"
    if m := re.match(r"^LT\(([^,]+),\s*(.+)\)$", token):
        return f"LT({m.group(1)},\n{human_label(m.group(2), defines)})"
    if re.match(r"^(MO|OSL|TO|TG|DF|TT|LT)\(", token):
        return token
    if m := re.match(r"^TD\(DANCE_(\d+)\)$", token):
        return f"TD{m.group(1)}"

    exact = {
        "KC_ESC": "Esc",
        "KC_ESCAPE": "Esc",
        "KC_TAB": "Tab",
        "KC_CAPS": "Caps",
        "KC_BSPC": "Bksp",
        "KC_BSPACE": "Bksp",
        "KC_DEL": "Del",
        "KC_DELETE": "Del",
        "KC_INS": "Ins",
        "KC_INSERT": "Ins",
        "KC_ENT": "Enter",
        "KC_ENTER": "Enter",
        "KC_SPC": "Space",
        "KC_SPACE": "Space",
        "KC_HOME": "Home",
        "KC_END": "End",
        "KC_PGUP": "PgUp",
        "KC_PAGE_UP": "PgUp",
        "KC_PGDN": "PgDn",
        "KC_PAGE_DOWN": "PgDn",
        "KC_LEFT": "←",
        "KC_RIGHT": "→",
        "KC_UP": "↑",
        "KC_DOWN": "↓",
        "KC_GRAVE": "`",
        "KC_GRV": "`",
        "KC_MINUS": "-",
        "KC_MINS": "-",
        "KC_EQUAL": "=",
        "KC_EQL": "=",
        "KC_LBRC": "[",
        "KC_RBRC": "]",
        "KC_BSLS": "\\",
        "KC_SCLN": ";",
        "KC_QUOTE": "'",
        "KC_QUOT": "'",
        "KC_COMMA": ",",
        "KC_COMM": ",",
        "KC_DOT": ".",
        "KC_SLASH": "/",
        "KC_SLSH": "/",
        "KC_TILD": "~",
        "KC_EXLM": "!",
        "KC_AT": "@",
        "KC_HASH": "#",
        "KC_DLR": "$",
        "KC_PERC": "%",
        "KC_CIRC": "^",
        "KC_AMPR": "&",
        "KC_ASTR": "*",
        "KC_LPRN": "(",
        "KC_RPRN": ")",
        "KC_UNDS": "_",
        "KC_PLUS": "+",
        "KC_LCBR": "{",
        "KC_RCBR": "}",
        "KC_PIPE": "|",
        "KC_COLN": ":",
        "KC_DQUO": '"',
        "KC_LT": "<",
        "KC_GT": ">",
        "KC_QUES": "?",
        "SC_LSPO": "Shift\n(cadet)",
        "SC_RSPC": "Shift\n(cadet)",
        "KC_APP": "App",
        "KC_PSCR": "PrtSc",
        "KC_SLCK": "ScrLk",
        "KC_PAUS": "Pause",
        "KC_PAUSE": "Pause",
        "KC_NLCK": "NumLk",
        "KC_NUM": "Num",
        "KC_KP_PLUS": "+\n(KP)",
        "KC_KP_MINUS": "-\n(KP)",
        "KC_KP_ASTERISK": "*\n(KP)",
        "KC_KP_SLASH": "/\n(KP)",
        "KC_KP_DOT": ".\n(KP)",
        "KC_KP_ENTER": "Enter\n(KP)",
        "KC_WWW_BACK": "Back",
        "KC_WWW_FORWARD": "Fwd",
        "KC_WWW_HOME": "Web",
        "KC_WWW_SEARCH": "Search",
        "KC_MY_COMPUTER": "PC",
        "CW_TOGG": "Caps\nWord",
        "CW_TOGGLE": "Caps\nWord",
        "QK_AUDIO_ON": "Audio\nOn",
        "QK_AUDIO_OFF": "Audio\nOff",
        "MU_TOGG": "Music",
        "QK_BOOT": "Reset",
        "KC_MS_UP": "M↑",
        "KC_MS_DOWN": "M↓",
        "KC_MS_LEFT": "M←",
        "KC_MS_RIGHT": "M→",
        "KC_MS_BTN1": "M1",
        "KC_MS_BTN2": "M2",
        "MS_UP": "M↑",
        "MS_DOWN": "M↓",
        "MS_LEFT": "M←",
        "MS_RGHT": "M→",
        "MS_BTN1": "M1",
        "MS_BTN2": "M2",
        "KC_MPLY": "Play",
        "KC_MSTP": "Stop",
        "KC_MPRV": "Prev",
        "KC_MNXT": "Next",
        "KC_VOLU": "Vol+",
        "KC_VOLD": "Vol-",
        "KC_MUTE": "Mute",
        "RGB_HUI": "H+",
        "RGB_HUD": "H-",
        "RGB_SAI": "S+",
        "RGB_SAD": "S-",
        "RGB_VAI": "V+",
        "RGB_VAD": "V-",
        "RGB_SPI": "Sp+",
        "RGB_SPD": "Sp-",
        "RGB_SLD": "Solid",
        "RGB_TOG": "RGB",
        "RGB_MODE_FORWARD": "Mode+",
        "UG_NEXT": "Anim",
        "UG_TOGG": "Glow",
        "UG_VALU": "B+",
        "UG_VALD": "B-",
        "UG_HUEU": "H+",
        "UG_HUED": "H-",
        "LED_LEVEL": "LED",
        "TOGGLE_LAYER_COLOR": "Layer\nLED",
        "EE_CLR": "Clear",
        "KC_LCTL": "LCtrl",
        "KC_RCTL": "RCtrl",
        "KC_LEFT_CTRL": "LCtrl",
        "KC_RIGHT_CTRL": "RCtrl",
        "KC_LSFT": "LShift",
        "KC_RSFT": "RShift",
        "KC_LEFT_SHIFT": "LShift",
        "KC_RIGHT_SHIFT": "RShift",
        "KC_LALT": "LAlt",
        "KC_RALT": "RAlt",
        "KC_LEFT_ALT": "LAlt",
        "KC_RIGHT_ALT": "RAlt",
        "KC_LGUI": "LGui",
        "KC_RGUI": "RGui",
        "KC_LEFT_GUI": "LGui",
        "KC_RIGHT_GUI": "RGui",
    }
    if raw in exact:
        return exact[raw]
    if m := re.match(r"KC_F(\d+)$", raw):
        return f"F{m.group(1)}"
    if m := re.match(r"KC_KP_(\d+)$", raw):
        return f"{m.group(1)}\n(KP)"
    if m := re.match(r"KC_P(\d+)$", raw):
        return f"{m.group(1)}\n(KP)"
    if m := re.match(r"KC_(\d)$", raw):
        return m.group(1)
    if m := re.match(r"KC_([A-Z])$", raw):
        return m.group(1)
    if raw.startswith("HSV_"):
        return "HSV"
    if raw.startswith("KC_"):
        return raw[3:].title()
    return raw


def geometry_from_layout(layout: List[Tuple[float, float, float, float]], key_count: int, expected: int, keyboard_name: str, layout_macro: str) -> List[Key]:
    if key_count != expected:
        raise ValueError(f"Expected {expected} keys for {keyboard_name} / {layout_macro}, found {key_count}")

    pitch = KEY_W + GAP
    keys = []
    for x, y, w, h in layout:
        px = MARGIN + x * pitch
        py = MARGIN + 28 + y * pitch
        pw = w * KEY_W + (w - 1) * GAP
        ph = h * KEY_H + (h - 1) * GAP
        keys.append(Key(x=px, y=py, w=pw, h=ph))
    return keys


def ergodox_geometry(key_count: int) -> List[Key]:
    # Exact LAYOUT_ergodox_pretty positions from QMK keyboards/ergodox_ez/info.json.
    layout = [
        (0, 0.375, 1.5, 1), (1.5, 0.375, 1, 1), (2.5, 0.125, 1, 1), (3.5, 0, 1, 1), (4.5, 0.125, 1, 1), (5.5, 0.25, 1, 1), (6.5, 0.25, 1, 1),
        (9.5, 0.25, 1, 1), (10.5, 0.25, 1, 1), (11.5, 0.125, 1, 1), (12.5, 0, 1, 1), (13.5, 0.125, 1, 1), (14.5, 0.375, 1, 1), (15.5, 0.375, 1.5, 1),
        (0, 1.375, 1.5, 1), (1.5, 1.375, 1, 1), (2.5, 1.125, 1, 1), (3.5, 1, 1, 1), (4.5, 1.125, 1, 1), (5.5, 1.25, 1, 1), (6.5, 1.25, 1, 1.5),
        (9.5, 1.25, 1, 1.5), (10.5, 1.25, 1, 1), (11.5, 1.125, 1, 1), (12.5, 1, 1, 1), (13.5, 1.125, 1, 1), (14.5, 1.375, 1, 1), (15.5, 1.375, 1.5, 1),
        (0, 2.375, 1.5, 1), (1.5, 2.375, 1, 1), (2.5, 2.125, 1, 1), (3.5, 2, 1, 1), (4.5, 2.125, 1, 1), (5.5, 2.25, 1, 1),
        (10.5, 2.25, 1, 1), (11.5, 2.125, 1, 1), (12.5, 2, 1, 1), (13.5, 2.125, 1, 1), (14.5, 2.375, 1, 1), (15.5, 2.375, 1.5, 1),
        (0, 3.375, 1.5, 1), (1.5, 3.375, 1, 1), (2.5, 3.125, 1, 1), (3.5, 3, 1, 1), (4.5, 3.125, 1, 1), (5.5, 3.25, 1, 1), (6.5, 2.75, 1, 1.5),
        (9.5, 2.75, 1, 1.5), (10.5, 3.25, 1, 1), (11.5, 3.125, 1, 1), (12.5, 3, 1, 1), (13.5, 3.125, 1, 1), (14.5, 3.375, 1, 1), (15.5, 3.375, 1.5, 1),
        (0.5, 4.375, 1, 1), (1.5, 4.375, 1, 1), (2.5, 4.125, 1, 1), (3.5, 4, 1, 1), (4.5, 4.125, 1, 1),
        (11.5, 4.125, 1, 1), (12.5, 4, 1, 1), (13.5, 4.125, 1, 1), (14.5, 4.375, 1, 1), (15.5, 4.375, 1, 1),
        (6, 5, 1, 1), (7, 5, 1, 1), (9, 5, 1, 1), (10, 5, 1, 1),
        (7, 6, 1, 1), (9, 6, 1, 1),
        (5, 6, 1, 2), (6, 6, 1, 2), (7, 7, 1, 1), (9, 7, 1, 1), (10, 6, 1, 2), (11, 6, 1, 2),
    ]

    return geometry_from_layout(layout, key_count, 76, "ErgoDox EZ", "LAYOUT_ergodox_pretty")


def moonlander_geometry(key_count: int) -> List[Key]:
    # Exact positions from QMK keyboards/zsa/moonlander/keyboard.json (LAYOUT alias used by LAYOUT_moonlander).
    layout = [
        (0, 0.375, 1, 1), (1, 0.375, 1, 1), (2, 0.125, 1, 1), (3, 0, 1, 1), (4, 0.125, 1, 1), (5, 0.25, 1, 1), (6, 0.25, 1, 1),
        (10, 0.25, 1, 1), (11, 0.25, 1, 1), (12, 0.125, 1, 1), (13, 0, 1, 1), (14, 0.125, 1, 1), (15, 0.375, 1, 1), (16, 0.375, 1, 1),
        (0, 1.375, 1, 1), (1, 1.375, 1, 1), (2, 1.125, 1, 1), (3, 1, 1, 1), (4, 1.125, 1, 1), (5, 1.25, 1, 1), (6, 1.25, 1, 1),
        (10, 1.25, 1, 1), (11, 1.25, 1, 1), (12, 1.125, 1, 1), (13, 1, 1, 1), (14, 1.125, 1, 1), (15, 1.375, 1, 1), (16, 1.375, 1, 1),
        (0, 2.375, 1, 1), (1, 2.375, 1, 1), (2, 2.125, 1, 1), (3, 2, 1, 1), (4, 2.125, 1, 1), (5, 2.25, 1, 1), (6, 2.25, 1, 1),
        (10, 2.25, 1, 1), (11, 2.25, 1, 1), (12, 2.125, 1, 1), (13, 2, 1, 1), (14, 2.125, 1, 1), (15, 2.375, 1, 1), (16, 2.375, 1, 1),
        (0, 3.375, 1, 1), (1, 3.375, 1, 1), (2, 3.125, 1, 1), (3, 3, 1, 1), (4, 3.125, 1, 1), (5, 3.25, 1, 1),
        (11, 3.25, 1, 1), (12, 3.125, 1, 1), (13, 3, 1, 1), (14, 3.125, 1, 1), (15, 3.375, 1, 1), (16, 3.375, 1, 1),
        (0, 4.375, 1, 1), (1, 4.375, 1, 1), (2, 4.125, 1, 1), (3, 4, 1, 1), (4, 4.125, 1, 1), (5, 4.5, 2, 1),
        (10, 4.5, 2, 1), (12, 4.125, 1, 1), (13, 4, 1, 1), (14, 4.125, 1, 1), (15, 4.375, 1, 1), (16, 4.375, 1, 1),
        (5, 5.5, 1, 1.5), (6, 5.5, 1, 1.5), (7, 5.5, 1, 1.5), (9, 5.5, 1, 1.5), (10, 5.5, 1, 1.5), (11, 5.5, 1, 1.5),
    ]
    return geometry_from_layout(layout, key_count, 72, "Moonlander", "LAYOUT_moonlander")


KEYBOARD_SPECS = [
    KeyboardSpec(name="ErgoDox EZ", layout_macro="LAYOUT_ergodox_pretty", key_count=76, geometry_func=ergodox_geometry),
    KeyboardSpec(name="Moonlander", layout_macro="LAYOUT_moonlander", key_count=72, geometry_func=moonlander_geometry),
]


def detect_keyboard(text: str) -> KeyboardSpec:
    stripped = strip_comments(text)
    for spec in KEYBOARD_SPECS:
        if re.search(rf"\b{re.escape(spec.layout_macro)}\s*\(", stripped):
            return spec
    supported = ", ".join(spec.layout_macro for spec in KEYBOARD_SPECS)
    raise ValueError(f"No supported layout macro found. Supported: {supported}")


def wrap_text(text: str, width: int = 8) -> List[str]:
    if "\n" in text:
        return text.split("\n")[:3]
    if len(text) <= width:
        return [text]
    chunks = re.split(r"([_(), ])", text)
    lines = []
    current = ""
    for chunk in chunks:
        if not chunk:
            continue
        if len(current) + len(chunk) <= width or not current:
            current += chunk
        else:
            lines.append(current.strip())
            current = chunk
    if current.strip():
        lines.append(current.strip())
    if len(lines) == 1 and len(lines[0]) > width:
        lines = [text[:width], text[width:]]
    return lines[:3]


def label_font_size(lines: List[str]) -> int:
    longest = max((len(line) for line in lines), default=0)
    if len(lines) >= 3 or longest >= 12:
        return 11
    if longest >= 10:
        return 13
    return FONT_SIZE


def legend_entries_for_layer(layer: Layer, defines: dict) -> List[Tuple[str, str]]:
    entries = []
    seen = set()
    for token in layer.keys:
        if is_transparent(token, defines):
            continue
        item = None
        if re.match(r"^MO\((.+)\)$", token):
            item = ("MO(n)", "momentarily activate layer n while held")
        elif re.match(r"^OSL\((.+)\)$", token):
            item = ("OSL(n)", "activate layer n for one key")
        elif re.match(r"^TO\((.+)\)$", token):
            item = ("TO(n)", "switch default layer to n")
        elif re.match(r"^LT\((.+)\)$", token):
            item = ("LT(layer, key)", "hold for layer, tap for key")
        elif m := re.match(r"^TD\(DANCE_(\d+)\)$", token):
            item = (f"TD{m.group(1)}", f"tap dance {m.group(1)}")
        elif token in {"CW_TOGG", "CW_TOGGLE"}:
            item = ("Caps Word", "toggle Caps Word mode")
        elif token == "QK_BOOT":
            item = ("Reset", "jump to bootloader for firmware flashing")
        elif token in {"QK_AUDIO_ON", "QK_AUDIO_OFF"}:
            item = ("Audio On/Off", "enable or disable QMK keyclick audio")
        elif token == "MU_TOGG":
            item = ("Music", "toggle QMK music mode")
        if item and item[0] not in seen:
            seen.add(item[0])
            entries.append(item)
    return entries


def svg_for_layer(layer: Layer, keys: List[Key], defines: dict, legend: List[Tuple[str, str]], layer_names: dict, colorful: bool) -> str:
    legend_h = 0 if not legend else 34 + len(legend) * 18
    width = int(max(k.x + k.w for k in keys) + MARGIN)
    height = int(max(k.y + k.h for k in keys) + MARGIN + 30 + legend_h)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{MARGIN}" y="28" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{TITLE_SIZE}" font-weight="700" fill="#222">{html.escape(layer_title(layer, layer_names))}</text>',
    ]

    for key, token in zip(keys, layer.keys):
        overridden = not is_transparent(token, defines)
        fill, stroke = key_colors(token, defines, overridden, colorful)
        parts.append(
            f'<rect x="{key.x:.1f}" y="{key.y:.1f}" width="{key.w}" height="{key.h}" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
        )
        if overridden:
            label = human_label(token, defines)
            lines = wrap_text(label, width=8)
            base_font_size = label_font_size(lines)
            line_sizes = [max(10, base_font_size - 3) if i > 0 and line.startswith("(") and line.endswith(")") else base_font_size for i, line in enumerate(lines)]
            if len(lines) == 1:
                y = key.y + key.h / 2 + line_sizes[0] * 0.35
                parts.append(
                    f'<text x="{key.x + key.w / 2:.1f}" y="{y:.1f}" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{line_sizes[0]}" font-weight="600" fill="#666">{html.escape(lines[0])}</text>'
                )
            else:
                gap = 2
                total_h = sum(line_sizes) + gap * (len(lines) - 1)
                top = key.y + key.h / 2 - total_h / 2
                current_top = top
                for i, line in enumerate(lines):
                    y = current_top + line_sizes[i] * 0.8
                    parts.append(
                        f'<text x="{key.x + key.w / 2:.1f}" y="{y:.1f}" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{line_sizes[i]}" font-weight="600" fill="#666">{html.escape(line)}</text>'
                    )
                    current_top += line_sizes[i] + gap

    if legend:
        top = max(k.y + k.h for k in keys) + 22
        parts.append(f'<text x="{MARGIN}" y="{top}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="16" font-weight="700" fill="#222">Legend</text>')
        y = top + 20
        for short, desc in legend:
            parts.append(f'<text x="{MARGIN}" y="{y}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" fill="#222">{html.escape(short)}</text>')
            parts.append(f'<text x="{MARGIN + 110}" y="{y}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="13" fill="#444">{html.escape(desc)}</text>')
            y += 18
    parts.append('</svg>')
    return '\n'.join(parts)


def safe_name(name: str) -> str:
    cleaned = name.strip().strip('"').strip("'")
    cleaned = re.sub(r"^_+", "", cleaned)
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", cleaned)
    cleaned = cleaned.strip('-') or 'layer'
    return cleaned


def parse_layer_names_txt(text: str) -> dict:
    names = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
        else:
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            key, value = parts
        names[key.strip()] = value.strip()
    return names


def load_layer_names_from_text(text: str, suffix: str) -> dict:
    if suffix == ".json":
        return json.loads(text)
    return parse_layer_names_txt(text)


def load_layer_names(path: Path) -> dict:
    candidates = [
        path.parent / LAYER_NAMES_TXT,
        path.parent / LAYER_NAMES_JSON,
    ]
    for candidate in candidates:
        if candidate.exists():
            return load_layer_names_from_text(candidate.read_text(encoding="utf-8"), candidate.suffix.lower())
    return {}


def load_keymap_and_layer_names(path: Path) -> Tuple[str, dict]:
    if path.is_dir():
        keymap = path / "keymap.c"
        if not keymap.exists():
            raise ValueError(f"No keymap.c found in directory {path}")
        layer_names = {}
        for name in (LAYER_NAMES_TXT, LAYER_NAMES_JSON):
            sidecar = path / name
            if sidecar.exists():
                layer_names = load_layer_names_from_text(sidecar.read_text(encoding="utf-8"), sidecar.suffix.lower())
                break
        return keymap.read_text(encoding="utf-8"), layer_names

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            keymaps = [name for name in names if name.endswith("/keymap.c") or name == "keymap.c"]
            if not keymaps:
                raise ValueError(f"No keymap.c found inside {path}")
            keymap_text = zf.read(keymaps[0]).decode("utf-8")
            layer_names = {}
            for target in (LAYER_NAMES_TXT, LAYER_NAMES_JSON):
                matches = [name for name in names if name.endswith("/" + target) or name == target]
                if matches:
                    layer_names = load_layer_names_from_text(zf.read(matches[0]).decode("utf-8"), Path(target).suffix.lower())
                    break
            return keymap_text, layer_names

    return path.read_text(encoding="utf-8"), load_layer_names(path)


def layer_friendly_name(layer: Layer, layer_names: dict) -> str | None:
    return layer_names.get(layer.name) or layer_names.get(str(layer.index))


def layer_title(layer: Layer, layer_names: dict) -> str:
    friendly = layer_friendly_name(layer, layer_names)
    if friendly:
        return f"Layer: {layer.name} — {friendly}"
    return f"Layer: {layer.name}"


def output_layer_filename(layer: Layer, layer_names: dict) -> str:
    friendly = layer_friendly_name(layer, layer_names)
    if friendly:
        return f"{layer.index:02d}-{safe_name(friendly)}.svg"
    return f"layer{layer.index}.svg"


def export_png(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        [
            "inkscape",
            str(svg_path),
            "--export-type=png",
            f"--export-filename={png_path}",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate layer images from a QMK keymap (ErgoDox EZ or Moonlander)")
    parser.add_argument("keymap", help="Path to keymap.c, layout directory, or source zip")
    parser.add_argument("-o", "--out", default="out", help="Output directory (default: out)")
    parser.add_argument("--svg", action="store_true", help="Output SVG files")
    parser.add_argument("--png", action="store_true", help="Output PNG files")
    parser.add_argument("--colorful", action="store_true", help="Use subtle category colors for overridden keys")
    args = parser.parse_args()

    want_svg = args.svg or not args.png
    want_png = args.png

    keymap_path = Path(args.keymap)
    out_dir = Path(args.out)
    text, layer_names = load_keymap_and_layer_names(keymap_path)
    spec = detect_keyboard(text)
    defines = collect_defines(text)
    layers = parse_layers(text, spec.layout_macro)
    geometry = spec.geometry_func(len(layers[0].keys))

    out_dir.mkdir(parents=True, exist_ok=True)
    for layer in layers:
        legend = legend_entries_for_layer(layer, defines)
        svg = svg_for_layer(layer, geometry, defines, legend, layer_names, args.colorful)
        stem = Path(output_layer_filename(layer, layer_names)).stem
        svg_path = out_dir / f"{stem}.svg"
        png_path = out_dir / f"{stem}.png"
        if want_svg or want_png:
            svg_path.write_text(svg, encoding="utf-8")
        if want_png:
            export_png(svg_path, png_path)
        if want_svg:
            print(svg_path)
        if want_png:
            print(png_path)
        if want_png and not want_svg and svg_path.exists():
            svg_path.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
