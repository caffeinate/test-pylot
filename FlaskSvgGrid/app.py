import multiprocessing
from multiprocessing import shared_memory
import time

from flask import Flask, current_app, jsonify, render_template
import gunicorn.app.base


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


def grid_producer(access_lock, shared_memory_label, grid_dimension):
    init_list = []
    for x in range(grid_dimension):
        for y in range(grid_dimension):
            init_list.extend([x, y, "#000"])

    with access_lock:
        shared_list = shared_memory.ShareableList(init_list, name=shared_memory_label)

    while True:
        time.sleep(1)

        # any kind of pattern
        colours = ["#f00", "#0f0", "#00f", "#ff0"]
        loop_start = int(time.time())
        with access_lock:
            for x in range(grid_dimension):
                for y in range(grid_dimension):
                    v = loop_start + (x * grid_dimension) + (x * grid_dimension) * y
                    colour_choice = colours[v % len(colours)]
                    grid_position = (x * grid_dimension) + y
                    # print(shared_list[grid_position], colour_choice, grid_position)
                    shared_list[(grid_position * 3) + 2] = colour_choice


class FlaskSharedMemory(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskSharedMemory, self).__init__(*args, **kwargs)

        self.grid_dimension = 10
        self.shared_memory_label = "shared_memory_z16"
        self.access_lock = multiprocessing.Lock()
        # self.shared_list = shared_memory.ShareableList(name=self.shared_memory_label)

    def start_sidecar(self):

        time.sleep(2)
        p = multiprocessing.Process(
            target=grid_producer, args=(self.access_lock, self.shared_memory_label, self.grid_dimension)
        )
        p.start()


app = FlaskSharedMemory(__name__)


@app.route("/")
def root():
    return render_template("svg_grid.html", grid_dimension=current_app.grid_dimension)


@app.route("/frame")
def frame():
    shared_list = shared_memory.ShareableList(name=current_app.shared_memory_label)

    with current_app.access_lock:
        reshaped_grid = []
        grid_items = int(len(shared_list) / 3)
        for grid_position in range(grid_items):
            grid_cell = grid_position * 3
            x = shared_list[grid_cell]
            y = shared_list[grid_cell + 1]
            colour = shared_list[grid_cell + 2]

            if x is None or y is None or colour is None:
                continue

            reshaped_grid.append([x, y, colour])

    return jsonify(reshaped_grid)


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":

    app.start_sidecar()

    options = {
        "bind": "%s:%s" % ("127.0.0.1", "8080"),
        "workers": number_of_workers(),
    }
    # logger.debug("StandaloneApplication running")
    StandaloneApplication(app, options).run()
