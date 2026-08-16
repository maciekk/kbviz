# kbviz

Very small Python tool for visualizing QMK keyboard layers as SVGs.

It is aimed at personal layout documentation/review, with an emphasis on answering:

> What changed on this layer?

Current scope:

- ErgoDox EZ via `LAYOUT_ergodox_pretty`
- Moonlander via `LAYOUT_moonlander`
- one SVG per layer
- inherited keys shown in light gray
- overridden keys highlighted and labeled

This is intentionally **not** a framework.

## Quick start

Render the included ErgoDox input directory:

```bash
python3 kbviz.py inputs/ergodox -o out-ergo
```

Render the included Moonlander input directory:

```bash
python3 kbviz.py inputs/moonlander -o out-moon
```

Then view the results on macOS:

```bash
./view-svgs.sh out-ergo
./view-svgs.sh out-moon
```

## Example output

Base layer (full map):

![ErgoDox QWERTY layer](images/ergodox-qwerty.png)

Partial override layer:

![ErgoDox NUM layer](images/ergodox-num.png)

## Internal model

The script does not render directly from raw `keymap.c` text.

It does this instead:

1. parse `keymap.c`
2. build a tiny in-memory model: `Layer(name, keys)`
3. render that model to SVG using hard-coded keyboard geometry

For inheritance, a key is treated as:

- **overridden** if the layer entry is not transparent
- **inherited** if the layer entry is transparent

Inherited keys are drawn in light gray and left unlabeled.
Overridden keys are highlighted and labeled.

## Usage

Bare `keymap.c`:

```bash
python3 kbviz.py path/to/keymap.c -o out
```

Directory mode (`keymap.c` plus optional `layer-names.txt` / `layer_names.json`):

```bash
python3 kbviz.py path/to/layout-dir -o out
```

ZSA source zip:

```bash
python3 kbviz.py path/to/source.zip -o out
```

Example output files:

- with layer names: `out/00-QWERTY.svg`
- without layer names: `out/layer0.svg`

The repo includes two input directories ready to use:

- `inputs/ergodox/`
- `inputs/moonlander/`

## Label behavior

Examples:

- `KC_PGUP` -> `PgUp`
- `KC_HOME` -> `Home`
- `KC_LEFT` -> `←`
- `KC_F5` -> `F5`
- `KC_P7` / `KC_KP_7` -> `7` + `(KP)`
- `MO(3)` / `OSL(4)` / `TO(1)` / `LT(3, KC_TAB)` stay explicit

Unknown or custom expressions fall back to the original token.

Layer names can be provided in either:

- `layer-names.txt`
- `layer_names.json`

Example `layer-names.txt`:

```txt
0 QWERTY
1 Dvorak
2 Gaming
3 NUM
4 NAV
5 KBD
```

If no layer-name sidecar is found, titles stay as `Layer: N` and filenames fall back to `layerN.svg`.

## Notes

- Geometry is based on QMK layout data and is intended to be visually accurate.
- Readability is prioritized over exact board dimensions.
- The parser is intentionally narrow: it expects standard QMK layer entries like:
- Supported input forms are: directory, bare `keymap.c`, or ZSA source zip.

```c
[QWERTY] = LAYOUT_ergodox_pretty(...)
```

or:

```c
[0] = LAYOUT_moonlander(...)
```

## Viewing SVGs on macOS

Open one file:

```bash
open -a Safari out/00-QWERTY.svg
```

Open all generated SVGs with your macOS default browser:

```bash
./view-svgs.sh out
```

Choose a different app explicitly:

```bash
SVG_APP=Firefox ./view-svgs.sh out
```
