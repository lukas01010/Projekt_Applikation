import py5


def setup():
    py5.size(400, 300)
    py5.background(20, 30, 40)


def draw():
    py5.background(20, 30, 40)
    py5.fill(255, 200, 100)
    py5.circle(py5.mouse_x, py5.mouse_y, 40)


py5.run_sketch()
