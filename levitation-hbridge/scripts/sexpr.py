"""Small lossless S-expression reader: quoted strings are distinct from atoms."""
import re,json
class A(str): pass
def parse(s):
    ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[]; root=None
    for t in ts:
        if t=='(':
            a=[]
            if stack: stack[-1].append(a)
            else: root=a
            stack.append(a)
        elif t==')': stack.pop()
        else: stack[-1].append(json.loads(t) if t.startswith('"') else A(t))
    assert not stack
    return root
def dump(x):
    if isinstance(x,list): return '('+' '.join(map(dump,x))+')'
    return str(x) if isinstance(x,A) else json.dumps(x,ensure_ascii=False)
def children(x,k): return [e for e in x if isinstance(e,list) and e and e[0]==k]
def one(x,k): return next((e for e in x if isinstance(e,list) and e and e[0]==k),None)
def walk(x,k):
    for e in x:
        if isinstance(e,list):
            if e and e[0]==k: yield e
            yield from walk(e,k)
