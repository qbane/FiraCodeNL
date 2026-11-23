from collections import OrderedDict
import re
import sys
import json
import openstep_plist


def transform_list_like(d):
    delim = ({'nl': '\n', 'sp': ' '})[d['$delim']]
    return delim.join(d['$elts'])


def from_dict(d, name_key='name'):
    arr = []
    keys = d['$keys'].split('!')
    del d['$keys']
    for k in keys:
        # ignore nonexistent key for convenience
        if k not in d: continue
        # if[]
        d[k][name_key] = k
        arr.append(d[k])
    return arr

# TODO: replace it with array_hook in Python 3.15
def replace_simple_lists_with_tuples(d):
    if isinstance(d, list):
        if all(isinstance(x, (str, int, float, bool, type(None))) for x in d):
            return tuple(d)
        return list(map(replace_simple_lists_with_tuples, d))
    if isinstance(d, dict):
        for k, v in d.items():
            # the only exception: horrible :(
            if k == 'tags': continue
            d[k] = replace_simple_lists_with_tuples(v)
    return d

def transform(data):
    data['classes'] = from_dict(data['classes'])
    for d in data['classes']:
        if 'code' in d:
            d['code'] = transform_list_like(d['code'])
    data['features'] = from_dict(data['features'], name_key='tag')
    data['fontMaster'][0]['guides'] = replace_simple_lists_with_tuples(data['fontMaster'][0]['guides'])
    for d in data['features']:
        if 'code' in d:
            d['code'] = transform_list_like(d['code'])
    data['glyphs'] = from_dict(data['glyphs'], name_key='glyphname')
    data['glyphs'] = replace_simple_lists_with_tuples(data['glyphs'])
    for i in range(len(data['instances'])):
        insts = data['instances']
        keys = insts[i]['$keys'].split('!')
        d = OrderedDict()
        for k in keys:
            d[k] = insts[i][k]
        insts[i] = d


def output(out):
    first = True
    for line in out.split('\n'):
        if not first:
            print()
        first = False
        print(line.replace('\\n', '\n'), end='')
    print()


def main(data):
    transform(data)
    out = openstep_plist.dumps(
        data,
        indent='',
        single_line_tuples=True,
        unicode_escape=False,
        single_line_empty_objects=False)
    output(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <FILE>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as fp:
        data = json.load(fp)
    main(data)
