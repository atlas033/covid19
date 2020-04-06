#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import json
import itertools
from matplotlib import animation
import matplotlib.colors
import os
import collections

def hide_axis(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)
    ax.tick_params(axis='both', which='both', length=0)

code_to_name = {
    'ZH':'Zürich',
    'BE':'Bern',
    'LU':'Luzern',
    'UR':'Uri',
    'SZ':'Schwyz',
    'OW':'Obwalden',
    'NW':'Nidwalden',
    'GL':'Glarus',
    'ZG':'Zug',
    'FR':'Fribourg',
    'SO':'Solothurn',
    'BS':'Basel-Stadt',
    'BL':'Basel-Landschaft',
    'SH':'Schaffhausen',
    'AR':'Appenzell Ausserrhoden',
    'AI':'Appenzell Innerrhoden',
    'SG':'St. Gallen',
    'GR':'Graubünden',
    'AG':'Aargau',
    'TG':'Thurgau',
    'TI':'Ticino',
    'VD':'Vaud',
    'VS':'Valais',
    'NE':'Neuchâtel',
    'GE':'Genève',
    'JU':'Jura',
}

code_to_center_shift = {
    'BE':(0,0),
    'LU':(0,0),
    'UR':(0,0),
    'SZ':(0,0),
    'OW':(0,-3),
    'NW':(2,2),
    'GL':(0,0),
    'ZG':(-2,-2),
    'FR':(5,-3),
    'SO':(-5,0),
    'BS':(-1,0.5),
    'BL':(9,-4),
    'SH':(-4,1),
    'AR':(-9,-6),
    'AI':(3,-3),
    'SG':(-7,-3),
    'GR':(0,0),
    'AG':(4,5),
    'TG':(5,7),
    'TI':(0,5),
    'VD':(-20,5),
    'VS':(0,0),
    'NE':(1,-3),
    'GE':(0,-2),
    'JU':(0,3),
        }

for key in code_to_center_shift:
    shift = code_to_center_shift[key]
    k = 1e3
    code_to_center_shift[key] = [shift[0] * k, shift[1] * k]


name_to_code = {}
for code,name in code_to_name.items():
    name_to_code[name] = code

codes = code_to_name.keys()

class Renderer:
    def __init__(self, frame_callback):
        '''
        frame_callback: callable
            Function that takes Renderer and called before rendering a frame.
            It can use `set_colors()` and `set_texts()` to update the state,
            and `get_frame()` and `get_max_frame()` to get current frame index.
        '''
        basedir = os.path.dirname(__file__)
        with open(os.path.join(basedir, "data/home_work_people.json")) as f:
            home_work_people = json.load(f)
        fname = os.path.join(basedir, "data/canton_shapes.npy")
        d = np.load(fname, allow_pickle=True).item()

        # Compute shape centers.
        centers = {}
        for name, ss in d.items():
            for i,s in enumerate(ss):
                x, y = s
                code = name_to_code[name]
                centers[code] = [x.mean(), y.mean()]
                if code in code_to_center_shift:
                    shift = code_to_center_shift[code]
                    centers[code][0] += shift[0]
                    centers[code][1] += shift[1]
                break

        colorcycle = {}
        plt_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for i,code in enumerate(codes):
            colorcycle[code] = np.array(matplotlib.colors.to_rgb(
                    plt_cycle[i % len(plt_cycle)]))
        self.colorcycle = colorcycle

        dpi = 200
        fig, ax = plt.subplots(figsize=(1920 / dpi, 1080 / dpi), dpi=dpi)
        hide_axis(ax)
        ax.set_aspect('equal')
        fig.tight_layout()
        self.fig = fig
        self.ax = ax

        # Draw shapes.
        fills = collections.defaultdict(list)
        self.fills = fills
        for name, ss in d.items():
            code = name_to_code[name]
            for i,s in enumerate(ss):
                x, y = s
                line, = ax.plot(x, y, marker=None, c='black', lw=0.25)
                fill, = ax.fill(x, y, alpha=0.25, c='white')
                fills[code].append(fill)

        # Draw labels.
        texts = dict()
        self.texts = texts
        for code in codes:
            xc, yc = centers[code]
            ax.text(xc, yc, code, ha='center', va='bottom', zorder=10,
                    color=[0,0,0])
            text = ax.text(
                    xc, yc - 1700,
                    '', ha='center', va='top', zorder=10, fontsize=7,
                    color=[0,0,0])
            texts[code] = text
            ax.scatter(xc, yc, color=colorcycle[code], s=10, zorder=5)

        # Draw connections.
        max_people = np.max([v for vv in home_work_people.values() for v in vv.values()])
        for c_home, c_work in itertools.product(codes, repeat=2):
            x0, y0 = centers[c_home]
            x1, y1 = centers[c_work]
            n = home_work_people[c_home][c_work]
            alpha = np.clip(n / max_people * 100, 0, 0.5)
            lw = np.clip(n / max_people * 100, 0.5, 5)
            ax.plot([x0, x1], [y0, y1], color=colorcycle[c_work], alpha=alpha, lw=lw)

        self.frame_callback = frame_callback
        self.code_to_color = {}
        self.code_to_text = {}
        self.codes = codes

    def set_colors(self, code_to_color):
        '''
        code_to_color: `dict`
          Mapping from canton code to float between 0 and 1.
        '''
        self.code_to_color = code_to_color

    def set_texts(self, code_to_text):
        '''
        code_to_text: `dict`
          Mapping from canton code to label text.
        '''
        self.code_to_text = code_to_text

    def get_colors(self):
        return self.code_to_color

    def get_texts(self):
        return self.code_to_text

    def get_codes(self):
        return self.codes

    def get_frame(self):
        '''
        Returns current frame index between 0 and get_max_frame().
        '''
        return self.frame

    def get_max_frame(self):
        '''
        Returns maximum frame index.
        Set to `frames - 1` by `save_movie(frames)`.
        Set to 1 by `save_image()`.
        '''
        return self.max_frame

    def init(self):
        return [v for vv in self.fills.values() for v in vv] + list(self.texts.values())

    def update(self, frame=-1, silent=False):
        self.frame = frame
        self.frame_callback(self)

        if frame == -1:
            frame = self.max_frame
        if not silent:
            print("{:}/{:}".format(frame, self.max_frame))
        for code,color in self.code_to_color.items():
            color = self.colorcycle[code] * np.clip(color, 0, 1)
            for fill in self.fills[code]:
                fill.set_color(color)
        for code,text in self.code_to_text.items():
            self.texts[code].set_text(str(text))
        return [v for vv in self.fills.values() for v in vv] + list(self.texts.values())

    def save_movie(self, frames=100, filename="a.mp4", fps=15):
        self.max_frame = frames - 1
        ani = animation.FuncAnimation(self.fig, self.update,
                frames=list(range(frames)),
                init_func=self.init, blit=True)
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=fps, metadata=dict(artist='Me'), bitrate=2000)
        ani.save(filename, writer=writer)

    def save_image(self, frame=-1, filename="a.png"):
        self.max_frame = 1
        self.init()
        self.update(self.max_frame, silent=True)
        self.fig.savefig(filename)

if __name__ == "__main__":

    def frame_callback(rend):
        print(rend.get_frame(), rend.get_max_frame())
        colors = dict()
        texts = dict()
        for i, c in enumerate(rend.get_codes()):
            colors[c] = np.sin(i + rend.get_frame()) ** 2 + 1
            texts[c] = "{:},{:}".format(rend.get_frame(), i)
        rend.set_colors(colors)
        rend.set_texts(texts)

    rend = Renderer(frame_callback)

    #rend.save_movie(frames=30)
    rend.save_image()
