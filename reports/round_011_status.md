# Round 011 Status: Historical Controls and Primary Harvest Gate

## What Completed
- Selected **100** target weak/no-binding controls from existing 1946-1987 Taiwan-context attestations.
- Built target-dish analysis overlay with **213** rows: 113 target-positive rows plus 100 selected controls.
- Balanced target binding bins are now usable for both Taiwan-side and all-corridor views: **9/9 bins**.
- Generic marker-absence negative extraction remains thin: **38** candidates, all taiwan-only under the older definition.

## Control Quality Gate
- Record quality grade: **B**.
- Duplicate artifact groups: **0**.
- Suspicious split groups: **0**.
- Invalid years: **0**.
- Controls by authority: `{'secondary': 50, 'primary': 35, 'tertiary': 12, 'unknown': 3}`.
- Controls by corridor: `{'Taiwan-side': 30, 'Japan': 22, 'North America': 16, 'Singapore': 16, 'unknown': 12, 'Mainland China': 4}`.

## Primary Harvest Attempt
- Accepted new primary records this round: **0**.
- Culture Memory smoke harvest attempted 4 keyword/page searches and logged **4** DNS failures in `logs/round_011_culture_memory_failure_log.csv`.
- NewspaperSG direct URL smoke validation checked 5 known direct URLs and returned **0 OK**; the batch is marked critical because the current environment cannot resolve/fetch those URLs.
- These failures are recorded as execution failures, not progress.

## Current Writing Readiness
- Status: **keep_collecting**.
- Taiwan-side records needed for the old threshold: **206**.
- Current Taiwan-side primary count in readiness assessor: **4**.
- Tourism/retrospective ratio: **38.2%**.
- Current target-trend diagnosis still estimates **219** additional effective records before strong historical-trend writing.
- Overall credibility: **70.81%**.
- Transparency score: **72.77/100**.

## Next Action
Do not count search-plan volume as progress. The next useful step is to run primary harvesting from a network context that can resolve Culture Memory / NewspaperSG / NDL, then accept only rows with real source refs and provenance. The analytical control layer can already be used to test target-dish trends, but it does not replace the missing Taiwan-side primary corpus.
