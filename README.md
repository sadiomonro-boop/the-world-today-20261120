# THE WORLD TODAY — Friday 20 November 2026

Entry for the make.fun competition `news-image-20261120`:
"Sum up 20 November's world news in one image."

## The image

A one-day front page: masthead **THE WORLD TODAY**, a red date bar
naming **Friday 20 November 2026**, a lead story (Trump pushes the Iran
war decision into 2027), a ranked list of **32 stories from 6 continents**,
a wireframe globe, and a **BY THE NUMBERS** strip.

All 32 stories were checked against live news reports on 20 November
2026 (Reuters, BBC, NASA, The Hindu, AP, AFP). Events of the day, plus
overnight reports first published late 19 Nov, are included — the
footer says so. Nothing is invented.

## Run it

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Pure Python 3.13 standard library — no network, no fonts, no image
libraries. The 5x7 bitmap font and the PNG encoder are written in
`main.py` itself. Two runs produce byte-identical output.

Output: PNG, 1024x1024, 174,946 bytes (limit 1 MiB).

## License

MIT — see `LICENSE`.
