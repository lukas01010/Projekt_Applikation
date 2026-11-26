import py5
import math

# Zustand der Anwendung: "menu", "prim", "ggt", "kgv"
mode = "menu"

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
pair_message = "Gib zwei Zahlen ein (Tab zum Wechseln) und drücke Enter."


class FactorNode:

  def __init__(self, value, x=0, y=0):
    self.value = value
    self.x = x
    self.y = y
    self.left = None
    self.right = None


def setup():
  py5.size(1200, 800)
  py5.text_font(py5.create_font("Arial", 22))
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
  position_tree(current_tree, 80, 1120, 260)
  collect_steps(current_tree)
  if is_prime(number):
    message = f"{number} ist bereits eine Primzahl."
  else:
    message = "Klicke oder drücke die Leertaste für den nächsten Zerlegungsschritt."


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
  pair_message = "Berechnung erfolgreich."


def draw():
  py5.background(20)

  if mode == "menu":
    draw_menu()
  elif mode == "prim":
    draw_back_button()
    draw_prim()
  elif mode in ("ggt", "kgv"):
    draw_back_button()
    draw_ggt_kgv()


def draw_button(x, y, w, h, label, bg_color=(45, 75, 115)):
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h
  if hover:
    py5.fill(bg_color[0] + 20, bg_color[1] + 20, bg_color[2] + 20)
  else:
    py5.fill(*bg_color)
  py5.no_stroke()
  py5.rect(x, y, w, h, 10)
  py5.fill(255)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(label, x + w / 2, y + h / 2)
  py5.text_align(py5.LEFT, py5.CENTER)


def draw_back_button():
  draw_button(990, 25, 180, 45, "Zurück zum Menü", (70, 70, 85))


def draw_menu():
  py5.fill(255)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text_size(36)
  py5.text("Mathe-Werkzeug: Auswahl", 600, 140)
  py5.text_size(22)

  draw_button(350, 260, 500, 90, "Primfaktorzerlegung", (35, 110, 150))
  draw_button(350, 390, 500, 90, "grössten gemeinsamen Teiler (ggT)", (45, 125, 95))
  draw_button(350, 520, 500, 90, "kleinstes gemeinsames Vielfaches (kgV)", (125, 85, 145))


def position_tree(node, left, right, y):
  if node is None:
    return
  node.x = (left + right) / 2
  node.y = y
  if node.left is not None:
    position_tree(node.left, left, node.x, y + 120)
  if node.right is not None:
    position_tree(node.right, node.x, right, y + 120)


def draw_factor_node(node, reveal_step):
  if node is None:
    return

  if node.left is not None and node.right is not None:
    if reveal_step >= 0:
      py5.stroke(100, 180, 255)
      py5.stroke_weight(2)
      py5.line(node.x, node.y, node.left.x, node.left.y)
      py5.line(node.x, node.y, node.right.x, node.right.y)

  if is_prime(node.value):
    py5.fill(50, 160, 90)
  elif reveal_step > 0:
    py5.fill(45, 105, 170)
  else:
    py5.fill(110, 110, 110)

  py5.stroke(255)
  py5.stroke_weight(2)
  py5.ellipse(node.x, node.y, 60, 60)
  py5.fill(255)
  py5.no_stroke()
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(str(node.value), node.x, node.y)

  if reveal_step > 0:
    draw_factor_node(node.left, reveal_step - 1)
    draw_factor_node(node.right, reveal_step - 1)


def draw_prim():
  py5.fill(255)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(22)
  py5.text("Primfaktorzerlegung", 50, 50)

  py5.fill(35)
  py5.no_stroke()
  py5.rect(50, 100, 830, 55, 10)
  py5.fill(255)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text(input_text + ("_" if py5.is_key_pressed else ""), 65, 127)

  py5.text_align(py5.LEFT, py5.TOP)
  py5.text(message, 50, 175)

  if number is not None:
    if current_tree is not None:
      draw_factor_node(current_tree, current_step)

    py5.text_align(py5.LEFT, py5.CENTER)
    py5.text_size(20)
    if number >= 2:
      py5.text("Primfaktoren: " + format_factors(get_prime_factors(number)),
                50, 720)


def draw_ggt_kgv():
  py5.fill(255)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(22)
  if mode == "ggt":
    py5.text("Grösster gemeinsamer Teiler (ggT)", 50, 50)
  else:
    py5.text("Kleinstes gemeinsames Vielfaches (kgV)", 50, 50)

  py5.fill(35)
  py5.no_stroke()
  py5.rect(50, 120, 420, 55, 10)
  py5.rect(520, 120, 420, 55, 10)
  py5.fill(255)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text("Zahl 1: " + input_a + ("_" if active_field == 0 and py5.is_key_pressed else ""),
           65, 147)
  py5.text("Zahl 2: " + input_b + ("_" if active_field == 1 and py5.is_key_pressed else ""),
           535, 147)

  py5.text_align(py5.LEFT, py5.TOP)
  py5.text(pair_message, 50, 210)

  if num_a is not None and num_b is not None:
    greatest = math.gcd(num_a, num_b)
    py5.text_size(28)
    if mode == "ggt":
      py5.text(f"ggT({num_a}, {num_b}) = {greatest}", 50, 280)
    elif mode == "kgv":
      least = abs(num_a * num_b) // greatest
      py5.text(f"kgV({num_a}, {num_b}) = {least}", 50, 280)


def mouse_pressed():
  global current_step, active_field

  if mode == "menu":
    if 350 <= py5.mouse_x <= 850:
      if 260 <= py5.mouse_y <= 350:
        reset_mode("prim")
      elif 390 <= py5.mouse_y <= 480:
        reset_mode("ggt")
      elif 520 <= py5.mouse_y <= 610:
        reset_mode("kgv")
    return

  if 990 <= py5.mouse_x <= 1170 and 25 <= py5.mouse_y <= 70:
    reset_mode("menu")
    return

  if mode == "prim":
    if number is not None and current_step < len(factor_steps):
      current_step += 1
  elif mode in ("ggt", "kgv"):
    if 50 <= py5.mouse_x <= 470 and 120 <= py5.mouse_y <= 175:
      active_field = 0
    elif 520 <= py5.mouse_x <= 940 and 120 <= py5.mouse_y <= 175:
      active_field = 1


def key_pressed():
  global input_text, input_a, input_b, active_field, current_step

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

  if py5.key and py5.key in "0123456789":
    if mode == "prim":
      input_text += py5.key
    elif mode in ("ggt", "kgv"):
      if active_field == 0:
        input_a += py5.key
      else:
        input_b += py5.key


py5.run_sketch()