import multiprocessing
from multiprocessing import shared_memory
import time

from flask import Flask, current_app, jsonify, render_template
import gunicorn.app.base


def number_of_workers():
    # return (multiprocessing.cpu_count() * 2) + 1
    return 1


class GridProducer:
    def __init__(self, grid_dimension):
        self.grid_dimension = grid_dimension
        self.access_lock = None
        self.shared_list = None

    def initiate(self):

        self.access_lock = multiprocessing.Lock()

        init_list = []
        for x in range(self.grid_dimension):
            for y in range(self.grid_dimension):
                init_list.extend([x, y, "#000"])

        with self.access_lock:
            self.shared_list = shared_memory.ShareableList(init_list)
            shared_memory_label = self.shared_list.shm.name

        return self.access_lock, shared_memory_label

    def run(self):

        while True:
            time.sleep(1)

            # any kind of pattern
            colours = ["#f00", "#0f0", "#00f", "#ff0"]
            loop_start = int(time.time())
            with self.access_lock:
                for x in range(self.grid_dimension):
                    for y in range(self.grid_dimension):
                        v = loop_start + (x * self.grid_dimension) + (x * self.grid_dimension) * y
                        colour_choice = colours[v % len(colours)]
                        grid_position = (x * self.grid_dimension) + y
                        self.shared_list[(grid_position * 3) + 2] = colour_choice


class FlaskSharedMemory(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskSharedMemory, self).__init__(*args, **kwargs)

        self.grid_dimension = 10
        self.access_lock = self.shared_memory_label = None

    def start_sidecar(self):

        grid_writer = GridProducer(grid_dimension=self.grid_dimension)
        self.access_lock, self.shared_memory_label = grid_writer.initiate()

        p = multiprocessing.Process(target=grid_writer.run)
        p.start()


app = FlaskSharedMemory(__name__)


@app.route("/")
def root():
    return render_template("svg_grid.html", grid_dimension=current_app.grid_dimension)


@app.route("/frame")
def frame():

    if current_app.shared_memory_label is None or current_app.access_lock is None:
        return "Shared memory writer not initialised", 500

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

    frame_doc = {
        "cell_values": reshaped_grid,
        "build_time": None,
        "valid_until": None,
    }

    return jsonify(frame_doc)


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
    StandaloneApplication(app, options).run()
