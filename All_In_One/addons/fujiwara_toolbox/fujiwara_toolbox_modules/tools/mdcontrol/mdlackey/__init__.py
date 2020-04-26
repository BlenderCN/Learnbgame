import os
import datetime
import lackey
from lackey import *

import sys
sys.path.append(os.pardir)
import uwscwrapper as uwsc

sys.path.append(os.pardir)
import simulation_config

debug = False
# debug = True

###############################################
#  for patch
from PIL import Image, ImageTk
from numbers import Number
try:
    import Tkinter as tk
    import tkMessageBox as tkmb
except ImportError:
    import tkinter as tk
    import tkinter.messagebox as tkmb
import multiprocessing
import subprocess
import pyperclip
import tempfile
import platform
import numpy
import time
import uuid
import cv2
import sys
import os
import re

# Python 3 compatibility
try:
    basestring
except NameError:
    basestring = str
try:
    FOREVER = float("inf")
except:
    import math
    FOREVER = math.inf
###############################################

def check_abort():
    loc = Mouse().getPos()
    if loc.getX() < 10 and loc.getY() < 10:
        print("abort.")
        sys.exit()


class RegionPatch(Region, object):
    def exists_patch(self, pattern, seconds=None):
        """ Searches for an image pattern in the given region

        Returns Match if pattern exists, None otherwise (does not throw exception)
        Sikuli supports OCR search with a text parameter. This does not (yet).
        """
        find_time = time.time()
        r = self
        if seconds is None:
            seconds = self.autoWaitTimeout
        if isinstance(pattern, int):
            # Actually just a "wait" statement
            time.sleep(pattern)
            return
        if not pattern:
            time.sleep(seconds)
        if not isinstance(pattern, Pattern):
            if not isinstance(pattern, basestring):
                raise TypeError("find expected a string [image path] or Pattern object")
            pattern = Pattern(pattern)
        needle = cv2.imread(pattern.path)
        if needle is None:
            raise ValueError("Unable to load image '{}'".format(pattern.path))
        needle_height, needle_width, needle_channels = needle.shape
        match = None
        timeout = time.time() + seconds

        # Consult TemplateMatcher to find needle
        while not match:
            matcher = lackey.TemplateMatchers.PyramidTemplateMatcher(r.getBitmap())
            match = matcher.findBestMatch(needle, pattern.similarity)
            time.sleep(1/self._defaultScanRate if self._defaultScanRate is not None else 1/Settings.WaitScanRate)
            if time.time() > timeout:
                break

        if match is None:
            Debug.info("Couldn't find '{}' with enough similarity.".format(pattern.path))
            return None

        # Translate local position into global screen position
        position, confidence = match
        position = (position[0] + self.x, position[1] + self.y)
        self._lastMatch = Match(
            confidence,
            pattern.offset,
            (position, (needle_width, needle_height)))
        #self._lastMatch.debug_preview()
        Debug.info("Found match for pattern '{}' at ({},{}) with confidence ({}). Target at ({},{})".format(
            pattern.path,
            self._lastMatch.getX(),
            self._lastMatch.getY(),
            self._lastMatch.getScore(),
            self._lastMatch.getTarget().x,
            self._lastMatch.getTarget().y))
        self._lastMatchTime = (time.time() - find_time) * 1000 # Capture find time in milliseconds
        return self._lastMatch

class MD():
    """
        MarvelousDesigner操作用クラス。
    """
    def __init__(self):
        app = App("Marvelous Designer")
        self.is_initialized = False
        if not app.isRunning():
            return
        self.is_initialized = True
        self.app = app

        self.ver = "7"
        title = app.getWindow()
        self.title = title
        if "7" in title:
            self.ver = "7"
        if "6.5" in title:
            self.ver = "6.5"

        self.scale = "100%"

        Settings.MoveMouseDelay = 0.01
        Settings.MinSimilarity = 0.95

        self.set_scale("file")

        self.activate()
        self.screen = App.focusedWindow().getScreen()
        self.screen_id = self.screen.getID()

    @classmethod
    def wait(self, time):
        App.pause(time)

    def imgpath(self, filename):
        moddir = os.path.dirname(__file__)
        path = "img" + os.sep + str(self.ver) + os.sep + "jp" + os.sep + self.scale + os.sep
        return moddir + os.sep + path + filename + ".png"

    def activate(self):
        if check_abort():
            return
        """
            uwscwrapperをつかったウィンドウのアクティベート。
        """
        print(self.title)
        uwsc.activate(self.title)
        self.wait(1)

    def set_scale(self, filename):
        """
            各スケール画像で検索して、倍率を確定する。
        """
        scale_list = ["100%", "125%", "150%", "175%", "200%"]
        self.activate()
        region = App.focusedWindow().getScreen()

        for scale in scale_list:
            self.scale = scale

            img = self.imgpath(filename)

            if os.path.exists(img):
                m = region.exists(img)

                if m is not None:
                    return
        
        #なかったのでデフォルトに戻す
        self.scale = "100%"

    def find(self, filename, multiscreen=True,):
        return self.click(filename, click=False, multiscreen=multiscreen)

    @classmethod
    def create_correct_region(cls, region):
        x0 = region.getTopLeft().getX()
        y0 = region.getTopLeft().getY()
        x1 = region.getBottomRight().getX()
        y1 = region.getBottomRight().getY()
        w = x1 - x0
        h = y1 - y0

        return RegionPatch(x0,y0,w,h)

    @classmethod
    def highlight(cls, region, color="yellow"):
        global debug
        if debug:
            region.highlight(True, 1, color)

    @classmethod
    def extend_region(cls, region, value):
        x0 = region.getTopLeft().getX() - value
        y0 = region.getTopLeft().getY() - value
        x1 = region.getBottomRight().getX() + value
        y1 = region.getBottomRight().getY() + value
        w = x1 - x0
        h = y1 - y0
        return Region(x0,y0,w,h)


    def click(self, filename, click=True, region=None, multiscreen=True):
        if check_abort():
            print("aboted.")
            return False

        # win = App.focusedWindow()
        # self.highlight(win, "green")

        sec = simulation_config.max_search_time
        img = self.imgpath(filename)
        m = None

        start_time = datetime.datetime.now()

        if region is None and multiscreen:
            n_of_screens = Screen.getNumberScreens()

            #アクティブスクリーンから検索するリスト
            scrs = [self.screen_id]
            for i in range(n_of_screens):
                if i not in scrs:
                    scrs.append(i)

            for i in scrs:
                region = self.create_correct_region(Screen(i))
                self.highlight(region)
                m = region.exists_patch(img, sec)
                if m:
                    break
        elif region is None and not multiscreen:
            region = self.screen
            region = self.create_correct_region(region)
            m = region.exists_patch(img, sec)
        else:
            region = self.create_correct_region(region)
            self.highlight(region)
            m = region.exists_patch(img, sec)

        if m:
            self.highlight(m, "red")
            if click:
                region.click(m)
            print(filename)

            end_time = datetime.datetime.now()
            dt = end_time - start_time
            print("time: {}".format(dt))


            return m
        return None

    # def click_untill_success(self, filename):
    #     for i in range(100):
    #         c = self.click(filename)
    #         if c is not None:
    #             return True
    #         self.wait(0.1)
    #     return False

    def click_untill_imgfound(self, filename, searchfor):
        for i in range(100):
            f = self.find(searchfor)
            if f is not None:
                return True

            self.click(filename)
            self.wait(0.5)
        return False
        


class MDMacro():
    md = None

    @classmethod
    def md_setup(cls):
        if cls.md == None:
            cls.md = MD()
        return cls.md

    @classmethod
    def wait(self, time):
        MD.wait(time)

    @classmethod
    def macro_test(self):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            return()
        if not md.click("file"):
            return
        md.click("new_file")
        md.click("no")
        md.click("file")
        md.click("import")
        md.click("obj")
        # md.click("")

    @classmethod
    def set_up(self):
        md = MDMacro.md_setup()
        return md

    @classmethod
    def new_file(self):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return()
        md.activate()
        if not md.click("file"):
            return
        md.click("new_file")
        md.click("no")

    @classmethod
    def paste_str(self, str):
        App.setClipboard(str)
        type("v", KeyModifier.CTRL)
        type(Key.ENTER)

    @classmethod
    def open_avatar(self,filepath):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return()

        if not md.click("file"):
            return
        md.click("import")
        md.click("obj")

        # uwsc.click_item(filename)
        MD.wait(2)
        self.paste_str(filepath)

        md.click("ok", multiscreen=True)
        for i in range(30):
            md.activate()
            f = md.find("close")
            if f:
                break
            md.wait(0.5)
        md.click("close", multiscreen=True)
        md.activate()

    @classmethod
    def open_avatar_abc(self, filepath):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return()

        if not md.click("file"):
            return
        md.click("import")
        md.click("alembic")

        # uwsc.click_item(filename)
        MD.wait(2)
        self.paste_str(filepath)
        md.click("m", multiscreen=True)
        md.click("ok", multiscreen=True)
        for i in range(30):
            md.activate()
            f = md.find("close",multiscreen=True)
            if f:
                break
            md.wait(0.5)
        md.click("close", multiscreen=True)
        md.activate()

    @classmethod
    def add_garment(self, filepath):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return

        #成功するまでトライ
        for i in range(30):
            md.activate()
            md.click("file")
            c = md.click("add")

            if c:
                break
            md.wait(0.5)

        md.click("garment")

        MD.wait(2)
        self.paste_str(filepath)

    @classmethod
    def add_mdd(self, filepath):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return()

        md.activate()

        if not md.click("file"):
            return
        md.click("import")
        md.click("mdd_chache_default")

        MD.wait(2)
        self.paste_str(filepath)
        md.click("m", multiscreen=True)
        md.click("ok", multiscreen=True)

    @classmethod
    def simulate(self, time):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return

        md.activate()

        for i in range(30):
            md.activate()
            md.click("3dgarment")
            md.click("simulation_off")
            f = md.find("sim_on")

            if f:
                break
            md.wait(0.5)

        for i in range(30):
            md.activate()
            md.click("avatar")
            md.click("play_motion_off")
            f = md.find("anim_on")

            if f:
                break
            md.wait(0.5)

        MD.wait(time)

        for i in range(30):
            md.activate()
            md.click("3dgarment")
            md.click("simulation_on")
            f = md.find("sim_off")

            if f:
                break
            md.wait(0.5)

    @classmethod
    def select_all(self):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            return

        md.activate()
        type("a",Key.CTRL)

    @classmethod
    def export_obj(self, filepath, use_thickness):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return

        md.activate()
        md.click("file")
        md.click("export")
        md.click("obj_selected_only")
        MD.wait(2)
        self.paste_str(filepath)
        MD.wait(0.5)
        uwsc.click_item("はい")
        MD.wait(0.5)
        md.click("single_object", multiscreen=True)

        # m = md.find("select_all_graphics_on")
        # if not m:
        #     md.click("select_all_graphics")

        # m = md.find("select_all_graphics_and_trims_on")
        # if not m:
        #     md.click("select_all_graphics_and_trims")

        # m = md.find("select_all_patterns_on")
        # if not m:
        #     md.click("select_all_patterns")
        
        m = md.find("select_all_graphics")
        if m:
            m = MD.extend_region(m, 10)
            md.click("checkbox_off",region=m)

        m = md.find("select_all_graphics_and_trims") 
        if m:
            m = MD.extend_region(m, 10)
            md.click("checkbox_off",region=m)

        m = md.find("select_all_patterns") 
        if m:
            m = MD.extend_region(m, 10)
            md.click("checkbox_off",region=m)

        m = md.find("combine_uvs") 
        if m:
            m = MD.extend_region(m, 10)
            md.click("checkbox_on",region=m)

        # md.click("combine_objects")
        if use_thickness:
            md.click("thick")
        md.click("m")
        md.click("ok")

    @classmethod
    def export_abc(self, filepath):
        md = MDMacro.md_setup()
        if not md.is_initialized:
            print("###MD is not initialized.")
            return

        md.activate()
        md.click("file")
        md.click("export")
        md.click("alembic_ogawa")
        MD.wait(2)
        self.paste_str(filepath)
        uwsc.click_item("はい")
        MD.wait(1)
        md.click("single_object")
        if use_thickness:
            md.click("thick")
        md.click("m")
        md.click("ok")
