#!/usr/bin/env python3
"""Merge per-chunk capture outputs into captures.json. Each chunk file holds
id -> live capture records; accept a record only when both anonymous fetches
were stable and the saved source matched byte for byte."""
import glob, json
merged, accepted, rejected = {}, [], []
for path in sorted(glob.glob('capture-out-*.json')):
    data = json.load(open(path, encoding='utf-8'))
    for cid, rec in data.items():
        if 'html' in rec and rec.get('valid') and rec.get('stable') and rec.get('saved_source_matches'):
            merged[cid] = rec
            accepted.append(cid)
        else:
            rejected.append((cid, path, rec.get('valid'), rec.get('stable'),
                             rec.get('saved_source_matches')))
with open('captures.json', 'w', encoding='utf-8') as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print('merged valid stable source-matched records:', len(accepted))
print('rejected:', rejected)
