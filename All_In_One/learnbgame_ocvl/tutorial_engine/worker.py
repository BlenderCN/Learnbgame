from pynput.keyboard import Key, Controller
import time
import threading
import tornado
import bpy
from tornado.ioloop import IOLoop
from logging import getLogger

from .engine_app import tutorial_engine_app
from .settings import TUTORIAL_ENGINE_PORT

logger = getLogger(__name__)


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        logger.info("Tutorial engine thread stop.")
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def start(self, *args, **kwargs):
        logger.info("Worker tread started.")
        bpy.ops.wm.modal_timer_consumer_request_operator()
        logger.info("Modal timer operator started.")
        super().start(*args, **kwargs)


def tutorial_engine_worker():
    bpy.ioloop = IOLoop.current()
    tornado.log.enable_pretty_logging()
    app = tutorial_engine_app()
    app.listen(TUTORIAL_ENGINE_PORT)
    logger.info("Tutorial Engine worker started on port={}.".format(TUTORIAL_ENGINE_PORT))
    IOLoop.current().start()


def jupyter_engine_worker():
    from subprocess import call
    com = "/Users/dawidaniol/Downloads/blender-2.79-macOS-10.6/blender.app/Contents/Resources/2.79/python/bin/jupyter"
    call([com, "notebook"])



def print_keyborad_callback(text=""):

    keyboard = Controller()

    for char in text:
        if char == "!":
            keyboard.press(Key.enter)
        else:
            keyboard.press(char)
        time.sleep(0.5)


def print_keyborad_worker(text):
    return threading.Thread(target=print_keyborad_callback, kwargs={"text": text}, daemon=True)



engine_worker_thread = StoppableThread(target=tutorial_engine_worker, daemon=True)
jupyter_worker_thread = StoppableThread(target=jupyter_engine_worker, daemon=True)
bpy.engine_worker_thread = engine_worker_thread
bpy.jupyter_worker_thread = jupyter_worker_thread
