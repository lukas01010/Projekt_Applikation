import py5   # Bibliothek für Grafik, Fenster und Interaktion (Maus und Tastatur)
import math  # Standard-Bibliothek für mathematische Funktionen (z.B. math.gcd für den ggT)

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

# Variablen für die Unterseite "Primfaktorzerlegung"
input_text = ""       # Aktuell eingetippte Ziffern als Text (String)
number = None         # Die bestätigte Zahl als Ganzzahl (Integer), am Anfang noch leer (None)
current_tree = None   # Speichert den obersten Knoten (Wurzel) des berechneten Faktorbaums
factor_steps = []     # Liste aller verzweigten Knoten, um die Anzahl Schritte zu kennen
current_step = 0      # Zählt, wie viele Zerlegungsebenen im Baum aktuell sichtbar sind
message = "Gib eine Zahl ein und drücke Enter."

# Variablen für die Unterseiten "ggT" und "kgV"
input_a = ""          # Eingabetext für Zahl 1
input_b = ""          # Eingabetext für Zahl 2
active_field = 0      # Bestimmt, in welches Feld getippt wird: 0 = Zahl 1, 1 = Zahl 2
num_a = None          # Bestätigte Zahl 1 als Ganzzahl
num_b = None          # Bestätigte Zahl 2 als Ganzzahl
pair_message = "Gib zwei Zahlen ein (Tab oder Klick zum Wechseln) und drücke Enter."


# ==============================================================================
# 2. DATENSTRUKTUR FÜR DEN FAKTORBAUM
# ==============================================================================

class FactorNode:
  """Bauplan (Klasse) für einen einzelnen Kreis (Knoten) im Primfaktorbaum."""

  def __init__(self, value, x=0, y=0):
    # 'self' verweist auf den jeweiligen einzelnen Kreis im Baum
    self.value = value  # Der Zahlenwert in diesem Kreis (z.B. 84, 2 oder 42)
    self.x = x          # X-Position (waagrecht) auf dem Bildschirm
    self.y = y          # Y-Position (senkrecht) auf dem Bildschirm
    self.left = None    # Verweis auf den linken Kindknoten (kleinster Primfaktor)
    self.right = None   # Verweis auf den rechten Kindknoten (Rest nach Division)


# ==============================================================================
# 3. START-KONFIGURATION (WIRD EINMALIG BEIM START AUSGEFÜHRT)
# ==============================================================================

def setup():
  # Öffnet das Zeichenfenster mit 1200 Pixel Breite und 800 Pixel Höhe
  # Hinweis: Der Punkt (0, 0) liegt in py5 immer oben links
  py5.size(1200, 800)
  # Lädt die Schriftart "Verdana" in Standardgrösse 22
  py5.text_font(py5.create_font("Verdana", 22))
  # Setzt die Textausrichtung standardmässig auf linksbündig und vertikal mittig
  py5.text_align(py5.LEFT, py5.CENTER)


# ==============================================================================
# 4. MATHEMATISCHE HILFSFUNKTIONEN
# ==============================================================================

def is_prime(value):
  """Prüft, ob 'value' eine Primzahl ist (nur durch 1 und sich selbst teilbar)."""
  # Zahlen kleiner als 2 (0, 1 und negative Zahlen) sind per Definition keine Primzahlen
  if value < 2:
    return False

  divisor = 2
  # Wir testen mögliche Teiler nur bis zur Wurzel von 'value' (divisor * divisor <= value),
  # weil ein grösserer Teiler immer einen kleineren Partner unterhalb der Wurzel hat
  while divisor * divisor <= value:
    # Der Modulo-Operator (%) berechnet den Rest einer Division
    if value % divisor == 0:
      return False  # Rest 0 heisst: glatt teilbar -> keine Primzahl
    divisor += 1    # Nächsten möglichen Teiler ausprobieren

  return True       # Kein Teiler gefunden -> es ist eine Primzahl


def smallest_factor(value):
  """Sucht den kleinsten Teiler (grösser als 1) einer Zahl."""
  divisor = 2
  while divisor * divisor <= value:
    if value % divisor == 0:
      return divisor  # Der erste gefundene Teiler von unten ist automatisch eine Primzahl
    divisor += 1
  return value        # Falls kein kleinerer Teiler existiert, ist 'value' selbst prim


def build_factor_tree(value):
  """Baut rekursiv (durch Selbstaufruf) den gesamten Faktorbaum für 'value' auf."""
  # Erstellt zuerst den Kreis für die aktuelle Zahl
  node = FactorNode(value)

  # Nur wenn die Zahl noch keine Primzahl ist, wird sie weiter aufgeteilt
  if not is_prime(value):
    factor = smallest_factor(value)                  # Kleinsten Primfaktor finden
    node.left = build_factor_tree(factor)            # Linken Ast mit diesem Primfaktor bauen
    node.right = build_factor_tree(value // factor)  # Rechten Ast mit dem Rest (// = Ganzzahldivision) bauen

  return node


def collect_steps(node):
  """Durchläuft den Baum und sammelt alle Knoten, die noch Kinder haben."""
  # Abbruchbedingung: Wenn es keinen linken Ast gibt, ist der Knoten ein Endpunkt (Blatt)
  if node.left is None:
    return

  factor_steps.append(node)    # Diesen verzweigten Knoten zur Schrittliste hinzufügen
  collect_steps(node.left)     # Rekursiv im linken Teilbaum weitersuchen
  collect_steps(node.right)    # Rekursiv im rechten Teilbaum weitersuchen


def get_prime_factors(value):
  """Zerlegt 'value' in alle Primfaktoren und gibt sie als Liste zurück (z.B. [2, 2, 3])."""
  factors = []
  divisor = 2

  while divisor * divisor <= value:
    # Solange 'value' durch den aktuellen Teiler teilbar ist, diesen mehrfach herausziehen
    while value % divisor == 0:
      factors.append(divisor)  # Gefundenen Primfaktor in die Liste eintragen
      value //= divisor        # Zahl durch diesen Faktor teilen und Ergebnis speichern
    divisor += 1

  # Wenn am Schluss ein Rest grösser als 1 übrig bleibt, ist dieser Rest selbst eine Primzahl
  if value > 1:
    factors.append(value)

  return factors


def format_factors(factors):
  """Wandelt eine Zahlenliste wie [2, 2, 3] in den Text '2 × 2 × 3' um."""
  if not factors:
    return "1"
  # str(f) wandelt jede Zahl in Text um, " × ".join(...) verbindet alle Teile mit Malzeichen
  return " × ".join(str(f) for f in factors)


# ==============================================================================
# 5. ZUSTAND ZURÜCKSETZEN & BERECHNUNGEN STARTEN
# ==============================================================================

def reset_mode(new_mode):
  """Wechselt die Unterseite und setzt alle vorherigen Eingaben sauber zurück."""
  # 'global' erlaubt es dieser Funktion, die Variablen oben ausserhalb zu überschreiben
  global mode, input_text, number, current_tree, factor_steps, current_step, message
  global input_a, input_b, active_field, num_a, num_b, pair_message

  mode = new_mode  # Neuen Modus setzen ("menu", "prim", "ggt" oder "kgv")

  # Werte der Primfaktorzerlegung leeren
  input_text = ""
  number = None
  current_tree = None
  factor_steps = []
  current_step = 0
  message = "Gib eine Zahl ein und drücke Enter."

  # Werte von ggT / kgV leeren
  input_a = ""
  input_b = ""
  active_field = 0
  num_a = None
  num_b = None
  pair_message = "Gib zwei Zahlen ein (Tab oder Klick zum Wechseln) und drücke Enter."


def calculate_number():
  """Liest die eingegebene Zahl bei der Primfaktorzerlegung ein und baut den Baum."""
  global number, current_tree, factor_steps, current_step, message

  # Prüfen, ob überhaupt etwas eingetippt wurde
  if not input_text:
    message = "Bitte zuerst eine Zahl eingeben."
    return

  # Text (String) in eine echte Ganzzahl (Integer) umwandeln
  candidate = int(input_text)

  # Zahlen kleiner als 2 lassen sich nicht in Primfaktoren zerlegen
  if candidate < 2:
    number = None
    current_tree = None
    factor_steps = []
    message = "Bitte eine ganze Zahl grösser als 1 eingeben."
    return

  # Gültige Zahl übernehmen und Startwerte für die Animation vorbereiten
  number = candidate
  factor_steps = []
  current_step = 0
  current_tree = build_factor_tree(number)           # Baumstruktur im Speicher aufbauen
  position_tree(current_tree, 80, 1120, 325)         # Bildschirmkoordinaten für jeden Kreis berechnen
  collect_steps(current_tree)                        # Verzweigungspunkte zählen

  # Passende Rückmeldung für die SuS setzen
  if is_prime(number):
    message = f"{number} ist bereits eine Primzahl."
  else:
    message = "Klicke auf das Feld oder drücke die Leertaste für den nächsten Schritt."


def calculate_pair():
  """Liest beide Zahlen für ggT oder kgV ein und prüft sie auf Gültigkeit."""
  global num_a, num_b, pair_message

  # Abbrechen, falls eines der beiden Felder noch leer ist
  if not input_a or not input_b:
    pair_message = "Bitte beide Zahlen eingeben."
    num_a = None
    num_b = None
    return

  # Beide Eingabetexte in Ganzzahlen umwandeln
  a = int(input_a)
  b = int(input_b)

  # 0 ist für ggT und kgV im Unterricht nicht sinnvoll
  if a < 1 or b < 1:
    pair_message = "Bitte nur ganze Zahlen grösser als 0 eingeben."
    num_a = None
    num_b = None
    return

  num_a = a
  num_b = b
  pair_message = "Berechnung abgeschlossen:"


# ==============================================================================
# 6. HAUPT-ZEICHENSCHLEIFE (WIRD CA. 60-MAL PRO SEKUNDE AUSGEFÜHRT)
# ==============================================================================

def draw():
  # Übermalt das gesamte Fenster mit der Hintergrundfarbe (löscht das vorherige Einzelbild)
  # Der Stern (*) entpackt das Tupel (245, 246, 248) in drei einzelne Zahlen
  py5.background(*BG_MAIN)

  # Entscheidet anhand von 'mode', welche Seite gerade gezeichnet werden soll
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


# ==============================================================================
# 7. WIEDERVERWENDBARE UI-BAUSTEINE (BUTTONS, KARTEN, BANNER, EINGABEFELDER)
# ==============================================================================

def draw_button(x, y, w, h, label, bg_color, text_color=(255, 255, 255), font_size=18):
  """Zeichnet einen abgerundeten Button mit Hover-Effekt (abdunkeln bei Mauskontakt)."""
  # Prüft, ob die Mausposition aktuell innerhalb des Rechtecks (x bis x+w, y bis y+h) liegt
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h

  if hover:
    # Wenn die Maus darüber fährt, jeden Farbkanal um 16 abdunkeln (max(0, ...) verhindert Minuswerte)
    py5.fill(max(0, bg_color[0] - 16), max(0, bg_color[1] - 16), max(0, bg_color[2] - 16))
  else:
    py5.fill(*bg_color)

  py5.no_stroke()                   # Keinen Rand um den Button zeichnen
  py5.rect(x, y, w, h, 10)          # Rechteck mit Eckenradius 10 zeichnen
  py5.fill(*text_color)             # Textfarbe setzen
  py5.text_size(font_size)          # Schriftgrösse setzen
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(label, x + w / 2, y + h / 2)  # Beschriftung genau in die Mitte des Buttons setzen
  py5.text_align(py5.LEFT, py5.CENTER)   # Ausrichtung wieder auf Standard zurücksetzen


def draw_menu_card(x, y, w, h, title, subtitle, accent_color, light_bg):
  """Zeichnet eine grosse Auswahlkarte im Hauptmenü."""
  # Prüft, ob der Mauszeiger auf dieser Karte liegt
  hover = x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h

  # Bei Mauskontakt wird die Karte leicht eingefärbt und bekommt einen farbigen Rahmen
  py5.fill(*(light_bg if hover else CARD_BG))
  py5.stroke(*(accent_color if hover else BORDER_SOFT))
  py5.stroke_weight(2 if hover else 1.5)
  py5.rect(x, y, w, h, 14)

  # Farbiger Akzentstreifen am linken Rand der Karte (nur linke Ecken abgerundet: 14, 0, 0, 14)
  py5.no_stroke()
  py5.fill(*accent_color)
  py5.rect(x, y, 10, h, 14, 0, 0, 14)

  # Haupttitel der Karte zeichnen
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_DARK)
  py5.text_size(22)
  py5.text(title, x + 32, y + 36)

  # Kurze Beschreibung darunter in gedämpfter Farbe zeichnen
  py5.fill(*TEXT_MUTED)
  py5.text_size(15)
  py5.text(subtitle, x + 32, y + 68)


def draw_header(title, accent_color):
  """Zeichnet die obere Kopfleiste mit Titel, Farbpunkt und Zurück-Button."""
  # Weisser Balken über die gesamte Fensterbreite (1200 Pixel)
  py5.fill(*CARD_BG)
  py5.no_stroke()
  py5.rect(0, 0, 1200, 74)

  # Feine Trennlinie am unteren Rand der Kopfleiste
  py5.stroke(*BORDER_SOFT)
  py5.stroke_weight(1.5)
  py5.line(0, 74, 1200, 74)

  # Kleiner farbiger Punkt als visuelles Erkennungszeichen links vom Titel
  py5.no_stroke()
  py5.fill(*accent_color)
  py5.ellipse(58, 37, 14, 14)

  # Seitentitel zeichnen
  py5.fill(*TEXT_DARK)
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(22)
  py5.text(title, 78, 37)

  # Button oben rechts zum Zurückkehren ins Hauptmenü
  draw_button(970, 17, 180, 40, "Zurück zum Menü", BTN_NEUTRAL, TEXT_DARK, 16)


def draw_info_banner(title, theory_text, accent_color, light_bg):
  """Zeichnet den Theorie-Infobanner für die 1. Sek am oberen Rand der Unterseite."""
  x, y, w, h = 50, 92, 1100, 90

  # Pastellfarbener Hintergrund mit halbtransparentem Rahmen (4. Wert = Deckkraft 90)
  py5.fill(*light_bg)
  py5.stroke(accent_color[0], accent_color[1], accent_color[2], 90)
  py5.stroke_weight(1.5)
  py5.rect(x, y, w, h, 12)

  # Farbiger Seitenbalken links
  py5.no_stroke()
  py5.fill(*accent_color)
  py5.rect(x, y, 8, h, 12, 0, 0, 12)

  # Überschrift des Banners oben links in der Box platzieren
  py5.text_align(py5.LEFT, py5.TOP)
  py5.fill(*accent_color)
  py5.text_size(16)
  py5.text(title, x + 24, y + 12)

  # Erklärungstext: Die letzten zwei Parameter (w - 44, h - 42) sorgen dafür,
  # dass py5 den Text automatisch umbricht, bevor er über den Rand hinausragt
  py5.fill(*TEXT_DARK)
  py5.text_size(15)
  py5.text(theory_text, x + 24, y + 38, w - 44, h - 42)

  py5.text_align(py5.LEFT, py5.CENTER)


def draw_input_box(x, y, w, h, prefix, value, placeholder, is_active, accent_color):
  """Zeichnet ein Eingabefeld mit Rahmen, blinkendem Cursor und Platzhaltertext."""
  py5.fill(*CARD_BG)
  if is_active:
    # Aktives Eingabefeld erhält einen dickeren, farbigen Rahmen
    py5.stroke(*accent_color)
    py5.stroke_weight(2.2)
  else:
    # Inaktives Feld erhält einen dünnen grauen Rahmen
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1.5)
  py5.rect(x, y, w, h, 10)

  py5.no_stroke()
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.text_size(18)

  # Blinkender Schreibstrich: 'frame_count % 60 < 30' ist jeweils 30 Frames wahr und 30 Frames falsch
  cursor = "|" if (is_active and py5.frame_count % 60 < 30) else ""

  # Falls ein Vorsatz wie "Zahl 1:" angegeben ist, diesen zuerst zeichnen und Breite messen
  if prefix:
    py5.fill(*TEXT_MUTED)
    py5.text(prefix, x + 16, y + h / 2)
    offset = py5.text_width(prefix) + 8  # Abstand berechnen, damit die Zahl rechts daneben steht
  else:
    offset = 0

  # Wenn bereits Ziffern eingegeben wurden oder das Feld aktiv ist: Zahl + Cursor anzeigen
  if value or is_active:
    py5.fill(*TEXT_DARK)
    py5.text(value + cursor, x + 16 + offset, y + h / 2)
  else:
    # Sonst den hellgrauen Beispieltext (Platzhalter) anzeigen
    py5.fill(165, 172, 184)
    py5.text(placeholder, x + 16 + offset, y + h / 2)


# ==============================================================================
# 8. ZEICHENFUNKTIONEN FÜR DIE EINZELNEN SEITEN
# ==============================================================================

def draw_menu():
  """Zeichnet den Startbildschirm mit den drei Themenkarten."""
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.fill(*TEXT_DARK)
  py5.text_size(34)
  py5.text("Mathe-Werkzeug", 600, 125)

  py5.fill(*TEXT_MUTED)
  py5.text_size(18)
  py5.text("Wähle ein Thema per Klick oder Taste (1, 2, 3):", 600, 170)

  # Drei untereinander angeordnete Auswahlkarten zeichnen
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
  """Berechnet rekursiv die X- und Y-Koordinaten jedes Kreises im Faktorbaum."""
  if node is None:
    return

  # Setzt den aktuellen Knoten horizontal genau in die Mitte zwischen 'left' und 'right'
  node.x = (left + right) / 2
  node.y = y

  # Teilt den horizontalen Platz für die nächste Ebene (95 Pixel tiefer) in linke und rechte Hälfte
  if node.left is not None:
    position_tree(node.left, left, node.x, y + 95)
  if node.right is not None:
    position_tree(node.right, node.x, right, y + 95)


def draw_factor_node(node, reveal_step):
  """Zeichnet den Faktorbaum rekursiv bis zur aktuell freigeschalteten Tiefe."""
  if node is None:
    return

  # Verbindungslinien zu den Kindknoten nur zeichnen, wenn 'reveal_step > 0' ist
  # (damit beim allerersten Schritt noch keine Linien ins Leere zeigen)
  if node.left is not None and node.right is not None and reveal_step > 0:
    py5.stroke(180, 188, 200)
    py5.stroke_weight(2.2)
    py5.line(node.x, node.y, node.left.x, node.left.y)
    py5.line(node.x, node.y, node.right.x, node.right.y)

  # Farbe des Kreises je nach Zustand wählen:
  if is_prime(node.value):
    py5.fill(*THEME_GGT)            # Grün: Endpunkt erreicht (Primzahl)
    text_col = (255, 255, 255)
  elif reveal_step > 0:
    py5.fill(*THEME_PRIM)           # Blau: Zahl wurde bereits weiter zerlegt
    text_col = (255, 255, 255)
  else:
    py5.fill(218, 223, 230)         # Hellgrau: Zahl kann im nächsten Schritt noch zerlegt werden
    text_col = TEXT_DARK

  # Kreis mit weissem Rand zeichnen, damit er sich sauber von den Linien abhebt
  py5.stroke(*CARD_BG)
  py5.stroke_weight(3)
  py5.ellipse(node.x, node.y, 58, 58)

  # Zahlenwert mittig in den Kreis schreiben
  py5.fill(*text_col)
  py5.no_stroke()
  py5.text_size(18)
  py5.text_align(py5.CENTER, py5.CENTER)
  py5.text(str(node.value), node.x, node.y)

  # Mit 'reveal_step - 1' wird pro Ebene nach unten genau ein Schritt heruntergezählt
  if reveal_step > 0:
    draw_factor_node(node.left, reveal_step - 1)
    draw_factor_node(node.right, reveal_step - 1)


def draw_prim():
  """Zeichnet die gesamte Unterseite für die Primfaktorzerlegung."""
  # 1. Theorie-Banner oben
  draw_info_banner(
      "Theorie: Was ist eine Primfaktorzerlegung?",
      "Jede Zahl (ausser 1) lässt sich als Mal-Rechnung aus Primzahlen schreiben. "
      "Primzahlen sind nur durch 1 und sich selbst teilbar (z.B. 2, 3, 5, 7, 11). "
      "Beispiel: 12 = 2 × 2 × 3.",
      THEME_PRIM, THEME_PRIM_LIGHT
  )

  # 2. Eingabefeld und Berechnen-Button
  draw_input_box(50, 200, 380, 48, "", input_text, "Zahl eingeben (z.B. 84)...", True, THEME_PRIM)
  draw_button(445, 200, 145, 48, "Berechnen", THEME_PRIM, (255, 255, 255), 17)

  # 3. Button "Nächster Schritt" nur einblenden, solange der Baum noch nicht fertig aufgedeckt ist
  if number is not None and current_step < len(factor_steps):
    draw_button(605, 200, 185, 48, "Nächster Schritt", BTN_NEUTRAL, TEXT_DARK, 17)

  # 4. Status- und Hinweistext unter dem Eingabefeld
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_MUTED)
  py5.text_size(16)
  py5.text(message, 50, 268)

  # 5. Faktorbaum und untere Ergebniskarte zeichnen, sobald eine gültige Zahl vorliegt
  if number is not None:
    if current_tree is not None:
      draw_factor_node(current_tree, current_step)

    if number >= 2:
      # Weisse Ergebniskarte am unteren Bildschirmrand
      py5.fill(*CARD_BG)
      py5.stroke(*BORDER_SOFT)
      py5.stroke_weight(1.5)
      py5.rect(50, 725, 1100, 50, 12)

      py5.no_stroke()
      py5.text_align(py5.LEFT, py5.CENTER)
      py5.fill(*TEXT_MUTED)
      py5.text_size(17)
      py5.text("Primfaktorzerlegung:", 72, 750)

      # Vollständige Zerlegung als Produkt in Grün daneben schreiben
      py5.fill(*THEME_GGT)
      py5.text_size(20)
      py5.text(f"{number} = " + format_factors(get_prime_factors(number)), 285, 750)


def draw_ggt_kgv():
  """Zeichnet die Unterseite entweder für ggT oder für kgV."""
  # 1. Farben und Theorietext passend zum gewählten Modus festlegen
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

  # 2. Zwei Eingabefelder nebeneinander und rechts der Berechnen-Button
  draw_input_box(50, 200, 350, 48, "Zahl 1:", input_a, "z.B. 24", active_field == 0, accent)
  draw_input_box(420, 200, 350, 48, "Zahl 2:", input_b, "z.B. 36", active_field == 1, accent)
  draw_button(790, 200, 160, 48, "Berechnen", accent, (255, 255, 255), 17)

  # 3. Hinweistext unter den Eingabefeldern
  py5.text_align(py5.LEFT, py5.CENTER)
  py5.fill(*TEXT_MUTED)
  py5.text_size(16)
  py5.text(pair_message, 50, 268)

  # 4. Ergebniskarte anzeigen, sobald beide Zahlen berechnet wurden
  if num_a is not None and num_b is not None:
    greatest = math.gcd(num_a, num_b)  # Berechnet den ggT der beiden Zahlen

    # Karte zeichnen
    py5.fill(*CARD_BG)
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1.5)
    py5.rect(50, 300, 1100, 195, 14)

    # Farbiger Akzentbalken am linken Rand der Ergebniskarte
    py5.no_stroke()
    py5.fill(*accent)
    py5.rect(50, 300, 8, 195, 14, 0, 0, 14)

    py5.text_align(py5.LEFT, py5.CENTER)
    py5.fill(*TEXT_DARK)
    py5.text_size(30)

    # Nur das jeweilige Resultat (ggT ODER kgV) gross darstellen
    if mode == "ggt":
      py5.text(f"ggT({num_a}, {num_b}) = {greatest}", 82, 348)
    elif mode == "kgv":
      # Mathematischer Zusammenhang: kgV(a, b) = (a * b) / ggT(a, b)
      least = abs(num_a * num_b) // greatest
      py5.text(f"kgV({num_a}, {num_b}) = {least}", 82, 348)

    # Horizontale Trennlinie innerhalb der Ergebniskarte
    py5.stroke(*BORDER_SOFT)
    py5.stroke_weight(1)
    py5.line(82, 392, 1120, 392)

    # Darunter beide Primfaktorzerlegungen als visuelle Lernhilfe einblenden
    py5.no_stroke()
    py5.fill(*TEXT_MUTED)
    py5.text_size(17)
    py5.text(f"Primfaktoren von {num_a}:  {format_factors(get_prime_factors(num_a))}", 82, 425)
    py5.text(f"Primfaktoren von {num_b}:  {format_factors(get_prime_factors(num_b))}", 82, 460)


# ==============================================================================
# 9. MAUS- UND TASTATURSTEUERUNG
# ==============================================================================

def mouse_pressed():
  """Wird automatisch aufgerufen, sobald die linke Maustaste gedrückt wird."""
  global current_step, active_field

  # 1. Klicks im Hauptmenü prüfen (anhand der Koordinaten der drei Karten)
  if mode == "menu":
    if 310 <= py5.mouse_x <= 890:
      if 225 <= py5.mouse_y <= 327:
        reset_mode("prim")
      elif 355 <= py5.mouse_y <= 457:
        reset_mode("ggt")
      elif 485 <= py5.mouse_y <= 587:
        reset_mode("kgv")
    return

  # 2. Klick auf den Button "Zurück zum Menü" oben rechts (gilt auf allen Unterseiten)
  if 970 <= py5.mouse_x <= 1150 and 17 <= py5.mouse_y <= 57:
    reset_mode("menu")
    return

  # 3. Klicks auf der Unterseite "Primfaktorzerlegung"
  if mode == "prim":
    # Klick auf den Button "Berechnen"
    if 445 <= py5.mouse_x <= 590 and 200 <= py5.mouse_y <= 248:
      calculate_number()
      return
    # Jeder weitere Klick ins Fenster deckt die nächste Ebene des Baums auf
    if number is not None and current_step < len(factor_steps):
      current_step += 1

  # 4. Klicks auf den Unterseiten "ggT" und "kgV"
  elif mode in ("ggt", "kgv"):
    if 50 <= py5.mouse_x <= 400 and 200 <= py5.mouse_y <= 248:
      active_field = 0  # Erstes Eingabefeld ("Zahl 1") auswählen
    elif 420 <= py5.mouse_x <= 770 and 200 <= py5.mouse_y <= 248:
      active_field = 1  # Zweites Eingabefeld ("Zahl 2") auswählen
    elif 790 <= py5.mouse_x <= 950 and 200 <= py5.mouse_y <= 248:
      calculate_pair()  # Button "Berechnen" auslösen


def key_pressed():
  """Wird automatisch aufgerufen, sobald eine Taste auf der Tastatur gedrückt wird."""
  global input_text, input_a, input_b, active_field, current_step

  # Sondertasten ohne Textzeichen (wie Shift, Ctrl, Alt, Pfeiltasten) sofort überspringen
  if not isinstance(py5.key, str):
    return

  # 1. Schnellauswahl per Zifferntaste 1, 2 oder 3 im Hauptmenü
  if mode == "menu":
    if py5.key == "1":
      reset_mode("prim")
    elif py5.key == "2":
      reset_mode("ggt")
    elif py5.key == "3":
      reset_mode("kgv")
    return

  # 2. Tabulator-Taste ("\t") wechselt bei ggT/kgV zwischen Feld 0 und Feld 1
  if py5.key == "\t":
    if mode in ("ggt", "kgv"):
      active_field = 1 - active_field  # Trick: 1 - 0 ergibt 1, und 1 - 1 ergibt 0
    return

  # 3. Rücktaste / Löschen (ASCII-Code 8 auf Windows/Linux, 127 auf macOS)
  if py5.key == chr(8) or py5.key == chr(127):
    if mode == "prim":
      input_text = input_text[:-1]  # Schneidet das letzte Zeichen ab
    elif mode in ("ggt", "kgv"):
      if active_field == 0:
        input_a = input_a[:-1]
      else:
        input_b = input_b[:-1]
    return

  # 4. Enter-Taste ("\r" oder "\n") startet die Berechnung auf der aktuellen Seite
  if py5.key in "\r\n":
    if mode == "prim":
      calculate_number()
    elif mode in ("ggt", "kgv"):
      calculate_pair()
    return

  # 5. Leertaste (" ") deckt bei der Primfaktorzerlegung den nächsten Baumschritt auf
  if py5.key == " " and mode == "prim":
    if number is not None and current_step < len(factor_steps):
      current_step += 1
    return

  # 6. Ziffern 0 bis 9 an das aktuell aktive Eingabefeld anhängen (mit Längenbegrenzung)
  if py5.key in "0123456789":
    if mode == "prim" and len(input_text) < 10:
      input_text += py5.key
    elif mode in ("ggt", "kgv"):
      if active_field == 0 and len(input_a) < 9:
        input_a += py5.key
      elif active_field == 1 and len(input_b) < 9:
        input_b += py5.key


# ==============================================================================
# 10. PROGRAMM STARTEN
# ==============================================================================

# Startet das py5-Fenster und ruft automatisch einmal setup() und danach laufend draw() auf
py5.run_sketch()