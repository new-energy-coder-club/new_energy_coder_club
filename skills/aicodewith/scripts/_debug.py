import re

f = open('C:/Users/29711/.qclaw/openclaw.json', 'rb')
raw = f.read()
f.close()
if raw[:3] == b'\xef\xbb\xbf':
    raw = raw[3:]

# Decode as latin-1 to preserve all bytes losslessly
text = raw.decode('latin-1')
lines = text.split('\n')

print(f'Total lines: {len(lines)}')

# Find agent name lines (lines where "name" value has no closing quote or has garbled bytes)
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('"name"'):
        print(f'Line {i+1}: {repr(stripped[:80])}')

# Check lines around agent-859465ad
for i, line in enumerate(lines):
    if 'agent-859465ad' in line or 'agent-7cbcf336' in line:
        print(f'=== Found at line {i+1}')
        for j in range(i, min(i+6, len(lines))):
            print(f'  {j+1}: {repr(lines[j].strip()[:80])}')
