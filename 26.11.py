import py5   # Bibliothek für Grafik, Fenster und Interaktion (Maus und Tastatur)
import math  # Standard-Bibliothek für mathematische Funktionen (z.B. math.gcd für den ggT)
from collections import Counter  # Zählt, wie oft jeder Primfaktor in einer Zahl vorkommt

# ==============================================================================
# 1. GLOBALE VARIABLEN & ZUSTAND DER ANWENDUNG
# ==============================================================================

# Speichert, welche Seite aktuell angezeigt wird: "menu", "prim", "ggt" oder "kgv"
mode = "menu"

# Matte Farbpalette im RGB-Format: (Rot, Grün, Blau) mit Werten von 0 bis 255
BG_MAIN = (245, 246, 248)        # Warmes Hellgrau als Fensterhintergrund
CARD_BG = (255, 255, 255)        # Mattes Weiss für Karten und Eingabefelder
BORDER_SOFT = (220, 225, 232)    # Dezente Rahmenfarbe
TEXT_DARK = (44, 51, 63)         # Weiches Anthrazit für gut lesbaren Text
TEXT_MUTED = (115, 124, 138)     # Ruhiges Graublau für Hinweise und Untertitel

# Themenfarben: jeweils eine kräftigere Hauptfarbe und ein heller Pastellton für Banner
THEME_PRIM = (102, 149, 178)     # Mattes Taubenblau (Primfaktorzerlegung)
THEME_PRIM_LIGHT = (234, 242, 247)

THEME_GGT = (104, 154, 132)      # Mattes Salbeigrün (ggT)
THEME_GGT_LIGHT = (234, 244, 239)

THEME_KGV = (144, 122, 168)      # Mattes Lavendel (kgV)
THEME_KGV_LIGHT = (242, 238, 247)

BTN_NEUTRAL = (228, 232, 238)    # Neutrales Hellgrau für sekundäre Buttons

# Aktuelle Layout-Geometrie (wird pro Frame dynamisch an die Fenstergrösse angepasst)
layout = {}

# Animationszustände für fliessende Übergänge (60 FPS)
hover_states = {}                # Speichert sanfte Hover-Werte (0.0 bis 1.0) je UI-Element
page_anim = 1.0                  # Seitenübergang: blendet Inhalte sanft ein (0.0 -> 1.0)
result_anim = 1.0                # Gestaffelte Einblendung der Ergebnisse bei ggT/kgV
shake_anim = 0.0                 # Kurzes visuelles Wackeln bei ungültiger Eingabe

# Variablen für die Unterseite "Primfaktorzerlegung"
input_text = ""                  # Aktuell eingetippte Ziffern als Text (String)
number = None                    # Die bestätigte Zahl als Ganzzahl (Integer)
current_tree = None              # Oberster Knoten (Wurzel) des berechneten Faktorbaums
factor_steps = []                # Liste aller verzweigten Knoten für die Schrittanzahl
current_step = 0                 # Zählt, wie viele Zerlegungsebenen aktuell sichtbar sind
tree_scroll_y = 0.0              # Geglättete vertikale Scroll-Verschiebung in Pixeln
target_scroll_y = 0.0            # Ziel-Scrollposition für weiches Ausrollen
max_scroll_y = 0.0               # Maximaler Scrollweg nach unten (0 = kein Scrollen nötig)
is_pressing_tree = False         # True, während die Maustaste im Baumbereich gedrückt wird
has_dragged_tree = False         # True, sobald die Maus beim Gedrückthalten bewegt wurde
press_y = 0                      # Y-Position der Maus beim Klicken (für Drag-Scrolling)
drag_start_scroll = 0.0          # Scroll-Stand zu Beginn des Ziehens
last_tree_sig = None             # Merkt sich letzte Baumgrösse für Live-Skalierung beim Resizen
message = "Gib eine Zahl ein und drücke Enter."

# Variablen für die Unterseiten "ggT" und "kgV"
input_a = ""                     # Eingabetext für Zahl 1
input_b = ""                     # Eingabetext für Zahl 2
active_field = 0                 # Bestimmt, in welches Feld getippt wird: 0 = Zahl 1, 1 = Zahl 2
num_a = None                     # Bestätigte Zahl 1 als Ganzzahl
num_b = None                     # Bestätigte Zahl 2 als Ganzzahl
pair_message = "Gib zwei Zahlen ein (Tab oder Klick zum Wechseln) und drücke Enter."


# ==============================================================================
# 2. DATENSTRUKTUR & ANIMATIONS-HELFER
# ==============================================================================

class FactorNode:
  """Bauplan (Klasse) für einen einzelnen Kreis (Knoten) im Primfaktorbaum."""

  def __init__(self, value, x=0.0, y=0.0, anim=0.0):
    self.value = value    # Der Zahlenwert in diesem Kreis (z.B. 128, 2 oder 64)
    self.x = x            # X-Position (waagrecht) auf dem Bildschirm
    self.y = y            # Y-Position (senkrecht) ohne Scroll-Verschiebung
    self.left = None      # Verweis auf den linken Kindknoten (kleinster Primfaktor)
    self.right = None     # Verweis auf den rechten Kindknoten (Rest nach Division)
    self.anim = anim      # Einblend-Fortschritt (0.0 = unsichtbar, 1.0 = voll sichtbar)


def clamp(val, low, high):
  """Begrenzt einen Zahlenwert sauber auf den Bereich [low, high]."""
  return max(low, min(high, val))


def ease_out_cubic(t):
  """Sanfte Abbremskurve für weiche Bewegungen (t zwischen 0.0 und 1.0)."""
  t = clamp(t, 0.0, 1.0)
  return 1.0 - (1.0 - t) ** 3


def ease_out_back(t):
  """Leicht federnde Pop-In-Kurve für neu erscheinende Knoten und Badges."""
  t = clamp(t, 0.0, 1.0)
  c1 = 1.70158
  c3 = c1 + 1.0
  return 1.0 + c3 * ((t - 1.0) ** 3) + c1 * ((t - 1.0) ** 2)


def get_hover_amount(key, is_hovered, speed=0.22):
  """Interpoliert den Hover-Zustand eines Buttons oder einer Karte fliessend."""
  current = hover_states.get(key, 0.0)
  target = 1.0 if is_hovered else 0.0
  current += (target - current) * speed
  if abs(target - current) < 0.005:
    current = target
  hover_states[key] = current
  return current


def blend_rgb(col_a, col_b, factor):
  """Mischt zwei RGB-Farben stufenlos anhand von 'factor' (0.0 bis 1.0)."""
  f = clamp(factor, 0.0, 1.0)
  return (
      int(col_a[0] + (col_b[0] - col_a[0]) * f),
      int(col_a[1] + (col_b[1] - col_a[1]) * f),
      int(col_a[2] + (col_b[2] - col_a[2]) * f),
  )


# ==============================================================================
# 3. START-KONFIGURATION & DYNAMISCHES LAYOUT (SKALIERBAR)
# ==============================================================================

def setup():
  # Öffnet das Fenster in Standardgrösse 1200x800 (Kantenglättung ist in py5 bereits aktiv)
  py5.size(1200, 800)
  try:
    py5.get_surface().set_resizable(True)
  except Exception:
    pass
  py5.text_font(py5.create_font("Verdana", 22))
  py5.text_align(py5.LEFT, py5.CENTER)


def compute_layout():
  """Berechnet alle Positionen und Grössen passend zur aktuellen Fenstergrösse."""
  w = max(860, py5.width)
  h = max(620, py5.height)

  # Proportionaler Skalierungsfaktor relativ zur Referenzgrösse 1200x800
  s = clamp(min(w / 1200.0, h / 800.0), 0.78, 1.45)

  margin_x = max(32.0, w * 0.042)
  content_w = w - 2.0 * margin_x
  header_h = 72.0 * s
  banner_y = header_h + 16.0 * s
  banner_h = 88.0 * s
  controls_y = banner_y + banner_h + 16.0 * s
  control_h = 48.0 * s
  status_y = controls_y + control_h + 20.0 * s

  # Baum-Bereich (Primfaktorzerlegung)
  footer_h = 50.0 * s
  footer_y = h - footer_h - 18.0 * s
  tree_y = status_y + 18.0 * s
  tree_h = max(220.0, footer_y - tree_y - 14.0 * s)
  tree_header_h = 40.0 * s
  tree_start_y = tree_y + tree_header_h + 46.0 * s
  level_dy = 92.0 * s

  # Ergebniskarte (ggT und kgV)
  result_y = status_y + 18.0 * s
  result_h = max(330.0, h - result_y - 20.0 * s)

  return {
      "w": w,
      "h": h,
      "s": s,
      "margin_x": margin_x,
      "content_w": content_w,
      "header_h": header_h,
      "banner_y": banner_y,
      "banner_h": banner_h,
      "controls_y": controls_y,
      "control_h": control_h,
      "status_y": status_y,
      "footer_y": footer_y,
      "footer_h": footer_h,
      "tree_x": margin_x,
      "tree_y": tree_y,
      "tree_w": content_w,
      "tree_h": tree_h,
      "tree_header_h": tree_header_h,
      "tree_start_y": tree_start_y,
      "level_dy": level_dy,
      "result_y": result_y,
      "result_h": result_h,
  }


# ==============================================================================
# 4. MATHEMATISCHE HILFSFUNKTIONEN
# ==============================================================================

def is_prime(value):
  """Prüft, ob 'value' eine Primzahl ist (nur durch 1 und sich selbst teilbar)."""
  if value < 2:
    return False
  divisor = 2
  while divisor * divisor <= value:
    if value % divisor == 0:
      return False
    divisor += 1
  return True


def smallest_factor(value):
  """Sucht den kleinsten Teiler (grösser als 1) einer Zahl."""
  divisor = 2
  while divisor * divisor <= value:
    if value % divisor == 0:
      return divisor
    divisor += 1
  return value


def build_factor_tree(value, is_root=True):
  """Baut rekursiv den gesamten Faktorbaum für 'value' auf."""
  node = FactorNode(value, anim=1.0 if is_root else 0.0)
  if not is_prime(value):
    factor = smallest_factor(value)
    node.left = build_factor_tree(factor, is_root=False)
    node.right = build_factor_tree(value // factor, is_root=False)
  return node


def collect_steps(node):
  """Durchläuft den Baum und sammelt alle verzweigten Knoten."""
  if node.left is None:
    return
  factor_steps.append(node)
  collect_steps(node.left)
  collect_steps(node.right)


def get_prime_factors(value):
  """Zerlegt 'value' in alle Primfaktoren und gibt sie als Liste zurück (z.B. [2, 2, 3])."""
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
  """Wandelt eine Zahlenliste wie [2, 2, 3] in den Text '2 × 2 × 3' um."""
  if not factors:
    return "1"
  return " × ".join(str(f) for f in factors)


def get_highlighted_factor_masks(factors_a, factors_b, current_mode):
  """Markiert diejenigen Primfaktoren, die für ggT oder kgV ausgewählt werden."""
  counts_a = Counter(factors_a)
  counts_b = Counter(factors_b)
  all_primes = sorted(counts_a.keys() | counts_b.keys())

  if current_mode == "ggt":
    shared = Counter({p: min(counts_a[p], counts_b[p]) for p in all_primes})
    rem_a = shared.copy()
    rem_b = shared.copy()
    mask_a = []
    for f in factors_a:
      if rem_a[f] > 0:
        mask_a.append(True)
        rem_a[f] -= 1
      else:
        mask_a.append(False)

    mask_b = []
    for f in factors_b:
      if rem_b[f] > 0:
        mask_b.append(True)
        rem_b[f] -= 1
      else:
        mask_b.append(False)
    return mask_a, mask_b

  else:
    pick_a = Counter()
    pick_b = Counter()
    for p in all_primes:
      if counts_a[p] >= counts_b[p]:
        pick_a[p] = counts_a[p]
      else:
        pick_b[p] = counts_b[p]

    mask_a = []
    for f in factors_a:
      if pick_a[f] > 0:
        mask_a.append(True)
        pick_a[f] -= 1
      else:
        mask_a.append(False)

    mask_b = []
    for f in factors_b:
      if pick_b[f] > 0:
        mask_b.append(True)
        pick_b[f] -= 1
      else:
        mask_b.append(False)
    return mask_a, mask_b


def get_derivation_steps(a, b, current_mode, result):
  """Erzeugt die schriftliche Herleitung für ggT oder kgV aus den Primfaktorzerlegungen."""
  counts_a = Counter(get_prime_factors(a))
  counts_b = Counter(get_prime_factors(b))
  all_primes = sorted(counts_a.keys() | counts_b.keys())

  if current_mode == "ggt":
    shared = []
    for p in all_primes:
      shared.extend([p] * min(counts_a[p], counts_b[p]))

    rule = (
        "1. Regel: Markiere alle Primfaktoren, die in beiden Zahlen gleichzeitig "
        "vorkommen (farbig hervorgehoben), und multipliziere sie."
    )
    if shared:
      selection = f"2. Gemeinsame Primfaktoren: {format_factors(shared)}"
      calculation = f"3. Schriftliche Rechnung: ggT({a}, {b}) = {format_factors(shared)} = {result}"
    else:
      selection = "2. Gemeinsame Primfaktoren: keine (die beiden Zahlen sind teilerfremd)"
      calculation = f"3. Schriftliche Rechnung: ggT({a}, {b}) = 1"

  else:
    combined = []
    max_details = []
    for p in all_primes:
      max_count = max(counts_a[p], counts_b[p])
      combined.extend([p] * max_count)
      max_details.append(f"{p} (max. {max_count}×)")

    rule = (
        "1. Regel: Nimm jeden vorkommenden Primfaktor so oft, wie er maximal in "
        "einer der beiden Zahlen steckt (farbig markiert), und multipliziere sie."
    )
    if combined:
      selection = f"2. Höchste Anzahl je Primfaktor: {', '.join(max_details)}"
      calculation = f"3. Schriftliche Rechnung: kgV({a}, {b}) = {format_factors(combined)} = {result}"
    else:
      selection = "2. Höchste Anzahl je Primfaktor: keine"
      calculation = f"3. Schriftliche Rechnung: kgV({a}, {b}) = 1"

  return rule, selection, calculation


def count_leaves(node):
  """Zählt rekursiv, wie viele Endpunkte (Blätter) unterhalb eines Knotens hängen."""
  if node is None:
    return 0
  if node.left is None and node.right is None:
    return 1
  return count_leaves(node.left) + count_leaves(node.right)


def get_visible_max_y(node, reveal_step, default_y):
  """Ermittelt die tiefste Y-Position aller aktuell aufgedeckten Kreise im Baum."""
  if node is None:
    return default_y

  max_y = node.y
  if reveal_step > 0:
    if node.left is not None:
      max_y = max(max_y, get_visible_max_y(node.left, reveal_step - 1, default_y))
    if node.right is not None:
      max_y = max(max_y, get_visible_max_y(node.right, reveal_step - 1, default_y))
  return max_y


def get_tree_node_diameter(tree_w, s):
  """Berechnet den optimalen Kreisdurchmesser abhängig von Baumbreite und Blattanzahl."""
  base_d = 56.0 * s
  if current_tree is None:
    return base_d
  leaves = max(1, count_leaves(current_tree))
  max_fit_d = (tree_w - 70.0 * s) / (leaves * 1.16)
  return clamp(min(base_d, max_fit_d), 28.0, 66.0)


def get_tree_max_scroll(tree_y, tree_h, tree_start_y, node_d):
  """Berechnet den maximalen Scrollweg nach unten für den Faktorbaum."""
  if current_tree is None:
    return 0.0

  content_bottom = get_visible_max_y(current_tree, current_step, tree_start_y) + (node_d * 0.5) + 28.0
  viewport_bottom = tree_y + tree_h
  return max(0.0, content_bottom - viewport_bottom)


# ==============================================================================
# 5. ZUSTAND ZURÜCKSETZEN & BERECHNUNGEN STARTEN
# ==============================================================================

def reset_mode(new_mode):
  """Wechselt die Unterseite und startet eine sanfte Seiten-Animation."""
  global mode, page_anim, result_anim, shake_anim
  global input_text, number, current_tree, factor_steps, current_step, message
  global tree_scroll_y, target_scroll_y, max_scroll_y, is_pressing_tree, has_dragged_tree, last_tree_sig
  global input_a, input_b, active_field, num_a, num_b, pair_message

  mode = new_mode
  page_anim = 0.0
  result_anim = 0.0
  shake_anim = 0.0

  input_text = ""
  number = None
  current_tree = None
  factor_steps = []
  current_step = 0
  tree_scroll_y = 0.0
  target_scroll_y = 0.0
  max_scroll_y = 0.0
  is_pressing_tree = False
  has_dragged_tree = False
  last_tree_sig = None
  message = "Gib eine Zahl ein und drücke Enter."

  input_a = ""
  input_b = ""
  active_field = 0
  num_a = None
  num_b = None
  pair_message = "Gib zwei Zahlen ein (Tab oder Klick zum Wechseln) und drücke Enter."


def calculate_number():
  """Liest die eingegebene Zahl bei der Primfaktorzerlegung ein und baut den Baum."""
  global number, current_tree, factor_steps, current_step, message
  global tree_scroll_y, target_scroll_y, max_scroll_y, last_tree_sig, shake_anim

  if not input_text:
    message = "Bitte zuerst eine Zahl eingeben."
    shake_anim = 1.0
    return

  candidate = int(input_text)
  if candidate < 2:
    number = None
    current_tree = None
    factor_steps = []
    tree_scroll_y = 0.0
    target_scroll_y = 0.0
    max_scroll_y = 0.0
    last_tree_sig = None
    shake_anim = 1.0
    message = "Bitte eine ganze Zahl grösser als 1 eingeben."
    return

  number = candidate
  factor_steps = []
  current_step = 0
  tree_scroll_y = 0.0
  target_scroll_y = 0.0
  last_tree_sig = None
  current_tree = build_factor_tree(number, is_root=True)
  collect_steps(current_tree)

  if is_prime(number):
    message = f"{number} ist bereits eine Primzahl."
  else:
    message = "Klicke ins Baum-Feld oder drücke Leertaste für den nächsten Schritt (Scrollen: Mausrad / ↑↓)."


def advance_prim_step():
  """Deckt die nächste Ebene im Faktorbaum auf und scrollt sanft mit."""
  global current_step, target_scroll_y, max_scroll_y

  if number is not None and current_step < len(factor_steps):
    current_step += 1
    s = layout["s"]
    node_d = get_tree_node_diameter(layout["tree_w"], s)
    max_scroll_y = get_tree_max_scroll(layout["tree_y"], layout["tree_h"], layout["tree_start_y"], node_d)
    target_scroll_y = -max_scroll_y


def calculate_pair():
  """Liest beide Zahlen für ggT oder kgV ein und startet die Ergebnis-Animation."""
  global num_a, num_b, pair_message, result_anim, shake_anim

  if not input_a or not input_b:
    pair_message = "Bitte beide Zahlen eingeben."
    num_a = None
    num_b = None
    shake_anim = 1.0
    return

  a = int(input_a)
  b = int(input_b)

  if a < 1 or b < 1:
    pair_message = "Bitte nur ganze Zahlen grösser als 0 eingeben."
    num_a = None
    num_b = None
    shake_anim = 1.0
    return

  num_a = a
  num_b = b
  result_anim = 0.0
  pair_message = "Berechnung abgeschlossen:"


# ==============================================================================
# 6. HAUPT-ZEICHENSCHLEIFE (WIRD CA. 60-MAL PRO SEKUNDE AUSGEFÜHRT)
# ==============================================================================

def update_animations():
  """Aktualisiert alle laufenden UI- und Baum-Animationen pro Frame."""
  global page_anim, result_anim, shake_anim, tree_scroll_y

  if page_anim < 1.0:
    page_anim = min(1.0, page_anim + 0.065)

  if result_anim < 1.0:
    result_anim = min(1.0, result_anim + 0.05)

  if shake_anim > 0.0:
    shake_anim = max(0.0, shake_anim - 0.06)

  # Weiches Ausrollen der Scroll-Verschiebung im Faktorbaum
  if abs(target_scroll_y - tree_scroll_y) > 0.2:
    tree_scroll_y += (target_scroll_y - tree_scroll_y) * 0.16
  else:
    tree_scroll_y = target_scroll_y


def draw():
  global layout
  layout = compute_layout()
  update_animations()

  py5.background(*BG_MAIN)

  # Sanftes Einblenden und Hochgleiten beim Seitenwechsel
  ease_p = ease_out_cubic(page_anim)
  slide_offset = (1.0 - ease_p) * 16.0 * layout["s"]

  py5.push_matrix()
  py5.translate(0, slide_offset)

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

  py5.pop_matrix()


# ==============================================================================
# 7. WIEDERVERWENDBARE UI-BAUSTEINE (MIT SCHATTEN, HOVER & SKALIERUNG)
# ==============================================================================

def draw_soft_shadow(x, y, w, h, radius, intensity=14):
  """Zeichnet einen weichen, mehrstufigen Schatten unter Karten und Buttons."""
  py5.no_stroke()
  py5.fill(30, 41, 59, int(intensity * 0.45))
  py5.rect(x, y + 4, w, h, radius)
  py5.fill(30, 41, 59, int(intensity * 0.7))
  py5.rect(x + 1, y + 2, w - 2, h, radius)


def draw_button(btn_id, x, y, w, h, label, bg_color, text_color=(255, 255, 255), font_size=18):
  """Zeichnet einen abgerundeten Button mit fliessendem Hover-Effekt und sanftem Lift."""
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h
  t = get_hover_amount(btn_id, hover)

  lift_y = y - 1.5 * t
  dark_target = (
      max(0, bg_color[0] - 18),
      max(0, bg_color[1] - 18),
      max(0, bg_color[2] - 18),
  )
  current_bg = blend_rgb(bg_color, dark_target, t)

  draw_soft_shadow(x, lift_y, w, h, 10 * layout["s"], intensity=int(10 + 10 * t))

  py5.fill(*current_bg)
  py5.no_stroke()
  py5.rect(x, lift_y, w, h, 10 * layout["s"])

  py5.fill(*text_color)
  py5.text_size(font_size)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(label, x + w / 2.0, lift_y + h / 2.0)
  py5.text_align(py5.LEFT, py5.CENTER)


def draw_menu_card(card_id, x, y, w, h, title, subtitle, accent_color, light_bg):
  """Zeichnet eine skalierbare Auswahlkarte im Hauptmenü mit sanfter Hover-Animation."""
  s = layout["s"]
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h
  t = get_hover_amount(card_id, hover, speed=0.18)

  lift_y = y - 3.0 * t
  fill_col = blend_rgb(CARD_BG, light_bg, t)
  stroke_col = blend_rgb(BORDER_SOFT, accent_color, t)

  draw_soft_shadow(x, lift_y, w, h, 14 * s, intensity=int(12 + 14 * t))

  py5.fill(*fill_col)
  py5.stroke(*stroke_col)
  py5.stroke_weight(1.5 + 0.8 * t)
  py5.rect(x, lift_y, w, h, 14 * s)

  bar_w = (10.0 + 4.0 * t) * s
  py5.no_stroke()
  py5.fill(*accent_color)
  py5.rect(x, lift_y, bar_w, h, 14 * s, 0, 0, 14 * s)

  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_DARK)
  py5.text_size(21 * s)
  py5.text(title, x + 32 * s + 3 * t, lift_y + h * 0.36)

  py5.fill(*TEXT_MUTED)
  py5.text_size(14.5 * s)
  py5.text(subtitle, x + 32 * s + 3 * t, lift_y + h * 0.68)


def draw_header(title, accent_color):
  """Zeichnet die obere Kopfleiste mit Titel, Farbpunkt und Zurück-Button."""
  w = layout["w"]
  s = layout["s"]
  hh = layout["header_h"]
  mx = layout["margin_x"]

  py5.fill(*CARD_BG)
  py5.no_stroke()
  py5.rect(0, 0, w, hh)

  py5.stroke(*BORDER_SOFT)
  py5.stroke_weight(1.5)
  py5.line(0, hh, w, hh)

  py5.no_stroke()
  py5.fill(*accent_color)
  py5.ellipse(mx + 8 * s, hh / 2.0, 14 * s, 14 * s)

  py5.fill(*TEXT_DARK)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(21 * s)
  py5.text(title, mx + 26 * s, hh / 2.0)

  btn_w = 180 * s
  btn_h = 40 * s
  btn_x = w - mx - btn_w
  btn_y = (hh - btn_h) / 2.0
  draw_button("btn_back", btn_x, btn_y, btn_w, btn_h, "Zurück zum Menü", BTN_NEUTRAL, TEXT_DARK, 15.5 * s)


def draw_info_banner(title, theory_text, accent_color, light_bg):
  """Zeichnet den skalierbaren Theorie-Infobanner am oberen Rand der Unterseite."""
  s = layout["s"]
  x = layout["margin_x"]
  y = layout["banner_y"]
  w = layout["content_w"]
  h = layout["banner_h"]

  py5.fill(*light_bg)
  py5.stroke(accent_color[0], accent_color[1], accent_color[2], 95)
  py5.stroke_weight(1.5)
  py5.rect(x, y, w, h, 12 * s)

  py5.no_stroke()
  py5.fill(*accent_color)
  py5.rect(x, y, 8 * s, h, 12 * s, 0, 0, 12 * s)

  py5.text_align(py5.LEFT, py5.TOP)
  py5.fill(*accent_color)
  py5.text_size(15.5 * s)
  py5.text(title, x + 22 * s, y + 11 * s)

  py5.fill(*TEXT_DARK)
  py5.text_size(14.5 * s)
  py5.text(theory_text, x + 22 * s, y + 35 * s, w - 42 * s, h - 40 * s)
  py5.text_align(py5.LEFT, py5.CENTER)


def draw_input_box(box_id, x, y, w, h, prefix, value, placeholder, is_active, accent_color):
  """Zeichnet ein skalierbares Eingabefeld mit weicher Fokus-Farbe und Fehler-Wackeln."""
  s = layout["s"]
  focus_t = get_hover_amount(box_id, is_active, speed=0.25)

  shake_x = 0.0
  if is_active and shake_anim > 0.0:
    shake_x = math.sin(shake_anim * 28.0) * 6.0 * s * shake_anim

  draw_x = x + shake_x
  border_col = blend_rgb(BORDER_SOFT, accent_color, focus_t)

  py5.fill(*CARD_BG)
  py5.stroke(*border_col)
  py5.stroke_weight(1.5 + 0.8 * focus_t)
  py5.rect(draw_x, y, w, h, 10 * s)

  py5.no_stroke()
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(17.5 * s)

  cursor = "|" if (is_active and py5.frame_count % 60 < 30) else ""

  if prefix:
    py5.fill(*TEXT_MUTED)
    py5.text(prefix, draw_x + 15 * s, y + h / 2.0)
    offset = py5.text_width(prefix) + 8 * s
  else:
    offset = 0.0

  if value or is_active:
    py5.fill(*TEXT_DARK)
    py5.text(value + cursor, draw_x + 15 * s + offset, y + h / 2.0)
  else:
    py5.fill(165, 172, 184)
    py5.text(placeholder, draw_x + 15 * s + offset, y + h / 2.0)


def draw_scrollbar():
  """Zeichnet rechts im Baum-Fenster einen skalierbaren Scrollbalken."""
  if max_scroll_y <= 0:
    return

  s = layout["s"]
  tx = layout["tree_x"]
  ty = layout["tree_y"]
  tw = layout["tree_w"]
  th = layout["tree_h"]
  thh = layout["tree_header_h"]

  track_x = tx + tw - 16 * s
  track_y = ty + thh + 10 * s
  track_w = 7 * s
  track_h = th - thh - 20 * s

  py5.no_stroke()
  py5.fill(232, 236, 242)
  py5.rect(track_x, track_y, track_w, track_h, 4 * s)

  total_h = th + max_scroll_y
  thumb_h = max(32 * s, track_h * (th / total_h))
  scroll_ratio = clamp(-tree_scroll_y / max_scroll_y, 0.0, 1.0)
  thumb_y = track_y + (track_h - thumb_h) * scroll_ratio

  py5.fill(*THEME_PRIM)
  py5.rect(track_x, thumb_y, track_w, thumb_h, 4 * s)


def draw_tree_viewport_header():
  """Kennzeichnet den Zeichenbereich explizit als Primfaktorbaum mit skalierbarer Legende."""
  s = layout["s"]
  tx = layout["tree_x"]
  ty = layout["tree_y"]
  tw = layout["tree_w"]
  thh = layout["tree_header_h"]

  py5.no_stroke()
  py5.fill(*CARD_BG)
  py5.rect(tx + 1, ty + 1, tw - 2, thh - 1, 11 * s, 11 * s, 0, 0)

  py5.stroke(*BORDER_SOFT)
  py5.stroke_weight(1)
  py5.line(tx, ty + thh, tx + tw, ty + thh)

  py5.no_stroke()
  py5.fill(*THEME_PRIM)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(14.5 * s)
  py5.text("Darstellung: Primfaktorbaum (Zerlegung von oben nach unten)", tx + 18 * s, ty + thh / 2.0)

  legend_items = [
      (THEME_GGT, "Primzahl (Blatt)"),
      (THEME_PRIM, "Zerlegt"),
      ((218, 223, 230), "Noch zerlegbar"),
  ]
  py5.text_size(12.5 * s)
  cursor_x = tx + tw - 20 * s
  for col, label in legend_items:
    lbl_w = py5.text_width(label)
    cursor_x -= lbl_w
    py5.fill(*TEXT_MUTED)
    py5.text(label, cursor_x, ty + thh / 2.0)
    cursor_x -= 14 * s
    py5.fill(*col)
    py5.ellipse(cursor_x, ty + thh / 2.0, 11 * s, 11 * s)
    cursor_x -= 22 * s


# ==============================================================================
# 8. ZEICHENFUNKTIONEN FÜR DIE EINZELNEN SEITEN
# ==============================================================================

def draw_menu():
  """Zeichnet den Startbildschirm mit den drei farblich codierten Themenkarten."""
  w = layout["w"]
  h = layout["h"]
  s = layout["s"]

  py5.text_align(py5.CENTER, py5.CENTER)
  py5.fill(*TEXT_DARK)
  py5.text_size(34 * s)
  py5.text("Mathe-Werkzeug", w / 2.0, h * 0.155)

  py5.fill(*TEXT_MUTED)
  py5.text_size(17.5 * s)
  py5.text("Wähle ein Thema per Klick oder Taste (1, 2, 3):", w / 2.0, h * 0.215)

  card_w = min(640 * s, w - 80)
  card_h = 102 * s
  card_x = (w - card_w) / 2.0
  start_y = h * 0.285
  gap_y = 26 * s

  cards = [
      ("menu_0", "1. Primfaktorzerlegung", "Zahlen Schritt für Schritt als Primfaktorbaum zerlegen", THEME_PRIM, THEME_PRIM_LIGHT),
      ("menu_1", "2. Grösster gemeinsamer Teiler (ggT)", "Den grössten gemeinsamen Teiler zweier Zahlen bestimmen", THEME_GGT, THEME_GGT_LIGHT),
      ("menu_2", "3. Kleinstes gemeinsames Vielfaches (kgV)", "Das kleinste gemeinsame Vielfache zweier Zahlen finden", THEME_KGV, THEME_KGV_LIGHT),
  ]

  for idx, (cid, title, sub, acc, lbg) in enumerate(cards):
    cy = start_y + idx * (card_h + gap_y)
    draw_menu_card(cid, card_x, cy, card_w, card_h, title, sub, acc, lbg)


def position_tree(node, left, right, y, dy):
  """Berechnet rekursiv die X- und Y-Koordinaten jedes Kreises im Faktorbaum."""
  if node is None:
    return

  node.x = (left + right) / 2.0
  node.y = y

  if node.left is not None and node.right is not None:
    left_leaves = count_leaves(node.left)
    total_leaves = count_leaves(node)
    split = left + (right - left) * (left_leaves / total_leaves)
    position_tree(node.left, left, split, y + dy, dy)
    position_tree(node.right, split, right, y + dy, dy)


def draw_curved_branch(x1, y1, x2, y2, progress, s):
  """Zeichnet einen geschwungenen Ast, der sanft vom Eltern- zum Kindknoten wächst."""
  t = ease_out_cubic(progress)
  cur_x2 = x1 + (x2 - x1) * t
  cur_y2 = y1 + (y2 - y1) * t
  mid_y = y1 + (cur_y2 - y1) * 0.52

  py5.no_fill()
  py5.stroke(176, 185, 198, int(255 * t))
  py5.stroke_weight(2.2 * s)
  py5.bezier(x1, y1, x1, mid_y, cur_x2, mid_y, cur_x2, cur_y2)


def draw_factor_node(node, reveal_step, offset_y, node_d, s):
  """Zeichnet den Faktorbaum rekursiv mit Pop-In- und Astwachstums-Animation."""
  if node is None:
    return

  if node.anim < 1.0:
    node.anim = min(1.0, node.anim + 0.065)

  pop_scale = ease_out_back(node.anim)
  alpha = int(255 * clamp(node.anim * 1.4, 0.0, 1.0))
  draw_y = node.y + offset_y

  child_anim_avg = 0.0
  if node.left is not None and node.right is not None and reveal_step > 0:
    if node.left.anim < 1.0:
      node.left.anim = min(1.0, node.left.anim + 0.065)
    if node.right.anim < 1.0:
      node.right.anim = min(1.0, node.right.anim + 0.065)

    draw_curved_branch(node.x, draw_y, node.left.x, node.left.y + offset_y, node.left.anim, s)
    draw_curved_branch(node.x, draw_y, node.right.x, node.right.y + offset_y, node.right.anim, s)
    child_anim_avg = (node.left.anim + node.right.anim) * 0.5

  if is_prime(node.value):
    fill_col = THEME_GGT
    text_col = (255, 255, 255)
  elif reveal_step > 0:
    fill_col = blend_rgb((218, 223, 230), THEME_PRIM, child_anim_avg)
    text_col = blend_rgb(TEXT_DARK, (255, 255, 255), child_anim_avg)
  else:
    fill_col = (218, 223, 230)
    text_col = TEXT_DARK

  cur_d = node_d * pop_scale

  py5.no_stroke()
  py5.fill(30, 41, 59, int(20 * (alpha / 255.0)))
  py5.ellipse(node.x, draw_y + 2.5 * s, cur_d, cur_d)

  py5.fill(fill_col[0], fill_col[1], fill_col[2], alpha)
  py5.stroke(CARD_BG[0], CARD_BG[1], CARD_BG[2], alpha)
  py5.stroke_weight(2.6 * s)
  py5.ellipse(node.x, draw_y, cur_d, cur_d)

  val_str = str(node.value)
  digits = len(val_str)
  digit_factor = 1.0 if digits <= 3 else (0.78 if digits <= 5 else 0.62)
  font_sz = max(10.0, cur_d * 0.34 * digit_factor)

  py5.fill(text_col[0], text_col[1], text_col[2], alpha)
  py5.no_stroke()
  py5.text_size(font_sz)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(val_str, node.x, draw_y)

  if reveal_step > 0:
    draw_factor_node(node.left, reveal_step - 1, offset_y, node_d, s)
    draw_factor_node(node.right, reveal_step - 1, offset_y, node_d, s)


def draw_prim():
  """Zeichnet die skalierbare Unterseite für die Primfaktorzerlegung."""
  global last_tree_sig, max_scroll_y, target_scroll_y

  s = layout["s"]
  mx = layout["margin_x"]
  cy = layout["controls_y"]
  ch = layout["control_h"]
  tx = layout["tree_x"]
  ty = layout["tree_y"]
  tw = layout["tree_w"]
  th = layout["tree_h"]
  thh = layout["tree_header_h"]

  draw_info_banner(
      "Theorie: Was ist ein Primfaktorbaum?",
      "Jede Zahl (ausser 1) lässt sich als Mal-Rechnung aus Primzahlen schreiben. "
      "Im Primfaktorbaum wird die Zahl von oben nach unten schrittweise in Teiler aufgespalten, "
      "bis an allen Ästen nur noch Primzahlen (grüne Blätter) stehen.",
      THEME_PRIM, THEME_PRIM_LIGHT
  )

  inp_w = min(380 * s, layout["content_w"] * 0.42)
  btn_calc_w = 145 * s
  draw_input_box("inp_prim", mx, cy, inp_w, ch, "", input_text, "Zahl eingeben (z.B. 128)...", True, THEME_PRIM)
  draw_button("btn_prim_calc", mx + inp_w + 14 * s, cy, btn_calc_w, ch, "Berechnen", THEME_PRIM, (255, 255, 255), 16.5 * s)

  if number is not None and current_step < len(factor_steps):
    btn_step_x = mx + inp_w + btn_calc_w + 28 * s
    draw_button("btn_prim_step", btn_step_x, cy, 185 * s, ch, "Nächster Schritt", BTN_NEUTRAL, TEXT_DARK, 16.5 * s)

  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_MUTED)
  py5.text_size(15.5 * s)
  py5.text(message, mx, layout["status_y"])

  draw_soft_shadow(tx, ty, tw, th, 12 * s, intensity=12)
  py5.fill(250, 251, 253)
  py5.stroke(*BORDER_SOFT)
  py5.stroke_weight(1.5)
  py5.rect(tx, ty, tw, th, 12 * s)

  draw_tree_viewport_header()

  node_d = get_tree_node_diameter(tw, s)
  if number is not None and current_tree is not None:
    sig = (round(tx, 1), round(tw, 1), round(layout["tree_start_y"], 1), round(layout["level_dy"], 1))
    if sig != last_tree_sig:
      pad = max(36.0 * s, node_d * 0.7)
      position_tree(current_tree, tx + pad, tx + tw - pad - 14 * s, layout["tree_start_y"], layout["level_dy"])
      max_scroll_y = get_tree_max_scroll(ty, th, layout["tree_start_y"], node_d)
      target_scroll_y = clamp(target_scroll_y, -max_scroll_y, 0.0)
      last_tree_sig = sig

    py5.clip(tx + 2, ty + thh + 1, tw - 4, th - thh - 3)
    draw_factor_node(current_tree, current_step, tree_scroll_y, node_d, s)
    py5.no_clip()
    draw_scrollbar()

  if number is not None and number >= 2:
    fy = layout["footer_y"]
    fh = layout["footer_h"]
    draw_soft_shadow(mx, fy, layout["content_w"], fh, 12 * s, intensity=10)
    py5.fill(*CARD_BG)
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1.5)
    py5.rect(mx, fy, layout["content_w"], fh, 12 * s)

    py5.no_stroke()
    py5.text_align(py5.LEFT, py5.CENTER)
    py5.fill(*TEXT_MUTED)
    py5.text_size(16.5 * s)
    label_txt = "Primfaktorzerlegung:"
    py5.text(label_txt, mx + 22 * s, fy + fh / 2.0)

    py5.fill(*THEME_GGT)
    py5.text_size(19 * s)
    offset_x = py5.text_width(label_txt) + 16 * s
    py5.text(f"{number} = " + format_factors(get_prime_factors(number)), mx + 22 * s + offset_x, fy + fh / 2.0)


def draw_factor_pills(start_x, center_y, max_x, factors, mask, accent_color, anim_t, s):
  """Zeichnet Primfaktoren als grafische Badges und hebt ausgewählte Faktoren farbig hervor."""
  if not factors:
    return

  if len(factors) > 15 or (max_x - start_x) < 180 * s:
    py5.fill(*TEXT_DARK)
    py5.text_size(16.5 * s)
    py5.text_align(py5.LEFT, py5.CENTER)
    py5.text(format_factors(factors), start_x, center_y)
    return

  cx = start_x
  pill_h = 28 * s
  py5.text_size(15 * s)

  for idx, (f, is_hl) in enumerate(zip(factors, mask)):
    item_t = clamp((anim_t - idx * 0.04) * 2.2, 0.0, 1.0)
    scale = ease_out_back(item_t)
    alpha = int(255 * item_t)

    txt = str(f)
    txt_w = py5.text_width(txt)
    pill_w = max(28 * s, txt_w + 16 * s)

    if cx + pill_w > max_x:
      break

    bg = accent_color if is_hl else (238, 241, 246)
    fg = (255, 255, 255) if is_hl else TEXT_MUTED

    cur_w = pill_w * scale
    cur_h = pill_h * scale
    px = cx + (pill_w - cur_w) / 2.0
    py = center_y - cur_h / 2.0

    py5.no_stroke()
    py5.fill(bg[0], bg[1], bg[2], alpha)
    py5.rect(px, py, cur_w, cur_h, 7 * s)

    py5.fill(fg[0], fg[1], fg[2], alpha)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(txt, cx + pill_w / 2.0, center_y)

    cx += pill_w + 6 * s

    if idx < len(factors) - 1 and cx + 18 * s < max_x:
      py5.fill(TEXT_MUTED[0], TEXT_MUTED[1], TEXT_MUTED[2], alpha)
      py5.text_align(py5.CENTER, py5.CENTER)
      py5.text("×", cx + 6 * s, center_y)
      cx += 18 * s

  py5.text_align(py5.LEFT, py5.CENTER)


def draw_ggt_kgv():
  """Zeichnet die skalierbare Unterseite für ggT oder kgV mit visueller & schriftlicher Herleitung."""
  s = layout["s"]
  mx = layout["margin_x"]
  cw = layout["content_w"]
  cy = layout["controls_y"]
  ch = layout["control_h"]

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

  btn_w = 160 * s
  gap = 16 * s
  field_w = (cw - btn_w - 2 * gap) / 2.0

  draw_input_box("inp_a", mx, cy, field_w, ch, "Zahl 1:", input_a, "z.B. 24", active_field == 0, accent)
  draw_input_box("inp_b", mx + field_w + gap, cy, field_w, ch, "Zahl 2:", input_b, "z.B. 36", active_field == 1, accent)
  draw_button("btn_pair_calc", mx + 2 * (field_w + gap), cy, btn_w, ch, "Berechnen", accent, (255, 255, 255), 16.5 * s)

  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_MUTED)
  py5.text_size(15.5 * s)
  py5.text(pair_message, mx, layout["status_y"])

  if num_a is not None and num_b is not None:
    greatest = math.gcd(num_a, num_b)
    least = abs(num_a * num_b) // greatest
    result = greatest if mode == "ggt" else least
    op_label = "ggT" if mode == "ggt" else "kgV"

    ry = layout["result_y"]
    rh = layout["result_h"]
    ease_r = ease_out_cubic(result_anim)
    card_slide = (1.0 - ease_r) * 14.0 * s

    py5.push_matrix()
    py5.translate(0, card_slide)

    draw_soft_shadow(mx, ry, cw, rh, 14 * s, intensity=14)
    py5.fill(*CARD_BG)
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1.5)
    py5.rect(mx, ry, cw, rh, 14 * s)

    py5.no_stroke()
    py5.fill(*accent)
    py5.rect(mx, ry, 8 * s, rh, 14 * s, 0, 0, 14 * s)

    inner_x = mx + 30 * s
    inner_right = mx + cw - 28 * s

    py5.text_align(py5.LEFT, py5.CENTER)
    py5.fill(*TEXT_DARK)
    py5.text_size(28 * s)
    py5.text(f"{op_label}({num_a}, {num_b}) = {result}", inner_x, ry + 44 * s)

    line_y = ry + 84 * s
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1)
    py5.line(inner_x, line_y, inner_right, line_y)

    factors_a = get_prime_factors(num_a)
    factors_b = get_prime_factors(num_b)
    mask_a, mask_b = get_highlighted_factor_masks(factors_a, factors_b, mode)

    py5.no_stroke()
    py5.fill(*TEXT_DARK)
    py5.text_size(16.5 * s)
    lbl_a = f"Primfaktorzerlegung von {num_a}:"
    lbl_b = f"Primfaktorzerlegung von {num_b}:"
    label_col_w = max(py5.text_width(lbl_a), py5.text_width(lbl_b)) + 18 * s

    row1_y = line_y + 30 * s
    row2_y = line_y + 68 * s

    py5.text(lbl_a, inner_x, row1_y)
    draw_factor_pills(inner_x + label_col_w, row1_y, inner_right, factors_a, mask_a, accent, result_anim, s)

    py5.text(lbl_b, inner_x, row2_y)
    draw_factor_pills(inner_x + label_col_w, row2_y, inner_right, factors_b, mask_b, accent, result_anim, s)

    box_x = inner_x
    box_y = row2_y + 30 * s
    box_w = inner_right - inner_x
    box_h = max(165 * s, (ry + rh) - box_y - 22 * s)

    py5.fill(*light_bg)
    py5.stroke(accent[0], accent[1], accent[2], 95)
    py5.stroke_weight(1.5)
    py5.rect(box_x, box_y, box_w, box_h, 12 * s)

    py5.no_stroke()
    py5.text_align(py5.LEFT, py5.TOP)
    py5.fill(*accent)
    py5.text_size(16.5 * s)
    py5.text(
        f"Schriftliche Herleitung: Von den Primfaktoren zum {op_label}",
        box_x + 20 * s,
        box_y + 15 * s
    )

    rule_text, selection_text, calc_text = get_derivation_steps(num_a, num_b, mode, result)

    step1_a = int(255 * clamp((result_anim - 0.15) * 2.5, 0.0, 1.0))
    step2_a = int(255 * clamp((result_anim - 0.35) * 2.5, 0.0, 1.0))
    step3_a = int(255 * clamp((result_anim - 0.55) * 2.5, 0.0, 1.0))

    step_area_top = box_y + 46 * s
    step_span = (box_h - 54 * s) / 3.0

    py5.fill(TEXT_DARK[0], TEXT_DARK[1], TEXT_DARK[2], step1_a)
    py5.text_size(14.5 * s)
    py5.text(rule_text, box_x + 20 * s, step_area_top, box_w - 40 * s, step_span + 8 * s)

    py5.fill(TEXT_DARK[0], TEXT_DARK[1], TEXT_DARK[2], step2_a)
    py5.text_size(15.5 * s)
    py5.text(selection_text, box_x + 20 * s, step_area_top + step_span * 1.05, box_w - 40 * s, step_span)

    py5.fill(accent[0], accent[1], accent[2], step3_a)
    py5.text_size(17.5 * s)
    py5.text(calc_text, box_x + 20 * s, step_area_top + step_span * 2.02, box_w - 40 * s, step_span)

    py5.text_align(py5.LEFT, py5.CENTER)
    py5.pop_matrix()


# ==============================================================================
# 9. MAUS- UND TASTATURSTEUERUNG
# ==============================================================================

def mouse_pressed():
  """Wird automatisch aufgerufen, sobald die linke Maustaste gedrückt wird."""
  global active_field, is_pressing_tree, has_dragged_tree, press_y, drag_start_scroll

  w = layout["w"]
  h = layout["h"]
  s = layout["s"]
  mx = layout["margin_x"]
  hh = layout["header_h"]

  if mode == "menu":
    card_w = min(640 * s, w - 80)
    card_h = 102 * s
    card_x = (w - card_w) / 2.0
    start_y = h * 0.285
    gap_y = 26 * s

    if card_x <= py5.mouse_x <= card_x + card_w:
      for idx, target_mode in enumerate(["prim", "ggt", "kgv"]):
        cy = start_y + idx * (card_h + gap_y)
        if cy <= py5.mouse_y <= cy + card_h:
          reset_mode(target_mode)
          return
    return

  btn_w = 180 * s
  btn_h = 40 * s
  btn_x = w - mx - btn_w
  btn_y = (hh - btn_h) / 2.0
  if btn_x <= py5.mouse_x <= btn_x + btn_w and btn_y <= py5.mouse_y <= btn_y + btn_h:
    reset_mode("menu")
    return

  cy = layout["controls_y"]
  ch = layout["control_h"]

  if mode == "prim":
    inp_w = min(380 * s, layout["content_w"] * 0.42)
    btn_calc_w = 145 * s
    calc_x = mx + inp_w + 14 * s

    if calc_x <= py5.mouse_x <= calc_x + btn_calc_w and cy <= py5.mouse_y <= cy + ch:
      calculate_number()
      return

    step_x = mx + inp_w + btn_calc_w + 28 * s
    if (number is not None and current_step < len(factor_steps) and
        step_x <= py5.mouse_x <= step_x + 185 * s and cy <= py5.mouse_y <= cy + ch):
      advance_prim_step()
      return

    tx = layout["tree_x"]
    ty = layout["tree_y"]
    tw = layout["tree_w"]
    th = layout["tree_h"]
    thh = layout["tree_header_h"]
    if tx <= py5.mouse_x <= tx + tw and ty + thh <= py5.mouse_y <= ty + th:
      is_pressing_tree = True
      has_dragged_tree = False
      press_y = py5.mouse_y
      drag_start_scroll = target_scroll_y

  elif mode in ("ggt", "kgv"):
    cw = layout["content_w"]
    btn_w = 160 * s
    gap = 16 * s
    field_w = (cw - btn_w - 2 * gap) / 2.0

    if cy <= py5.mouse_y <= cy + ch:
      if mx <= py5.mouse_x <= mx + field_w:
        active_field = 0
      elif mx + field_w + gap <= py5.mouse_x <= mx + 2 * field_w + gap:
        active_field = 1
      elif mx + 2 * (field_w + gap) <= py5.mouse_x <= mx + cw:
        calculate_pair()


def mouse_dragged():
  """Wird aufgerufen, wenn die Maus bei gedrückter Taste bewegt wird (Scrollen per Ziehen)."""
  global target_scroll_y, tree_scroll_y, has_dragged_tree

  if mode == "prim" and is_pressing_tree and max_scroll_y > 0:
    delta_y = py5.mouse_y - press_y
    if abs(delta_y) > 4:
      has_dragged_tree = True
    new_scroll = clamp(drag_start_scroll + delta_y, -max_scroll_y, 0.0)
    target_scroll_y = new_scroll
    tree_scroll_y = new_scroll


def mouse_released():
  """Wird aufgerufen, sobald die Maustaste wieder losgelassen wird."""
  global is_pressing_tree, has_dragged_tree

  if mode == "prim" and is_pressing_tree:
    if not has_dragged_tree:
      advance_prim_step()
    is_pressing_tree = False
    has_dragged_tree = False


def mouse_wheel(event):
  """Wird aufgerufen, sobald das Mausrad gedreht wird."""
  global target_scroll_y

  if mode == "prim" and max_scroll_y > 0:
    target_scroll_y = clamp(target_scroll_y - event.get_count() * 52.0, -max_scroll_y, 0.0)


def key_pressed():
  """Wird automatisch aufgerufen, sobald eine Taste auf der Tastatur gedrückt wird."""
  global input_text, input_a, input_b, active_field, target_scroll_y

  if mode == "prim" and max_scroll_y > 0:
    if py5.key_code == py5.UP:
      target_scroll_y = clamp(target_scroll_y + 55.0, -max_scroll_y, 0.0)
      return
    elif py5.key_code == py5.DOWN:
      target_scroll_y = clamp(target_scroll_y - 55.0, -max_scroll_y, 0.0)
      return

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
      if active_field == 0 and input_a and not input_b:
        active_field = 1
      else:
        calculate_pair()
    return

  if py5.key == " " and mode == "prim":
    advance_prim_step()
    return

  if py5.key in "0123456789":
    if mode == "prim" and len(input_text) < 8:
      input_text += py5.key
    elif mode in ("ggt", "kgv"):
      if active_field == 0 and len(input_a) < 8:
        input_a += py5.key
      elif active_field == 1 and len(input_b) < 8:
        input_b += py5.key


# ==============================================================================
# 10. PROGRAMM STARTEN
# ==============================================================================

py5.run_sketch()