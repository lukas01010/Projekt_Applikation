import py5

input_text = ""
number = None
factor_steps = []
current_step = 0
message = "Gib eine Zahl ein und drücke Enter."


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


def calculate_number():
  global number, factor_steps, current_step, message

  if not input_text:
    message = "Bitte zuerst eine Zahl eingeben."
    return

  candidate = int(input_text)
  if candidate < 2:
    number = None
    factor_steps = []
    message = "Bitte eine ganze Zahl größer als 1 eingeben."
    return

  number = candidate
  factor_steps = []
  current_step = 0
  tree = build_factor_tree(number)
  collect_steps(tree)
  if is_prime(number):
    message = f"{number} ist bereits eine Primzahl."
  else:
    message = "Klicke oder drücke die Leertaste für den nächsten Zerlegungsschritt."


def draw():
  py5.background(20)

  py5.fill(255)
  py5.text("Primfaktorzerlegung", 30, 40)
  py5.fill(190)
  py5.text("Zahl:", 30, 90)
  py5.fill(40, 55, 75)
  py5.rect(105, 65, 280, 45, 8)
  py5.fill(255)
  py5.text(input_text, 120, 88)
  py5.fill(170)
  py5.text("Enter = berechnen | Klick/Leertaste = nächster Schritt", 30, 145)
  py5.fill(230)
  py5.text(message, 30, 190)

  if number is None:
    return

  tree = build_factor_tree(number)
  position_tree(tree, 80, 1120, 250)
  draw_tree(tree)
  if current_step >= len(factor_steps) and not is_prime(number):
    factors = get_prime_factors(number)
    py5.fill(100, 220, 150)
    py5.text("Primfaktoren: " + " × ".join(str(factor) for factor in factors), 30, 770)


def count_leaves(node):
  if node.left is None:
    return 1
  return count_leaves(node.left) + count_leaves(node.right)


def position_tree(node, left, right, y):
  node.x = (left + right) / 2
  node.y = y
  if node.left is not None:
    left_leaves = count_leaves(node.left)
    total_leaves = count_leaves(node)
    split = left + (right - left) * left_leaves / total_leaves
    position_tree(node.left, left, split, y + 105)
    position_tree(node.right, split, right, y + 105)


def draw_tree(node):
  expanded = node.left is not None and node in factor_steps[:current_step]

  if expanded:
    py5.stroke(100, 150, 190)
    py5.stroke_weight(3)
    py5.line(node.x, node.y + 25, node.left.x, node.left.y - 25)
    py5.line(node.x, node.y + 25, node.right.x, node.right.y - 25)
    draw_tree(node.left)
    draw_tree(node.right)

  py5.no_stroke()
  if node.left is None:
    py5.fill(45, 150, 105)
  else:
    py5.fill(55, 90, 140)
  py5.ellipse(node.x, node.y, 70, 50)
  py5.fill(255)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(str(node.value), node.x, node.y)
  py5.text_align(py5.LEFT, py5.CENTER)


def mouse_pressed():
  global current_step
  if number is not None and current_step < len(factor_steps):
    current_step += 1


def key_pressed():
  global input_text

  if py5.key == py5.ENTER or py5.key == py5.RETURN:
    try:
      calculate_number()
    except ValueError:
      input_text = ""
      py5.println("Bitte nur Ziffern eingeben.")
  elif py5.key == py5.BACKSPACE:
    input_text = input_text[:-1]
  elif py5.key == " " and number is not None:
    mouse_pressed()
  elif py5.key.isdigit() and len(input_text) < 12:
    input_text += py5.key

py5.run_sketch()