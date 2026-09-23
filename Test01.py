import py5

input_state = "NUM1"
typed_string = ""

num1 = None
num2 = None
result_ggt = None
current_istep = 0
max_steps = 0
tree_root = None


class FactorNode:

  def __init__(self, value, x, y, step):
    self.value = value
    self.x = x
    self.y = y
    self.left = None
    self.right = None
    self.step = step
    self.is_prime = True


def create_tree(n, x, y, dx, current_step_ptr):
  node = FactorNode(n, x, y, current_step_ptr[0])
  d = 2
  while d * d <= n:
    if n % d == 0:
      node.is_prime = False
      remainder = n // d

      # Linker Ast (Primfaktor-Teiler)
      current_step_ptr[0] += 1
      node.left = FactorNode(d, x - dx, y + 70, current_step_ptr[0])

      # Rechter Ast (Verbleibender Rest)
      node.right = create_tree(
          remainder, x + dx, y + 70, dx * 0.7, current_step_ptr
      )
      break
    d += 1
  return node


def count_nodes(node):
  if not node:
    return 0
  return 1 + count_nodes(node.left) + count_nodes(node.right)


def gcd(a, b):
  while b:
    a, b = b, a % b
  return a


def setup():
  py5.size(1000, 700)
  py5.text_size(16)
  py5.text_align(py5.CENTER, py5.CENTER)


def draw_tree(node, max_step):
  if not node or node.step > max_step:
    return

  # Verbindungslinien zeichnen
  if node.left and node.left.step <= max_step:
    py5.stroke(100, 180, 255)
    py5.stroke_weight(2)
    py5.line(node.x, node.y, node.left.x, node.left.y)
    draw_tree(node.left, max_step)

  if node.right and node.right.step <= max_step:
    py5.stroke(100, 180, 255)
    py5.stroke_weight(2)
    py5.line(node.x, node.y, node.right.x, node.right.y)
    draw_tree(node.right, max_step)

  # Knoten zeichnen
  py5.stroke(255)
  py5.stroke_weight(2)
  if node.is_prime:
    py5.fill(40, 160, 90)  # Primzahl = Grün
  else:
    py5.fill(30, 100, 200)  # Zerlegbar = Blau

  py5.ellipse(node.x, node.y, 50, 50)
  py5.fill(255)
  py5.text(str(node.value), node.x, node.y)


def draw():
  py5.background(20)

  if input_state == "NUM1":
    py5.text_align(py5.LEFT, py5.BASELINE)
    py5.fill(255)
    py5.text("Gib die ERSTE Zahl ein und drücke ENTER:", 50, 100)
    py5.fill(0, 255, 0)
    py5.text(f"{typed_string}_", 50, 140)

  elif input_state == "NUM2":
    py5.text_align(py5.LEFT, py5.BASELINE)
    py5.fill(255)
    py5.text(
        "Gib die ZWEITE Zahl ein (für den ggT) und drücke ENTER:", 50, 100
    )
    py5.fill(0, 255, 0)
    py5.text(f"{typed_string}_", 50, 140)

  else:  # IDLE
    py5.text_align(py5.LEFT, py5.BASELINE)
    py5.fill(255)
    py5.text(f"Zahl: {num1}", 50, 40)
    if num2 is not None:
      py5.text(f"Zweite Zahl: {num2} | ggT({num1}, {num2}) = {result_ggt}", 50, 70)
      py5.text(
          "Steuerung: [Z] Zweite Zahl | [N] Neu starten | [Klick] Nächster"
          " Schritt",
          50,
          100,
      )
    else:
      py5.text(
          "Steuerung: [Z] Zweite Zahl | [N] Neu starten | [Klick] Nächster"
          " Schritt",
          50,
          70,
      )

    if tree_root:
      draw_tree(tree_root, current_istep)


def mouse_pressed():
  global current_istep, max_steps
  if input_state == "IDLE" and tree_root:
    if current_istep < max_steps:
      current_istep += 1


def key_pressed():
  global input_state, typed_string, num1, num2, result_ggt, current_istep, tree_root, max_steps

  if input_state in ["NUM1", "NUM2"]:
    if py5.key in "0123456789":
      typed_string += py5.key
    elif py5.key == "\n" or py5.key == "\r":
      if typed_string:
        val = int(typed_string)
        if input_state == "NUM1":
          num1 = val
          step_ptr = [0]
          tree_root = create_tree(num1, 500, 150, 200, step_ptr)
          max_steps = count_nodes(tree_root) - 1
          current_istep = 0
          input_state = "IDLE"
        else:
          num2 = val
          result_ggt = gcd(num1, num2)
          input_state = "IDLE"
        typed_string = ""
    elif py5.key == chr(8) or py5.key == "\x7f":
      typed_string = typed_string[:-1]

  elif input_state == "IDLE":
    if py5.key in ["z", "Z"]:
      input_state = "NUM2"
      typed_string = ""
    elif py5.key in ["n", "N"]:
      num1 = None
      num2 = None
      result_ggt = None
      current_istep = 0
      max_steps = 0
      tree_root = None
      input_state = "NUM1"
      typed_string = ""


py5.run_sketch()