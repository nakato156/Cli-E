from pathlib import Path
import subprocess
import keyboard
import platform
import curses
import os

ruta_actual = Path(os.getcwd())

class Explorador:
	actions = {
		"abrir": {
			"windows": "start",
			"linux": "xdg-open",
			"darwin": "open"
		}
	}

	def __init__(self, path_inicial:Path) -> None:
		self.i = 0
		self.ruta_actual = path_inicial
		self.historial = [path_inicial]
		self.plataforma = platform.system().lower()

	def listar(self) -> list:
		return [(path, path.name) for path in self.ruta_actual.iterdir()]

	def cd(self, new_path: str):
		self.ruta_actual = new_path
		if self.i != len(self.historial) - 1:
			act, sig = self.historial[self.i: self.i + 2]
			self.historial[self.i: self.i + 2] = [sig, act]
			self.historial.append(new_path)
			self.i = len(self.historial)
		else:
			self.historial.append(new_path)
			self.i += 1

	def open(self, filename: str):
		cmd = Explorador.actions["abrir"][self.plataforma]
		subprocess.run([cmd, filename], shell=True)

	def up(self, callback = None):
		self.ruta_actual = self.ruta_actual.parent
		self.historial.append(self.ruta_actual)
		self.i += 1
		if callback: callback(self)

	def back(self, callback = None):
		if self.i - 1 < 0: return
		self.i -= 1 
		self.ruta_actual = self.historial[self.i]
		if callback: callback(self)

	def next(self, callback = None):
		if self.i + 1 > len(self.historial) - 1: return
		self.i+= 1
		self.ruta_actual = self.historial[self.i]
		if callback: callback(self)

def update_view(exp, stdscr):
	contenido_directorio = exp.listar()

	stdscr.clear()
	stdscr.addstr(0, 0, f"{exp.ruta_actual}:\n\t-")
	stdscr.addstr(1, 0, '\n'.join(f"\t- {name}" for _, name in contenido_directorio))
	stdscr.refresh()

def on_press(exp, stdscr):
	if keyboard.is_pressed('left') or keyboard.is_pressed('right') or keyboard.is_pressed('up'):
		update_view(exp, stdscr)

def open_explorer(exp: Explorador, callback = None):
	cmd = exp.actions["abrir"][platform.system().lower()]
	subprocess.run([cmd, exp.ruta_actual], shell=True)
	if callback: callback(exp)

def set_hot_keys(explorador: Explorador, callback):
	keyboard.add_hotkey('ctrl + left', lambda: explorador.back(callback))
	keyboard.add_hotkey('ctrl + right', lambda: explorador.next(callback))
	keyboard.add_hotkey('ctrl + up', lambda: explorador.up(callback))
	keyboard.add_hotkey('ctrl + e', lambda: open_explorer(explorador, callback))

def main():
	exp = Explorador(ruta_actual)

	stdscr = curses.initscr()
	curses.cbreak()

	callback = lambda exp: update_view(exp, stdscr)
	set_hot_keys(exp, callback)

	stdscr.keypad(True)

	update_view(exp, stdscr)

	key = stdscr.getch()

	acciones_teclas = {
		curses.KEY_UP: stdscr.move(stdscr.getyx()[0] - 1, stdscr.getyx()[1]),
		curses.KEY_DOWN: stdscr.move(stdscr.getyx()[0] + 1, stdscr.getyx()[1]),
		curses.KEY_LEFT: stdscr.move(stdscr.getyx()[0], stdscr.getyx()[1] - 1),
		curses.KEY_RIGHT: stdscr.move(stdscr.getyx()[0], stdscr.getyx()[1] + 1),

	}

	# Mover el cursor según la tecla presionada
	while key != ord('q'):
		if key in acciones_teclas:
			acciones_teclas[key]
		elif key == ord('\n') or key == ord('\r'):
			num_linea = stdscr.getyx()[0]
			contenido_directorio = exp.listar()
			new_path = contenido_directorio[num_linea - 2]
			if new_path[0].is_dir():
				exp.cd(new_path[0])
				update_view(exp, stdscr)
			else:
				exp.open(str(new_path[0]))
		key = stdscr.getch()

	# Salir del modo de captura de teclas y restaurar la configuración de la pantalla
	curses.nocbreak()
	stdscr.keypad(False)
	curses.echo()
	curses.endwin()

if __name__ == '__main__':
	main()