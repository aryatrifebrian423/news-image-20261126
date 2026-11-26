# 26 November 2026: 50 stories, a Gulf in flames cover

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/aryatrifebrian423/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/aryatrifebrian423/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image summing up Thursday 26 November 2026 in world news: 50
verified stories across the Middle East, Asia, the Americas, Europe,
Africa and Oceania, plus sport. The cover carries the day's biggest
story — Houthi strikes on Saudi Arabia's Ras Tanura refinery, two
tankers hitting mines in the Strait of Hormuz, and Brent crude past
$93 — and the numbers strip carries the day's biggest figures: 31
dead in the Cairo tanker fire, 19 dead in Sudan, a 204 off 53 balls
for 15-year-old Vaibhav Sooryavanshi, 1,220 players in for the IPL
2027 auction.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no numpy,
no network. It draws the poster with an embedded 5×7 bitmap font and
a hand-built PNG encoder (`zlib` + `struct`), and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`).
Output is fully deterministic: two runs write byte-identical files.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Verification

Every story is sourced in `SOURCES.md`, with the method and the
wrong-day items that were dropped. The image is 1024×1024 and under
1 MiB.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x9vj0gh6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
