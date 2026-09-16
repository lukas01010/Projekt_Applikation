import py5

# Zustand für die Schritt-Steuerung
current_step = 0

factor_steps = []


class FactorNode:

  def __init__(self, value, x, y):
    self.value = value
    self.x = x
    self.y = y
    self.left = None
    self.right = None


def setup():
  py5.size(900, 600)
  py5.background(20)
  # Hier kannst du deine Startzahl (z.B. 60) initialisieren und den Baum berechnen


def draw():
  py5.background(20)

  # Textanweisungen für den Nutzer einblenden
  py5.fill(255)
  py5.text("Klicke, um den nächsten Schritt zu berechnen.", 30, 40)

  # Hier den Baum rekursiv bis zum aktuellen `current_step` zeichnen


def mouse_pressed():
  global current_step
  # Mit jedem Klick einen Schritt weitergehen
  current_step += 1