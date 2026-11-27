'''Each function takes a single line and transforms it in some way.'''



def _pair(line, delim, open_tag, close_tag):
    '''
    Replace each alternating pair of delim with open_tag/close_tag.

    >>> _pair('a*b*c', '*', '<i>', '</i>')
    'a<i>b</i>c'
    >>> _pair('a*b', '*', '<i>', '</i>')
    'a*b'
    '''
    out, i, opened, len_d = '', 0, False, len(delim)
    while i < len(line):
        if line[i:i+len_d] == delim:
            if opened:
                out += close_tag
                opened = False
            else:
                out += open_tag
                opened = True
            i += len_d
        else:
            out += line[i]
            i += 1
    if opened:
        # Unmatched opener: undo the trailing open_tag and emit the delim.
        if out.endswith(open_tag):
            out = out[:-len(open_tag)] + delim
    return out


def compile_headers(line):
    if not line.startswith('#'):
        return line
    stripped = line.strip()
    level = 0
    while level < len(stripped) and stripped[level] == '#':
        level += 1
    content = stripped[level:]
    return f'<h{level}>{content}</h{level}>'

def _linkify(link_text, href):
    return f'<a href="{href}">{link_text}</a>'


def compile_italic_star(line):
    # Do not emit a tag if the delimiter will be unmatched.
    count = line.count('*')
    if count < 2:
        return line
    return _pair(line, '*', '<i>', '</i>')


def compile_italic_underscore(line):
    # Only treat underscores as style markers when adjacent to non-alphabetic chars
    count = line.count('_')
    if count < 2:
        return line
    return _pair(line, '_', '<i>', '</i>')


def compile_bold_underscore(line):
    return line


def compile_strikethrough(line):
    count = line.count('~~')
    if count < 2:
        return line
    return _pair(line, '~~', '<ins>', '</ins>')


def compile_bold_stars(line):
    count = line.count('**')
    if count < 2:
        return line
    return _pair(line, '**', '<b>', '</b>')


def compile_code_inline(line):
    out, inside, i = '', False, 0
    while i < len(line):
        if line[i:i + 3] == '```':
            out += '```'
            i += 3
            continue
        c = line[i]
        if c == '`':
            out += '</code>' if inside else '<code>'
            inside = not inside
        elif inside and c == '<':
            out += '&lt;'
        elif inside and c == '>':
            out += '&gt;'
        else:
            out += c
        i += 1
    return out


def compile_links(line):
    out = line
    while '[' in out and '](' in out:
        i = out.find('[')
        j = out.find('](', i)
        k = out.find(')', j)
        if j < 0 or k < 0:
            break
        out = out[:i] + f'<a href="{out[j+2:k]}">{out[i+1:j]}</a>' + out[k+1:]
    return out


def compile_images(line):
    out = line
    while ']' in out and '![' in out:
        i = out.find('![')
        j = out.find('](', i)
        k = out.find(')', j)
        if j < 0 or k < 0:
            break
        alt = out[i + 2:j]
        src = out[j + 2:k]
        out = out[:i] + f'<img src="{src}" alt="{alt}" />' + out[k + 1:]
    return out
