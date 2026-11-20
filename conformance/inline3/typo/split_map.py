#!/usr/bin/env python3
"""Split probe-map.json into small capture chunks so a transient GET failure
loses at most one chunk instead of the whole capture set."""
import json, os
m = json.load(open('probe-map.json'))
items = list(m.items())
size = 10
for n in range(0, len(items), size):
    part = dict(items[n:n + size])
    name = f'capture-map-{n//size+1:02d}.json'
    with open(name, 'w') as fh:
        json.dump(part, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(name, len(part))
