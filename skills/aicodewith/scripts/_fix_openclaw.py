"""
Line-by-line fix for openclaw.json broken agent name strings.
Handles the case where QClaw/encoding corruption caused "name" values
to lose their closing quote.
"""
import re

OPENCLAW = 'C:/Users/29711/.qclaw/openclaw.json'

# Known agent names (id -> correct UTF-8 name)
AGENT_NAMES = {
    'agent-7cbcf336': 'Ielts助理',
    'agent-859465ad': '林且慢',
}

f = open(OPENCLAW, 'rb')
raw = f.read()
f.close()
had_bom = raw[:3] == b'\xef\xbb\xbf'
if had_bom:
    raw = raw[3:]

# Split into lines (preserve \r\n)
sep = b'\r\n' if b'\r\n' in raw else b'\n'
lines = raw.split(sep)

fixed_lines = []
current_agent_id = None
i = 0
while i < len(lines):
    line = lines[i]
    line_str = line.decode('latin-1').strip()

    # Track current agent ID
    m = re.match(r'"id":\s*"(agent-[^"]+)"', line_str)
    if m:
        current_agent_id = m.group(1)

    # Detect broken "name" line: starts with "name": " but no closing ",
    if line_str.startswith('"name":') and current_agent_id in AGENT_NAMES:
        correct_name = AGENT_NAMES[current_agent_id].encode('utf-8')
        indent = b' ' * (len(line) - len(line.lstrip()))
        fixed_line = indent + b'"name": "' + correct_name + b'",'

        # Check if next line is also mangled (missing opening " due to regex eat)
        next_i = i + 1
        if next_i < len(lines):
            next_str = lines[next_i].decode('latin-1').strip()
            if next_str and not next_str.startswith('"') and not next_str.startswith('}'):
                # Next line missing opening quote - prepend it
                next_indent = b' ' * 8  # standard 8-space indent
                lines[next_i] = next_indent + b'"' + lines[next_i].lstrip()

        fixed_lines.append(fixed_line)
        i += 1
        continue

    fixed_lines.append(line)
    i += 1

result = sep.join(fixed_lines)

# Also strip any stray control chars
result = re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]', b'', result)

with open(OPENCLAW, 'wb') as fw:
    if had_bom:
        fw.write(b'\xef\xbb\xbf')
    fw.write(result)

print(f'Written {len(result)} bytes')

# Verify
import json
text = result.decode('utf-8')
cleaned = re.sub(r'^\s*\\"[^\n]+$', '  "__qclaw__": null,', text, flags=re.MULTILINE)
try:
    data = json.loads(cleaned)
    print('JSON valid!')
    agents = data['agents']['list']
    for a in agents:
        print(f"  agent {a.get('id','?')}: name={a.get('name','?')!r}")
    print('Providers:', list(data['models']['providers'].keys()))
    acw = data['models']['providers'].get('aicodewith', {})
    print('AiCodeWith models:', len(acw.get('models', [])))
except json.JSONDecodeError as e:
    print(f'JSON error: {e}')
    lines_t = text.split('\n')
    for j in range(max(0, e.lineno-3), min(len(lines_t), e.lineno+2)):
        print(f'  {j+1}: {lines_t[j][:100]}')
