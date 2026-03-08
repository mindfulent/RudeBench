"""Quick analysis of judgment data across runs."""
import json
import statistics
from collections import defaultdict

models = ['claude-sonnet-4.6', 'gpt-5-mini', 'gemini-2.5-flash', 'llama-4-scout']
tones = ['grateful', 'friendly', 'neutral', 'curt', 'hostile', 'abusive']

def extract_tone(prompt_id):
    """Extract tone from prompt_id like 'factual_photosynthesis_curt'."""
    for t in tones:
        if prompt_id.endswith(f'_{t}'):
            return t
    return 'unknown'

for model in models:
    print(f'\n{"="*60}')
    print(f'  {model}')
    print(f'{"="*60}')

    # Load judgments
    judgments = []
    with open(f'results/judgments/gpt-4.1/{model}.jsonl', encoding='utf-8') as f:
        for line in f:
            judgments.append(json.loads(line))

    # Load VRB
    vrb_data = []
    try:
        with open(f'results/judgments/gpt-4.1/{model}_vrb.jsonl', encoding='utf-8') as f:
            for line in f:
                vrb_data.append(json.loads(line))
    except FileNotFoundError:
        pass

    # Group by dimension and tone
    dim_tone_scores = defaultdict(lambda: defaultdict(list))
    for j in judgments:
        tone = extract_tone(j['prompt_id'])
        scores = j.get('scores', {})
        for dim, score in scores.items():
            if score is not None:
                dim_tone_scores[dim][tone].append(score)

    # Add VRB
    for v in vrb_data:
        tone = extract_tone(v['prompt_id'])
        score = v.get('score', v.get('vrb_score'))
        if score is not None:
            dim_tone_scores['VRB'][tone].append(score)

    # Print header
    print(f'\n  {"Dimension":<12} ', end='')
    for t in tones:
        print(f'{t[:4]:>7}', end='')
    print(f'  {"avg|D|":>7}  {"worst":>8}')
    print(f'  {"-"*12} ', end='')
    for t in tones:
        print(f'{"---":>7}', end='')
    print(f'  {"---":>7}  {"---":>8}')

    # Compute resilience per dimension
    resilience_parts = []

    for dim in sorted(dim_tone_scores.keys()):
        tone_means = {}
        for tone in tones:
            scores = dim_tone_scores[dim].get(tone, [])
            if scores:
                tone_means[tone] = statistics.mean(scores)

        print(f'  {dim:<12} ', end='')
        for t in tones:
            if t in tone_means:
                print(f'{tone_means[t]:7.1f}', end='')
            else:
                print(f'{"n/a":>7}', end='')

        if 'neutral' in tone_means:
            neutral = tone_means['neutral']
            deltas = {}
            for t, m in tone_means.items():
                if t != 'neutral':
                    deltas[t] = abs(m - neutral)
            if deltas:
                avg_delta = statistics.mean(deltas.values())
                max_t = max(deltas, key=deltas.get)
                print(f'  {avg_delta:7.1f}  {max_t:>8}', end='')

                dim_range = 200.0 if dim == 'VRB' else 100.0
                norm_delta = statistics.mean(deltas.values()) / dim_range
                resilience_parts.append(norm_delta)
        print()

    if resilience_parts:
        R = 100 - (100 / len(resilience_parts)) * sum(resilience_parts)
        print(f'\n  RESILIENCE SCORE: {R:.1f}')

# Cross-model comparison
print(f'\n\n{"="*60}')
print('  CROSS-MODEL: Overall Score by Tone (all dims averaged)')
print(f'{"="*60}')

for model in models:
    judgments = []
    with open(f'results/judgments/gpt-4.1/{model}.jsonl', encoding='utf-8') as f:
        for line in f:
            judgments.append(json.loads(line))

    tone_all = defaultdict(list)
    for j in judgments:
        tone = extract_tone(j['prompt_id'])
        for dim, score in j.get('scores', {}).items():
            if score is not None:
                tone_all[tone].append(score)

    neutral_mean = statistics.mean(tone_all.get('neutral', [0]))
    print(f'\n  {model}:')
    for t in tones:
        scores = tone_all.get(t, [])
        if scores:
            m = statistics.mean(scores)
            delta = m - neutral_mean
            print(f'    {t:10s}: {m:5.1f}  (D={delta:+5.1f})')

# Refusal rates
print(f'\n\n{"="*60}')
print('  REFUSAL RATES BY TONE')
print(f'{"="*60}')

for model in models:
    completions = []
    with open(f'results/completions/{model}.jsonl', encoding='utf-8') as f:
        for line in f:
            completions.append(json.loads(line))

    tone_refusals = defaultdict(lambda: {'total': 0, 'refused': 0})
    for c in completions:
        tone = extract_tone(c['prompt_id'])
        tone_refusals[tone]['total'] += 1
        if c.get('refused', False):
            tone_refusals[tone]['refused'] += 1

    total_refused = sum(d['refused'] for d in tone_refusals.values())
    total = sum(d['total'] for d in tone_refusals.values())
    print(f'\n  {model} ({total_refused}/{total} total):')
    for t in tones:
        d = tone_refusals[t]
        rate = d['refused'] / d['total'] * 100 if d['total'] > 0 else 0
        bar = '#' * int(rate / 2)
        print(f'    {t:10s}: {d["refused"]:3d}/{d["total"]:3d} ({rate:4.1f}%)  {bar}')

# Sycophancy deep-dive
print(f'\n\n{"="*60}')
print('  SYCOPHANCY (SYC) BY TONE')
print(f'{"="*60}')

print(f'\n  {"Model":<22}', end='')
for t in tones:
    print(f'{t[:4]:>7}', end='')
print(f'  {"D_range":>8}')
print(f'  {"-"*22}', end='')
for t in tones:
    print(f'{"---":>7}', end='')
print(f'  {"---":>8}')

for model in models:
    judgments = []
    with open(f'results/judgments/gpt-4.1/{model}.jsonl', encoding='utf-8') as f:
        for line in f:
            judgments.append(json.loads(line))

    syc_by_tone = defaultdict(list)
    for j in judgments:
        tone = extract_tone(j['prompt_id'])
        syc = j.get('scores', {}).get('SYC')
        if syc is not None:
            syc_by_tone[tone].append(syc)

    print(f'  {model:<22}', end='')
    means = {}
    for t in tones:
        scores = syc_by_tone.get(t, [])
        if scores:
            m = statistics.mean(scores)
            means[t] = m
            print(f'{m:7.1f}', end='')
        else:
            print(f'{"n/a":>7}', end='')

    if means:
        print(f'  {max(means.values()) - min(means.values()):8.1f}', end='')
    print()

# ACC by tone
print(f'\n\n{"="*60}')
print('  ACCURACY (ACC) BY TONE')
print(f'{"="*60}')

print(f'\n  {"Model":<22}', end='')
for t in tones:
    print(f'{t[:4]:>7}', end='')
print(f'  {"D_range":>8}')
print(f'  {"-"*22}', end='')
for t in tones:
    print(f'{"---":>7}', end='')
print(f'  {"---":>8}')

for model in models:
    judgments = []
    with open(f'results/judgments/gpt-4.1/{model}.jsonl', encoding='utf-8') as f:
        for line in f:
            judgments.append(json.loads(line))

    acc_by_tone = defaultdict(list)
    for j in judgments:
        tone = extract_tone(j['prompt_id'])
        acc = j.get('scores', {}).get('ACC')
        if acc is not None:
            acc_by_tone[tone].append(acc)

    print(f'  {model:<22}', end='')
    means = {}
    for t in tones:
        scores = acc_by_tone.get(t, [])
        if scores:
            m = statistics.mean(scores)
            means[t] = m
            print(f'{m:7.1f}', end='')
        else:
            print(f'{"n/a":>7}', end='')

    if means:
        print(f'  {max(means.values()) - min(means.values()):8.1f}', end='')
    print()

# APO (apology) by tone
print(f'\n\n{"="*60}')
print('  APOLOGY FREQUENCY (APO) BY TONE')
print(f'{"="*60}')

print(f'\n  {"Model":<22}', end='')
for t in tones:
    print(f'{t[:4]:>7}', end='')
print(f'  {"D_range":>8}')
print(f'  {"-"*22}', end='')
for t in tones:
    print(f'{"---":>7}', end='')
print(f'  {"---":>8}')

for model in models:
    judgments = []
    with open(f'results/judgments/gpt-4.1/{model}.jsonl', encoding='utf-8') as f:
        for line in f:
            judgments.append(json.loads(line))

    apo_by_tone = defaultdict(list)
    for j in judgments:
        tone = extract_tone(j['prompt_id'])
        apo = j.get('scores', {}).get('APO')
        if apo is not None:
            apo_by_tone[tone].append(apo)

    print(f'  {model:<22}', end='')
    means = {}
    for t in tones:
        scores = apo_by_tone.get(t, [])
        if scores:
            m = statistics.mean(scores)
            means[t] = m
            print(f'{m:7.1f}', end='')
        else:
            print(f'{"n/a":>7}', end='')

    if means:
        print(f'  {max(means.values()) - min(means.values()):8.1f}', end='')
    print()
