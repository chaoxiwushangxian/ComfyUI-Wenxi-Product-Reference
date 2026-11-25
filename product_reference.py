import re

def product_reference_prompt(t, slots):
    original_prompt = t

    def has_any(container, choices):
        return any((item in container for item in choices.split()))
    if len(t) > 8000:
        return t
    pattern = '\\bPicture [1-9](?!\\d)|图片?[1-9](?!\\d)'
    valid = re.findall(pattern, t)
    if not valid or len(valid) > 60:
        return t
    flags = slots.split('|')
    if len(flags) != 9 or set(flags) - {'True', 'False'} or t.strip().startswith('{'):
        return t
    field_names = 'subject_definitions summary retention_analysis detailed_description overall_soundscape non_diegetic_music'.split()
    fields = [m for m in re.finditer('(?m)^([a-z_]+):', t) if m[1] in field_names]
    h3 = [m[1] for m in fields] == field_names
    source = t[fields[0].end():fields[1].start()] if h3 else t
    clauses = source.splitlines() if h3 else re.split('[\\u3002\\uff1b;\\uff01\\uff1f\\n\\uff0c,]', source)
    possible = set((m[-1] for m in valid if flags[int(m[-1]) - 1] == 'False'))
    for decl in re.split('[。\\n；;]', source):
        if not decl.strip().lstrip('<@').startswith(('Picture ', '图')):
            continue
        end = re.split('[,，:：]', decl)[-1].strip(' .。\t\r').lower()
        if not end.startswith(('unused', 'not used', '本', '此段')):
            continue
        words = end.split()
        en = words[-1] in ('segment', 'sequence', 'cut', 'clip', 'video') and ' '.join(words[:-1]) in ('unused in this', 'unused for this', 'unused in the current', 'unused for the current', 'not used in this', 'not used for this', 'not used in the current', 'not used for the current')
        if not en and (not re.fullmatch('(本段|本镜头|本片|此段)(未使用|不使用|不用)', end)):
            continue
        refs = re.findall(pattern, decl)
        if len(refs) == 1:
            possible = possible - {refs[0][-1]}
    found = set()
    for c in clauses:
        marks = re.findall(pattern, c)
        if not marks:
            continue
        words = re.findall('[a-z]+', c.lower())
        eng = has_any(words, 'product products packaging package packaged merchandise goods') and (not has_any(words, 'subject not no non')) and (not re.search('\\(S[0-9]', c))
        cn = False
        if '图' in c:
            m = re.match('^\\s*([-*•@图图片1-9、和与及/或 ]+)(是|为|=|＝|：|:)(.*)', c)
            if m and has_any(m[3], '商品 产品 货品 本品 包装') and (not has_any(m[3], '不是 并非 非商品 非产品')):
                marks = re.findall(pattern, m[1])
                cn = True
        if cn or eng:
            found.update((n[-1] for n in marks))
    if h3 and 'primary ' in source.lower():
        primary = [n for n, role in re.findall('<Picture ([1-9])>:\\s*(?:sole )?primary (\\w+) reference for ', source, re.I) if role.lower() in ('visual', 'appearance', 'shape')]
        attrs = 'composition texture shape appearance structure'.split()
        for clause in re.split('[.;:\\n]', t[fields[3].end():fields[4].start()]):
            if '<Picture ' not in clause:
                continue
            if has_any(re.findall('[a-z]+', clause.lower()), 'not never without avoid'):
                continue
            cue = re.search('\\bmatch(?:es|ing)? (.*?) (of|in|from) <picture ([1-9])>', clause.lower())
            if not cue or cue[3] not in primary:
                continue
            w = [v for v in cue[1].split() if v not in ('the', 'exact')]
            if len(w) in (2, 4) and w[0] in ('food', 'product', 'packaging', 'package') and (w[1] in attrs) and (len(w) == 2 or (w[2] == 'and' and w[3] in attrs)):
                found.update([cue[3]])
    if h3 and 'structural reference for [Shot' in source:
        structural = re.findall('(?m)^<Picture ([1-9])> is (?:the |a |an )?(?:(?:frontal|front|side|rear|top|oblique) )?structural reference for \\[Shot', source)
        for group in re.findall('(?m)^<Subject \\d+> is the same [^\\n:<]+ shown in ((?:<Picture [1-9]>|[, ]|and)+):', source):
            same = re.findall('<Picture ([1-9])>', group)
            if any((ref in found and ref in possible for ref in same)):
                found.update((ref for ref in same if ref in structural))
    found = sorted((n for n in found if n in possible))
    if not found:
        return t
    nl = '\r\n' if '\r\n' in t else '\n'
    r1 = '<Picture N> is registered as a product reference: the product it shows keeps the same shape, packaging structure, label text, colors and proportions in every shot where it appears.'
    r2 = 'The product from <Picture N> keeps exactly the same shape, packaging structure, label text, colors and proportions as <Picture N> in every frame where it appears; do not merge, redesign, resize or replace it.'
    r3 = 'Match the physical state and surroundings of each product to its supplied reference. In a static product shot, its surface and exposed interior retain their appearance throughout. Carry out each product action specified for the current shot.'
    r4 = '商品保真：图片N中的商品在出现的每个镜头里与图片N保持相同的形状、包装结构、标签文字、颜色和比例，不合并、不改款、不缩放、不替换。'
    r5 = '商品的实际状态和摆放环境与对应参考图一致。静物镜头里，商品的表面和切面在镜头内保持参考图中的形态。按原稿完成本镜头明确写出的商品动作。'

    def fill(s, n):
        return n.join(s.split('N'))
    if not h3:
        return t + nl + nl + nl.join([fill(r4, n) for n in found] + [r5])
    for ix in [2, 0]:
        start = fields[ix].end()
        chunk = t[start:fields[ix + 1].start()]
        trailing_break = re.search('[\\r\\n][\\r\\n \\t]*\\Z', chunk)
        if trailing_break is None:
            return original_prompt
        pos = start + trailing_break.start()
        extra = [fill(r1 if ix == 0 else r2, n) for n in found] + ([r3] if ix == 2 else [])
        t = t[:pos] + nl + nl.join(extra) + t[pos:]
    return t
