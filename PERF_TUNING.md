# Performance tuning (Windows-friendly)

This app can trade **startup time**, **RAM**, and **runtime smoothness**. Use these environment variables to balance.

## Logging
- **`MEDICAL_PERF=1`**: print `[PERF] ...` timing logs.

## Startup behavior
- **`MEDICAL_PRELOAD_SCREENS=1`**: preload all screens at startup (slower startup, smoother runtime).
  - Default: off.
- **`MEDICAL_WARMUP=1`**: call optional `warmup()` hooks during preload.
  - Default: off.

## PDF preview cache
- **`MEDICAL_CACHE_PDF_PAGES=8`**: max cached rendered PDF pages (LRU). Set `0` to disable caching.
  - Default: `8`
- **`MEDICAL_PDF_WARM_NEXT=1`**: warm up (render) the next page after rendering the current page.
  - Default: off

## Test sequence cache
- **`MEDICAL_CACHE_SEQ_FRAMES=128`**: max cached sequence frames (LRU). Set `0` to disable caching.
  - Default: `128`

## Suggested balanced settings (recommended)

```bash
MEDICAL_PERF=1 \
MEDICAL_PRELOAD_SCREENS=0 \
MEDICAL_WARMUP=0 \
MEDICAL_CACHE_PDF_PAGES=8 \
MEDICAL_PDF_WARM_NEXT=0 \
MEDICAL_CACHE_SEQ_FRAMES=128 \
python app.py
```

