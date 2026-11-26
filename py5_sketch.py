import py5
import math

# Zustand der Anwendung: "menu", "prim", "ggt", "kgv"
mode = "menu"

# Matte Farbpalette (Hell & Ruhig)
BG_MAIN = (245, 246, 248)        # Warmes Hellgrau als Hintergrund
CARD_BG = (255, 255, 255)        # Mattes Weiss für Karten & Eingabefelder
BORDER_SOFT = (220, 225, 232)    # Dezente Rahmenfarbe
TEXT_DARK = (44, 51, 63)         # Weiches Anthrazit statt hartem Schwarz
TEXT_MUTED = (115, 124, 138)     # Ruhiges Graublau für Hinweise

# Matte Themenfarben für die drei Bereiche
THEME_PRIM = (102, 149, 178)     # Mattes Taubenblau
THEME_PRIM_LIGHT = (234, 242, 247)

THEME_GGT = (104, 154, 132)      # Mattes Salbeigrün
THEME_GGT_LIGHT = (234, 244, 239)

THEME_KGV = (144, 122, 168)      # Mattes Lavendel
THEME_KGV_LIGHT = (242, 238, 247)

BTN_NEUTRAL = (228, 232, 238)

# Variablen für Primfaktorzerlegung
input_text = ""
number = None
current_tree = None
factor_steps = []
current_step = 0
message = "Gib eine Zahl ein und drücke Enter."

# Variablen für ggT und kgV
input_a = ""
input_b = ""
active_field = 0  # 0 = Zahl 1, 1 = Zahl 2
num_a = None
num_b = None
pair_message = "Gib zwei Zahlen ein (Tab oder Klick zum Wechseln) und drücke Enter."


class FactorNode:

  def __init__(self, value, x=0, y=0):
    self.value = value
    self.x = x
    self.y = y
    self.left = None
    self.right = None


def setup():
  py5.size(1200, 800)
  py5.text_font(py5.create_font("Verdana", 22))
  py5.text_align(py5.LEFT, py5.CENTER)


def is_prime(value):
  if value < 2:
    return False
  divisor = 2
  while divisor * divisor <= value:
    if value % divisor == 0:
      return False
    divisor += 1
  return True


def smallest_factor(value):
  divisor = 2
  while divisor * divisor <= value:
    if value % divisor == 0:
      return divisor
    divisor += 1
  return value


def build_factor_tree(value):
  node = FactorNode(value)
  if not is_prime(value):
    factor = smallest_factor(value)
    node.left = build_factor_tree(factor)
    node.right = build_factor_tree(value // factor)
  return node


def collect_steps(node):
  if node.left is None:
    return
  factor_steps.append(node)
  collect_steps(node.left)
  collect_steps(node.right)


def get_prime_factors(value):
  factors = []
  divisor = 2
  while divisor * divisor <= value:
    while value % divisor == 0:
      factors.append(divisor)
      value //= divisor
    divisor += 1
  if value > 1:
    factors.append(value)
  return factors


def format_factors(factors):
  if not factors:
    return "1"
  return " × ".join(str(f) for f in factors)


def reset_mode(new_mode):
  global mode, input_text, number, current_tree, factor_steps, current_step, message
  global input_a, input_b, active_field, num_a, num_b, pair_message

  mode = new_mode
  input_text = ""
  number = None
  current_tree = None
  factor_steps = []
  current_step = 0
  message = "Gib eine Zahl ein und drücke Enter."

  input_a = ""
  input_b = ""
  active_field = 0
  num_a = None
  num_b = None
  pair_message = "Gib zwei Zahlen ein (Tab oder Klick zum Wechseln) und drücke Enter."


def calculate_number():
  global number, current_tree, factor_steps, current_step, message

  if not input_text:
    message = "Bitte zuerst eine Zahl eingeben."
    return

  candidate = int(input_text)
  if candidate < 2:
    number = None
    current_tree = None
    factor_steps = []
    message = "Bitte eine ganze Zahl grösser als 1 eingeben."
    return

  number = candidate
  factor_steps = []
  current_step = 0
  current_tree = build_factor_tree(number)
  position_tree(current_tree, 80, 1120, 325)
  collect_steps(current_tree)
  if is_prime(number):
    message = f"{number} ist bereits eine Primzahl."
  else:
    message = "Klicke auf das Feld oder drücke die Leertaste für den nächsten Schritt."


def calculate_pair():
  global num_a, num_b, pair_message

  if not input_a or not input_b:
    pair_message = "Bitte beide Zahlen eingeben."
    num_a = None
    num_b = None
    return

  a = int(input_a)
  b = int(input_b)
  if a < 1 or b < 1:
    pair_message = "Bitte nur ganze Zahlen grösser als 0 eingeben."
    num_a = None
    num_b = None
    return

  num_a = a
  num_b = b
  pair_message = "Berechnung abgeschlossen:"


def draw():
  py5.background(*BG_MAIN)

  if mode == "menu":
    draw_menu()
  elif mode == "prim":
    draw_header("Primfaktorzerlegung", THEME_PRIM)
    draw_prim()
  elif mode == "ggt":
    draw_header("Grösster gemeinsamer Teiler (ggT)", THEME_GGT)
    draw_ggt_kgv()
  elif mode == "kgv":
    draw_header("Kleinstes gemeinsames Vielfaches (kgV)", THEME_KGV)
    draw_ggt_kgv()


def draw_button(x, y, w, h, label, bg_color, text_color=(255, 255, 255), font_size=18):
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h
  if hover:
    py5.fill(max(0, bg_color[0] - 16), max(0, bg_color[1] - 16), max(0, bg_color[2] - 16))
  else:
    py5.fill(*bg_color)
  py5.no_stroke()
  py5.rect(x, y, w, h, 10)
  py5.fill(*text_color)
  py5.text_size(font_size)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(label, x + w / 2, y + h / 2)
  py5.text_align(py5.LEFT, py5.CENTER)


def draw_menu_card(x, y, w, h, title, subtitle, accent_color, light_bg):
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h
  py5.fill(*(light_bg if hover else CARD_BG))
  py5.stroke(*(accent_color if hover else BORDER_SOFT))
  py5.stroke_weight(2 if hover else 1.5)
  py5.rect(x, y, w, h, 14)

  # Farbiger Akzentstreifen links
  py5.no_stroke()
  py5.fill(*accent_color)
  py5.rect(x, y, 10, h, 14, 0, 0, 14)

  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_DARK)
  py5.text_size(22)
  py5.text(title, x + 32, y + 36)

  py5.fill(*TEXT_MUTED)
  py5.text_size(15)
  py5.text(subtitle, x + 32, y + 68)


def draw_header(title, accent_color):
  # Dezente Kopfleiste
  py5.fill(*CARD_BG)
  py5.no_stroke()
  py5.rect(0, 0, 1200, 74)
  py5.stroke(*BORDER_SOFT)
  py5.stroke_weight(1.5)
  py5.line(0, 74, 1200, 74)

  # Kleiner Farbpunkt vor dem Titel
  py5.no_stroke()
  py5.fill(*accent_color)
  py5.ellipse(58, 37, 14, 14)

  py5.fill(*TEXT_DARK)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(22)
  py5.text(title, 78, 37)

  draw_button(970, 17, 180, 40, "Zurück zum Menü", BTN_NEUTRAL, TEXT_DARK, 16)


def draw_info_banner(title, theory_text, accent_color, light_bg):
  x, y, w, h = 50, 92, 1100, 90

  py5.fill(*light_bg)
  py5.stroke(accent_color[0], accent_color[1], accent_color[2], 90)
  py5.stroke_weight(1.5)
  py5.rect(x, y, w, h, 12)

  py5.no_stroke()
  py5.fill(*accent_color)
  py5.rect(x, y, 8, h, 12, 0, 0, 12)

  py5.text_align(py5.LEFT, py5.TOP)
  py5.fill(*accent_color)
  py5.text_size(16)
  py5.text(title, x + 24, y + 12)

  py5.fill(*TEXT_DARK)
  py5.text_size(15)
  py5.text(theory_text, x + 24, y + 38, w - 44, h - 42)

  py5.text_align(py5.LEFT, py5.CENTER)


def draw_input_box(x, y, w, h, prefix, value, placeholder, is_active, accent_color):
  py5.fill(*CARD_BG)
  if is_active:
    py5.stroke(*accent_color)
    py5.stroke_weight(2.2)
  else:
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1.5)
  py5.rect(x, y, w, h, 10)

  py5.no_stroke()
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(18)

  cursor = "|" if (is_active and py5.frame_count % 60 < 30) else ""
  if prefix:
    py5.fill(*TEXT_MUTED)
    py5.text(prefix, x + 16, y + h / 2)
    offset = py5.text_width(prefix) + 8
  else:
    offset = 0

  if value or is_active:
    py5.fill(*TEXT_DARK)
    py5.text(value + cursor, x + 16 + offset, y + h / 2)
  else:
    py5.fill(165, 172, 184)
    py5.text(placeholder, x + 16 + offset, y + h / 2)


def draw_menu():
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.fill(*TEXT_DARK)
  py5.text_size(34)
  py5.text("Mathe-Werkzeug", 600, 125)

  py5.fill(*TEXT_MUTED)
  py5.text_size(18)
  py5.text("Wähle ein Thema per Klick oder Taste (1, 2, 3):", 600, 170)

  draw_menu_card(
      310, 225, 580, 102,
      "1. Primfaktorzerlegung",
      "Zahlen Schritt für Schritt in ihre Primfaktoren zerlegen",
      THEME_PRIM, THEME_PRIM_LIGHT
  )
  draw_menu_card(
      310, 355, 580, 102,
      "2. Grösster gemeinsamer Teiler (ggT)",
      "Den grössten gemeinsamen Teiler zweier Zahlen bestimmen",
      THEME_GGT, THEME_GGT_LIGHT
  )
  draw_menu_card(
      310, 485, 580, 102,
      "3. Kleinstes gemeinsames Vielfaches (kgV)",
      "Das kleinste gemeinsame Vielfache zweier Zahlen finden",
      THEME_KGV, THEME_KGV_LIGHT
  )


def position_tree(node, left, right, y):
  if node is None:
    return
  node.x = (left + right) / 2
  node.y = y
  if node.left is not None:
    position_tree(node.left, left, node.x, y + 95)
  if node.right is not None:
    position_tree(node.right, node.x, right, y + 95)


def draw_factor_node(node, reveal_step):
  if node is None:
    return

  if node.left is not None and node.right is not None and reveal_step > 0:
    py5.stroke(180, 188, 200)
    py5.stroke_weight(2.2)
    py5.line(node.x, node.y, node.left.x, node.left.y)
    py5.line(node.x, node.y, node.right.x, node.right.y)

  if is_prime(node.value):
    py5.fill(*THEME_GGT)
    text_col = (255, 255, 255)
  elif reveal_step > 0:
    py5.fill(*THEME_PRIM)
    text_col = (255, 255, 255)
  else:
    py5.fill(218, 223, 230)
    text_col = TEXT_DARK

  py5.stroke(*CARD_BG)
  py5.stroke_weight(3)
  py5.ellipse(node.x, node.y, 58, 58)

  py5.fill(*text_col)
  py5.no_stroke()
  py5.text_size(18)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(str(node.value), node.x, node.y)

  if reveal_step > 0:
    draw_factor_node(node.left, reveal_step - 1)
    draw_factor_node(node.right, reveal_step - 1)


def draw_prim():
  draw_info_banner(
      "Theorie: Was ist eine Primfaktorzerlegung?",
      "Jede Zahl (ausser 1) lässt sich als Mal-Rechnung aus Primzahlen schreiben. "
      "Primzahlen sind nur durch 1 und sich selbst teilbar (z.B. 2, 3, 5, 7, 11). "
      "Beispiel: 12 = 2 × 2 × 3.",
      THEME_PRIM, THEME_PRIM_LIGHT
  )

  draw_input_box(50, 200, 380, 48, "", input_text, "Zahl eingeben (z.B. 84)...", True, THEME_PRIM)
  draw_button(445, 200, 145, 48, "Berechnen", THEME_PRIM, (255, 255, 255), 17)

  if number is not None and current_step < len(factor_steps):
    draw_button(605, 200, 185, 48, "Nächster Schritt", BTN_NEUTRAL, TEXT_DARK, 17)

  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_MUTED)
  py5.text_size(16)
  py5.text(message, 50, 268)

  if number is not None:
    if current_tree is not None:
      draw_factor_node(current_tree, current_step)

    if number >= 2:
      # Ergebniskarte unten
      py5.fill(*CARD_BG)
      py5.stroke(*BORDER_SOFT)
      py5.stroke_weight(1.5)
      py5.rect(50, 725, 1100, 50, 12)

      py5.no_stroke()
      py5.text_align(py5.LEFT, py5.CENTER)
      py5.fill(*TEXT_MUTED)
      py5.text_size(17)
      py5.text("Primfaktorzerlegung:", 72, 750)

      py5.fill(*THEME_GGT)
      py5.text_size(20)
      py5.text(f"{number} = " + format_factors(get_prime_factors(number)), 285, 750)


def draw_ggt_kgv():
  if mode == "ggt":
    accent = THEME_GGT
    light_bg = THEME_GGT_LIGHT
    draw_info_banner(
        "Theorie: Was ist der ggT?",
        "Der ggT ist die grösste Zahl, durch die beide Zahlen ohne Rest teilbar sind. "
        "Tipp mit Primfaktoren: Zerlege beide Zahlen und multipliziere alle Primfaktoren, "
        "die in beiden Zerlegungen gleichzeitig vorkommen.",
        accent, light_bg
    )
  else:
    accent = THEME_KGV
    light_bg = THEME_KGV_LIGHT
    draw_info_banner(
        "Theorie: Was ist das kgV?",
        "Das kgV ist die kleinste Zahl, die in der Malreihe von beiden Zahlen vorkommt. "
        "Tipp mit Primfaktoren: Nimm jeden vorkommenden Primfaktor so oft, "
        "wie er maximal in einer der beiden Zahlen steckt.",
        accent, light_bg
    )

  draw_input_box(50, 200, 350, 48, "Zahl 1:", input_a, "z.B. 24", active_field == 0, accent)
  draw_input_box(420, 200, 350, 48, "Zahl 2:", input_b, "z.B. 36", active_field == 1, accent)
  draw_button(790, 200, 160, 48, "Berechnen", accent, (255, 255, 255), 17)

  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_MUTED)
  py5.text_size(16)
  py5.text(pair_message, 50, 268)

  if num_a is not None and num_b is not None:
    greatest = math.gcd(num_a, num_b)

    # Ergebniskarte
    py5.fill(*CARD_BG)
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1.5)
    py5.rect(50, 300, 1100, 195, 14)

    py5.no_stroke()
    py5.fill(*accent)
    py5.rect(50, 300, 8, 195, 14, 0, 0, 14)

    py5.text_align(py5.LEFT, py5.CENTER)
    py5.fill(*TEXT_DARK)
    py5.text_size(30)
    if mode == "ggt":
      py5.text(f"ggT({num_a}, {num_b}) = {greatest}", 82, 348)
    elif mode == "kgv":
      least = abs(num_a * num_b) // greatest
      py5.text(f"kgV({num_a}, {num_b}) = {least}", 82, 348)

    # Trennlinie und Hilfe über Primfaktoren
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1)
    py5.line(82, 392, 1120, 392)

    py5.no_stroke()
    py5.fill(*TEXT_MUTED)
    py5.text_size(17)
    py5.text(f"Primfaktoren von {num_a}:  {format_factors(get_prime_factors(num_a))}", 82, 425)
    py5.text(f"Primfaktoren von {num_b}:  {format_factors(get_prime_factors(num_b))}", 82, 460)


def mouse_pressed():
  global current_step, active_field

  if mode == "menu":
    if 310 <= py5.mouse_x <= 890:
      if 225 <= py5.mouse_y <= 327:
        reset_mode("prim")
      elif 355 <= py5.mouse_y <= 457:
        reset_mode("ggt")
      elif 485 <= py5.mouse_y <= 587:
        reset_mode("kgv")
    return

  # Zurück-Button oben rechts
  if 970 <= py5.mouse_x <= 1150 and 17 <= py5.mouse_y <= 57:
    reset_mode("menu")
    return

  if mode == "prim":
    # Button "Berechnen"
    if 445 <= py5.mouse_x <= 590 and 200 <= py5.mouse_y <= 248:
      calculate_number()
      return
    # Klick auf Feld oder "Nächster Schritt"-Button
    if number is not None and current_step < len(factor_steps):
      current_step += 1

  elif mode in ("ggt", "kgv"):
    if 50 <= py5.mouse_x <= 400 and 200 <= py5.mouse_y <= 248:
      active_field = 0
    elif 420 <= py5.mouse_x <= 770 and 200 <= py5.mouse_y <= 248:
      active_field = 1
    elif 790 <= py5.mouse_x <= 950 and 200 <= py5.mouse_y <= 248:
      calculate_pair()


def key_pressed():
  global input_text, input_a, input_b, active_field, current_step

  if not isinstance(py5.key, str):
    return

  if mode == "menu":
    if py5.key == "1":
      reset_mode("prim")
    elif py5.key == "2":
      reset_mode("ggt")
    elif py5.key == "3":
      reset_mode("kgv")
    return

  if py5.key == "\t":
    if mode in ("ggt", "kgv"):
      active_field = 1 - active_field
    return

  if py5.key == chr(8) or py5.key == chr(127):
    if mode == "prim":
      input_text = input_text[:-1]
    elif mode in ("ggt", "kgv"):
      if active_field == 0:
        input_a = input_a[:-1]
      else:
        input_b = input_b[:-1]
    return

  if py5.key in "\r\n":
    if mode == "prim":
      calculate_number()
    elif mode in ("ggt", "kgv"):
      calculate_pair()
    return

  if py5.key == " " and mode == "prim":
    if number is not None and current_step < len(factor_steps):
      current_step += 1
    return

  if py5.key in "0123456789":
    if mode == "prim" and len(input_text) < 10:
      input_text += py5.key
    elif mode in ("ggt", "kgv"):
      if active_field == 0 and len(input_a) < 9:
        input_a += py5.key
      elif active_field == 1 and len(input_b) < 9:
        input_b += py5.key


py5.run_sketch()