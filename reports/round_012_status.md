# Round 012 Status: Supervised Harvest Continuation

## Accepted Records
- Accepted new records: **4**.
- Accepted Taiwan-side primary records: **0**.
- Accepted regional primary records: **4** NewspaperSG records.
- Combined overlay rows: **1965**.

## Sources Added
- 1988 May Garden Taiwanese Restaurant — `https://eresources.nlb.gov.sg/newspapers/digitised/issue/straitstimes19880129-1`
- 1989 Taipei Umeko Sister Restaurant / May Garden Restaurant — `https://eresources.nlb.gov.sg/newspapers/digitised/issue/newpaper19891004-1`
- 1990 May Garden Restaurant — `https://eresources.nlb.gov.sg/newspapers/digitised/issue/newpaper19900912-1`
- 1992 May Garden Restaurant — `https://eresources.nlb.gov.sg/newspapers/digitised/issue/straitstimes19920209-1`

## Quality Gates
- Batch quality grade: **A**.
- Overlay quality grade: **B**.
- Overlay critical alerts: `{}`.
- Overlay warnings: `{'low_conf_probable_rows': 1}`.
- Batch provenance was written to `working/manual_harvest_primary_round_012_batch_001_with_provenance.csv`, `raw/manifests/raw_capture_manifest.jsonl`, and `logs/round_012_execution_log.csv`.

## Recomputed Assessment
- Writing status: **keep_collecting**.
- Taiwan-side records still needed: **206**.
- Taiwan-side primary count in readiness assessor: **4**.
- Tourism/retrospective ratio: **38.2%**.
- Credibility after strict reclassification: **64.87%**.
- Transparency score: **72.83/100**.
- Target controls selected after refresh: **100**.
- Target-trend estimated additional effective records needed: **220**.

## Why This Round Did Not Reach the Full Plan
The locally executed primary archive harvest is still blocked by DNS/access failures for Culture Memory and NewspaperSG direct URL fetches. I therefore accepted only records that could be verified through web-search-visible NewspaperSG snippets and were absent from the current overlay. Existing 1981-1985 May Garden / Taipei Umeko hits were skipped because they were already present.

## Next Required Move
The next productive run needs either a network context that can resolve primary archives, or manual browser-assisted extraction from NewspaperSG/NDL/Culture Memory. Continue to reject duplicate source/year/brand/type rows and do not count search tasks as records.
