import curses
import json
import os
import subprocess
import time
import sys

if os.geteuid() != 0:
    print("LibreFRP requiere privilegios de root. Ejecuta: sudo python3 LibreFRP.py")
    sys.exit(1)

DEVICES_FILE = "devices.json"
LOADERS_DIR = "loaders"

TEXTS = {
    "en": {
        "wait": "Waiting: {mode} mode",
        "target": "Target: {name}",
        "cancel": "Press 'q' to cancel",
        "title": "LibreFRP",
        "nav": "[ Arrows: Navigate ] [ Enter: Run ] [ L: Toggle Lang ] [ Q: Exit ]",
        "proc": "Processing {name}...",
        "done": "Operation complete. Press any key."
    },
    "es": {
        "wait": "Esperando: modo {mode}",
        "target": "Dispositivo: {name}",
        "cancel": "Presiona 'q' para cancelar",
        "title": "LibreFRP",
        "nav": "[ Flechas: Navegar ] [ Enter: Ejecutar ] [ L: Cambiar Idioma ] [ Q: Salir ]",
        "proc": "Procesando {name}...",
        "done": "Operación completada. Presiona cualquier tecla."
    }
}

def load_devices():
    if not os.path.exists(DEVICES_FILE): return []
    try:
        with open(DEVICES_FILE, "r") as f:
            return sorted(json.load(f), key=lambda x: x['name'].lower())
    except: return []

def draw_borders(stdscr, y1, x1, y2, x2):
    stdscr.addstr(y1, x1, '╭')
    stdscr.addstr(y1, x2, '╮')
    stdscr.addstr(y2, x1, '╰')
    stdscr.addstr(y2, x2, '╯')
    for x in range(x1 + 1, x2): 
        stdscr.addstr(y1, x, '─')
        stdscr.addstr(y2, x, '─')
    for y in range(y1 + 1, y2): 
        stdscr.addstr(y, x1, '│')
        stdscr.addstr(y, x2, '│')

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
            out = subprocess.check_output("lsusb", shell=True).decode()
            if (dev['type'] == "MTK" and "0e8d:" in out) or (dev['type'] == "Qualcomm" and "05c6:" in out):
                return True
        except: pass
        time.sleep(1)

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    all_devices = load_devices()
    selected, scroll_offset, lang = 0, 0, "es"
    
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        draw_borders(stdscr, 1, 1, h - 2, w - 2)
        stdscr.addstr(2, 3, f"{TEXTS[lang]['title']} [{lang.upper()}]", curses.A_BOLD)
        
        for i, d in enumerate(all_devices[scroll_offset : scroll_offset + (h-8)]):
            idx = i + scroll_offset
            line = f"{'>' if idx == selected else ' '} {d['name']}"
            if idx == selected:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(4+i, 3, line.ljust(w-6))
                stdscr.attroff(curses.color_pair(1))
            else: stdscr.addstr(4+i, 3, line)
        
        stdscr.addstr(h - 3, 3, TEXTS[lang]["nav"])
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == curses.KEY_UP and selected > 0: selected -= 1
        elif key == curses.KEY_DOWN and selected < len(all_devices) - 1: selected += 1
        elif key in [ord('l'), ord('L')]: lang = "en" if lang == "es" else "es"
        elif key in [10, 13]:
            dev = all_devices[selected]
            if wait_for_device(stdscr, dev, lang):
                tool = "mtk" if dev['type'] == "MTK" else "edl"
                loader = f" --loader={os.path.join(LOADERS_DIR, dev['loader'])}" if dev.get('loader') else ""
                cmd = f"{tool} {dev['action']}{loader}"
                
                stdscr.erase()
                draw_borders(stdscr, 1, 1, h - 2, w - 2)
                stdscr.addstr(2, 3, f"{TEXTS[lang]['title']} [{lang.upper()}]", curses.A_BOLD)
                stdscr.addstr(4, 3, TEXTS[lang]["proc"].format(name=dev['name']), curses.A_BOLD)
                stdscr.refresh()
                
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                stdscr.nodelay(False)
                stdscr.addstr(6, 3, TEXTS[lang]["done"], curses.A_BLINK)
                stdscr.refresh()
                stdscr.getch()
        elif key == ord('q'): break

if __name__ == "__main__":
    curses.wrapper(main)