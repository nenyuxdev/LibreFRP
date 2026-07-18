import curses
import json
import os
import subprocess
import time
import sys

if os.geteuid() != 0:
    print("LibreFRP requiere privilegios de root.")
    sys.exit(1)

DEVICES_FILE = "devices.json"
LOADERS_DIR = "loaders"

TEXTS = {
    "en": {
        "wait": "Waiting: {mode} mode",
        "target": "Target: {name}",
        "cancel": "Press 'q' to cancel",
        "title": "LibreFRP",
        "nav": "[ Arrows: Navigate ] [ Enter: Run ] [ L: Lang ] [ S: Search ] [ Q: Exit ]",
        "done": "Operation complete. Press any key.",
        "search": "Search: "
    },
    "es": {
        "wait": "Esperando: modo {mode}",
        "target": "Dispositivo: {name}",
        "cancel": "Presiona 'q' para cancelar",
        "title": "LibreFRP",
        "nav": "[ Flechas: Navegar ] [ Enter: Ejecutar ] [ L: Idioma ] [ S: Buscar ] [ Q: Salir ]",
        "done": "Operación completada. Presiona cualquier tecla.",
        "search": "Buscar: "
    }
}

def load_devices():
    if not os.path.exists(DEVICES_FILE): return []
    try:
        with open(DEVICES_FILE, "r") as f:
            return sorted(json.load(f), key=lambda x: x['name'].lower())
    except: return []

def draw_borders(stdscr, y1, x1, y2, x2):
    t, b, tr, br, h, v = '╭', '╰', '╮', '╯', '─', '│'
    stdscr.addstr(y1, x1, t)
    stdscr.addstr(y1, x2, tr)
    stdscr.addstr(y2, x1, b)
    stdscr.addstr(y2, x2, br)
    for x in range(x1 + 1, x2):
        stdscr.addstr(y1, x, h)
        stdscr.addstr(y2, x, h)
    for y in range(y1 + 1, y2):
        stdscr.addstr(y, x1, v)
        stdscr.addstr(y, x2, v)

def draw_rounded_window(win):
    h, w = win.getmaxyx()
    
    def safe(y, x, char):
        try: win.addch(y, x, char)
        except curses.error: pass
    
    safe(0, 0, '╭')
    safe(0, w-1, '╮')
    safe(h-1, 0, '╰')
    safe(h-1, w-1, '╯')
    for i in range(1, w-1):
        safe(0, i, '─')
        safe(h-1, i, '─')
    for i in range(1, h-1):
        safe(i, 0, '│')
        safe(i, w-1, '│')

def get_device_cmd(dev):
    loader = dev.get('loader')
    path = os.path.join(LOADERS_DIR, loader) if loader else None
    
    if dev['type'] == "MTK":
        l_arg = f" --loader={path}" if path else ""
        return f"mtk {dev['action']}{l_arg}"
    
    if dev['type'] == "Qualcomm":
        mem = dev.get('memory', 'emmc')
        lun = f" --lun={dev['lun']}" if dev.get('lun') else ""
        l_arg = f" --loader={path}" if path else ""
        return f"edl {dev['action']} --memory={mem}{lun}{l_arg}"
    return None

def open_search(stdscr, query, lang):
    win = curses.newwin(3, 30, 3, stdscr.getmaxyx()[1] - 32)
    draw_rounded_window(win)
    win.keypad(True)
    curses.curs_set(1)
    while True:
        win.addstr(1, 2, f"{TEXTS[lang]['search']} {query} ".ljust(26))
        win.refresh()
        key = win.getch()
        if key in [10, 13]: break
        elif key in [curses.KEY_BACKSPACE, 127, 8]: query = query[:-1]
        elif 32 <= key <= 126: query += chr(key)
    curses.curs_set(0)
    stdscr.touchwin()
    stdscr.refresh()
    return query

def wait_for_device(stdscr, dev, lang):
    stdscr.nodelay(True)
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_borders(stdscr, 1, 1, h - 2, w - 2)
        stdscr.addstr(2, 3, f"{TEXTS[lang]['title']} [{lang.upper()}]", curses.A_BOLD)
        stdscr.addstr(4, 3, TEXTS[lang]["wait"].format(mode=dev['type']), curses.A_BOLD)
        stdscr.addstr(5, 3, TEXTS[lang]["target"].format(name=dev['name']), curses.A_DIM)
        stdscr.addstr(6, 3, TEXTS[lang]["cancel"], curses.A_DIM)
        stdscr.refresh()
        if stdscr.getch() == ord('q'): return False
        try:
            out = subprocess.check_output("lsusb", shell=True, stderr=subprocess.DEVNULL).decode()
            if (dev['type'] == "MTK" and "0e8d:" in out) or (dev['type'] == "Qualcomm" and "05c6:" in out):
                return True
        except: pass
        time.sleep(1)

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    all_devs = load_devices()
    sel, scroll, lang = 0, 0, "es"
    query = ""
    
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        draw_borders(stdscr, 1, 1, h - 2, w - 2)
        
        filtered = [d for d in all_devs if query.lower() in d['name'].lower()]
        if sel >= len(filtered): sel = max(0, len(filtered) - 1)
        
        stdscr.addstr(2, 3, f"{TEXTS[lang]['title']} [{lang.upper()}]", curses.A_BOLD)
        
        for i, d in enumerate(filtered[scroll : scroll + (h-8)]):
            idx = i + scroll
            line = f"{'>' if idx == sel else ' '} {d['name']}"
            if idx == sel:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(4+i, 3, line.ljust(w-6))
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(4+i, 3, line)
        
        stdscr.addstr(h - 3, 3, TEXTS[lang]["nav"])
        stdscr.refresh()
        
        key = stdscr.getch()
        if key in [ord('s'), ord('S')]:
            query = open_search(stdscr, query, lang)
            sel = 0
        elif key == curses.KEY_UP and sel > 0: sel -= 1
        elif key == curses.KEY_DOWN and sel < len(filtered) - 1: sel += 1
        elif key in [ord('l'), ord('L')]: lang = "en" if lang == "es" else "es"
        elif key in [10, 13] and filtered:
            dev = filtered[sel]
            stdscr.nodelay(False)
            if wait_for_device(stdscr, dev, lang):
                cmd = get_device_cmd(dev)
                if cmd:
                    curses.reset_shell_mode()
                    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    curses.reset_prog_mode()
                    stdscr.clear()
                    stdscr.refresh()
                    stdscr.addstr(6, 3, TEXTS[lang]["done"], curses.A_BLINK)
                    stdscr.refresh()
                    stdscr.getch()
        elif key == ord('q'): break

if __name__ == "__main__":
    curses.wrapper(main)
