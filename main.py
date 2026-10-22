"""
Copyright (c) 2017, Jonathan Brooks
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

'''
Rocket Boots Game
Fly through the sky trying to avoid obstacles by tapping the screen to trigger boosts from your Rocket Boots
'''

import kivy
from kivy.utils import platform
from kivy.config import Config

if platform in ('linux', 'win', 'macosx'):
    ratio = 2560.0 / 1440.0  # Ratio of pixel XL
    x = 1400  # width for testing
    y = int(x / ratio)
    Config.set('graphics', 'width', str(x))  # set window size for testing (must be before importing app)
    Config.set('graphics', 'height', str(y))
    PC = True
else:
    PC = False

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from kivy.core.audio import SoundLoader
from random import choice, randrange
from os.path import dirname, join, basename
from glob import glob
from kivy.storage.jsonstore import JsonStore
from functools import partial

kivy.require('2.0.0')

DIRECTORY = join(dirname(__file__), "assets")
RESOLUTION = [800.0, 480.0]
WINDOW_SIZE = [float(Window.size[0]), float(Window.size[1])]
X_RATIO = WINDOW_SIZE[0] / RESOLUTION[0]
Y_RATIO = WINDOW_SIZE[1] / RESOLUTION[1]
RATIO = max(X_RATIO, Y_RATIO)


def update_window_metrics(*args):
    global WINDOW_SIZE, X_RATIO, Y_RATIO, RATIO
    WINDOW_SIZE = [float(Window.size[0]), float(Window.size[1])]
    X_RATIO = WINDOW_SIZE[0] / RESOLUTION[0]
    Y_RATIO = WINDOW_SIZE[1] / RESOLUTION[1]
    RATIO = max(X_RATIO, Y_RATIO)


Window.bind(on_resize=lambda *args: update_window_metrics())

AUDIO = {}  # dict to hold location of audio files
IMAGES = {}  # dict to hold location of images
GIFS = {}  # dict to hold location of gifs

# some random colors to choose from
black = (0, 0, 0, 1)
yellow = (0.99, 0.99, 0, 1)
red = (0.99, 0, 0, 1)
orange = (0.99, .45, 0, 1)
white = (1, 1, 1, 1)
dark_grey = (0.2, 0.2, 0.2, 1)
blue_grey = (0.3, 0.3, 0.45, 1)

LEVEL = 'level1'
LEVELS = {'level1': {'obstacles': (275, 6, 'obstacle1'),
                     'ground': ('hills1', 'hills2'),
                     'Level': (.25, 200, 'level1', 'level1'),
                     'background': 'sky1'},
          'level2': {'obstacles': (225, 5, 'obstacle2'),
                     'ground': ('icehills1', 'icehills2'),
                     'Level': (.3, 160, 'level2', 'level2lock'),
                     'background': 'sky2'},
          'level3': {'obstacles': (250, 4, 'obstacle3'),
                     'ground': ('beach1', 'beach2'),
                     'Level': (.35, 160, 'level3', 'level3lock'),
                     'background': 'sky3'},
          'level4': {'obstacles': (200, 3, 'obstacle4'),
                     'ground': ('fract1', 'fract2'),
                     'Level': (.5, 100, 'level4', 'level4lock'),
                     'background': 'sky2'},
          }


# shadow text just makes 2 of the same text but with an offset for a drop shadow effect
def shadow_text(text, pos=(0, 0), size=90, align='center', offset=None,
                color1=yellow, color2=black, font='freesansbold.ttf'):
    if offset is None:
        offset = int(size / 12)
    if align == 'center':
        label = Label(text=str(text), color=color1, font_size=size * RATIO, size_hint=(None, None),
                      center_x=pos[0], center_y=pos[1],
                      font_name=join(DIRECTORY, font))

        label_shadow = Label(text=str(text), color=color2, font_size=size * RATIO, size_hint=(None, None),
                             center_x=pos[0] + offset, center_y=pos[1] - offset,
                             font_name=join(DIRECTORY, font))
    elif align == 'leftcenter':
        label = Label(text=str(text), color=color1, font_size=size * RATIO, size_hint=(None, None),
                      x=pos[0], center_y=pos[1],
                      font_name=join(DIRECTORY, font))

        label_shadow = Label(text=str(text), color=color2, font_size=size * RATIO, size_hint=(None, None),
                             x=pos[0] + offset, center_y=pos[1] - offset,
                             font_name=join(DIRECTORY, font))
    else:
        print('invalid shadow text align')
        return None, None
    return label_shadow, label


class Gems(Widget):
    def __init__(self):
        super(Gems, self).__init__()
        self.speed = LEVELS[LEVEL]['obstacles'][1] * 0.7
        self.gem = load_gif('gem2', 0)
        min_y = int(WINDOW_SIZE[1] * 0.07)
        max_y = max(min_y + 1, int((WINDOW_SIZE[1] * 0.93) - self.gem.height))
        self.gem.pos = WINDOW_SIZE[0], randrange(min_y, max_y)
        self.add_widget(self.gem)
        anim = Animation(x=-self.gem.width, duration=self.speed)
        anim.start(self.gem)

    def get_gem(self):
        return self.gem


''' Obstacles(Widget)
load obstacles and animate them across the screen (they are removed by the level method when they reach the edge of
the screen.'''


class Obstacles(Widget):
    def __init__(self, difficulty):
        super(Obstacles, self).__init__()
        settings = LEVELS[LEVEL]['obstacles']
        self.gap = int((settings[0] * Y_RATIO) - difficulty)
        self.speed = settings[1]

        min_gap = max(1, self.gap)
        max_height = max(min_gap + 1, int(WINDOW_SIZE[1]))
        self.obst_top = load_image(settings[2], 0, x=WINDOW_SIZE[0], y=randrange(min_gap, max_height))

        self.obst_bottom = load_image(settings[2], 0, x=WINDOW_SIZE[0])

        self.obst_bottom.top = self.obst_top.y - self.gap
        self.add_widget(self.obst_top)
        self.add_widget(self.obst_bottom)

        anim = Animation(x=-self.obst_top.width, duration=self.speed)
        anim.start(self.obst_top)
        anim.start(self.obst_bottom)

    def get_obstacles(self):
        return self.children


''' Ground(Widget)
loads 2 images for ground and resets them after they leave the screen'''


class Ground(Widget):
    def __init__(self):
        super(Ground, self).__init__()
        settings = LEVELS[LEVEL]['ground']
        self.ground_1 = load_image(settings[0])
        self.ground_2 = load_image(settings[1], x=self.ground_1.width)
        self.add_widget(self.ground_1)
        self.add_widget(self.ground_2)
        self.run = Clock.schedule_interval(lambda dt: self.update(), 1 / 60.0)

    def update(self):
        for each in [self.ground_1, self.ground_2]:
            if each.right < 0:
                each.x += each.width * 2
            each.x -= WINDOW_SIZE[0] * 0.0002


''' Player(Widget)
Load player image, flames image, and boost audio
controls player movement gravity ect.
also does level starting player enter animation'''


class Player(Widget):
    def __init__(self):
        super(Player, self).__init__()
        self.player_lock = True
        self.boosting = False
        self.player = load_gif('player1', 0, pos=(WINDOW_SIZE[0] * 0.30, WINDOW_SIZE[1] / 2))
        self.flames = load_gif('flames1')
        self.flames.pos = self.player.x, self.player.y - self.flames.height
        self.add_widget(self.player, 0)
        self.add_widget(self.flames, 1)
        self.boost_sound = None
        if 'boots' in AUDIO and len(AUDIO['boots']) > 1:
            self.boost_sound = SoundLoader.load(AUDIO['boots'][1])
        elif 'boots' in AUDIO and len(AUDIO['boots']) > 0:
            self.boost_sound = SoundLoader.load(AUDIO['boots'][0])

        if self.boost_sound:
            self.set_boost_volume('low')
            self.sound_loop = Clock.schedule_interval(lambda dt: self.boost_sound.seek(1), 10)
            self.boost_sound.play()

        self.velocity = 2.0
        self.gravity = 0.0013 * WINDOW_SIZE[1]
        self.boost = 0.0013 * WINDOW_SIZE[1]

    def update(self):
        if self.boosting and WINDOW_SIZE[1] * 0.02 > self.velocity:
            self.velocity += self.boost
        else:
            self.velocity -= self.gravity

        if self.player_lock:
            self.player.y = WINDOW_SIZE[1] / 2
            self.velocity = 2
        else:
            self.player.y += self.velocity
        self.flames.pos = self.player.pos[0], self.player.pos[1] - self.flames.height

    def set_boost(self, boost_state):
        self.boosting = boost_state
        if boost_state:
            self.set_boost_volume('high')
            if 'flame2' in GIFS and GIFS['flame2']:
                self.flames.source = GIFS['flame2'][0]
                self.flames.height = self.flames.texture_size[1] * RATIO
        else:
            self.set_boost_volume('low')
            if 'flames1' in GIFS and GIFS['flames1']:
                self.flames.source = GIFS['flames1'][0]
                self.flames.height = self.flames.texture_size[1] * RATIO

    def get_player(self):
        return self.children[0]

    def set_boost_volume(self, state):
        if not self.boost_sound:
            return
        high = 0.20
        low = 0.05
        if state == 'low':
            self.boost_sound.volume = low
            self.boost_sound.play()
        elif state == 'high':
            self.boost_sound.volume = high
            self.boost_sound.play()

    def enter_animation(self, animation=None, widget=None):
        self.player.x = -WINDOW_SIZE[1] * 0.1
        self.flames.x = self.player.x
        anim = Animation(x=WINDOW_SIZE[0] * 0.3, duration=4)
        anim.start(self.player)
        anim.start(self.flames)


''' Clouds(widget)
create clouds and animate them
random starting x,y, speed, and image'''


class Clouds(Widget):
    def __init__(self):
        super(Clouds, self).__init__()
        self.cloud_list = []
        self.speeds = []  # list for clouds random speeds
        for n in range(0, 3):  # number of clouds
            cloud = load_image('cloud', index=-1)
            cloud.x = randrange(0, max(1, int(WINDOW_SIZE[0] / 1.5) * (n + 1)))
            cloud.y = WINDOW_SIZE[1] * (randrange(50, 90) * .01)
            self.cloud_list.append(cloud)
            self.speeds.append(randrange(1, 4))
            self.add_widget(self.cloud_list[n])

    def update(self):
        for n, each in enumerate(self.cloud_list):
            if each.right > 0:
                each.x -= self.speeds[n]
            else:
                each.source = choice(IMAGES['cloud'])
                self.speeds[n] = randrange(1, 4)
                each.size = each.texture_size[0] * RATIO, each.texture_size[1] * RATIO
                each.x = randrange(int(WINDOW_SIZE[0]), max(int(WINDOW_SIZE[0]) + 1, int(WINDOW_SIZE[0] * 1.5)))
                each.y = WINDOW_SIZE[1] * (randrange(50, 90) * .01)


''' load_assets()
go through assets folder and put all audio and image file locations into a dict'''


def load_assets():
    audio = {}
    images = {}
    gifs = {}

    def get_dict(_dict, folder, extension):
        for _file in sorted(glob(join(dirname(__file__), "assets", folder, extension))):
            name = basename(_file[:-4]).split("_")[0]
            if name in _dict:
                _dict[name].append(_file)
            else:
                _dict[name] = [_file]

    get_dict(audio, 'sounds', '*.wav')
    get_dict(images, 'images', '*.png')
    get_dict(gifs, 'gifs', '*.gif')
    return audio, images, gifs


''' load_image()
simplify loading of images by setting defaults and setting image size'''


def load_image(source, index=0, stretch=True, _ratio=True, **kwargs):
    if index < 0:
        index = choice(range(len(IMAGES[source])))
    try:
        image = Image(source=IMAGES[source][index], allow_stretch=stretch, keep_ratio=_ratio, **kwargs)
        image.size = image.texture_size[0] * RATIO, image.texture_size[1] * RATIO
        return image
    except Exception as e:
        print("Can't load image name:[%s] index:[%s]: %s" % (source, index, e))


def load_gif(source, index=0, stretch=True, _ratio=True, **kwargs):
    if index < 0:
        index = choice(range(len(GIFS[source])))
    try:
        image = Image(source=GIFS[source][index], allow_stretch=stretch, keep_ratio=_ratio, **kwargs)
        image.size = image.texture_size[0] * RATIO, image.texture_size[1] * RATIO
        return image
    except Exception as e:
        print("Can't load gif name:[%s] index:[%s]: %s" % (source, index, e))


'''Level(object)
creates obstacles controls difficulty and score'''


class Level(object):
    def __init__(self):
        self.settings = LEVELS[LEVEL]['Level']
        self.score = 0.0
        self.count = 0
        self.difficulty = 2
        self.obstacles = []
        self.gems = []
        self.spacing = self.settings[1]

    def update(self):
        self.score += self.settings[0]
        self.count += 1
        if self.count > self.spacing - self.difficulty:
            self.count = 0
            if self.difficulty < self.spacing - 40:
                self.difficulty += 2
            self.obstacles.append(Obstacles(self.difficulty))
        elif self.count == (self.spacing - self.difficulty - 10) and randrange(0, 3) == 0:
            self.gems.append(Gems())

        for obstacle in self.obstacles[:]:
            if obstacle.obst_top.right <= 0:
                obstacle.clear_widgets()
                self.obstacles.remove(obstacle)

        for gem in self.gems[:]:
            if gem.gem.right <= 0:
                gem.clear_widgets()
                self.gems.remove(gem)

        return self.obstacles, self.gems


''' collision(player, obstacles, gems)
checks player collision against obstacles, boundaries, and gems returns string and if gem returns gem also'''


def collision(player, obstacles, gems):
    for obstacle in obstacles:
        ob1, ob2 = obstacle.get_obstacles()
        if player.collide_widget(ob1) or player.collide_widget(ob2):
            return 'obstacle', None
    for gem in gems:
        _gem = gem.get_gem()
        if player.collide_widget(_gem):
            return 'gem', gem
    if not (WINDOW_SIZE[1] * 1.2 > player.y > -player.height * 2):
        return 'leftScreen', None
    else:
        return None, None


''' LoadingAnimation(player)
moves the player around a bit on the loading screen'''


class LoadingAnimation(Player):
    def __init__(self):
        super(LoadingAnimation, self).__init__()

    def start_animation(self):
        self.player.size = self.player.texture_size[0] * RATIO * 0.1, self.player.texture_size[1] * RATIO * 0.1
        self.player.pos = (0, 0)
        anim1 = Animation(pos=(WINDOW_SIZE[0] * .20, WINDOW_SIZE[1] * 0.38),
                          size=(self.player.texture_size[0] * RATIO, self.player.texture_size[1] * RATIO), duration=2.0)
        self.flames.size = self.flames.texture_size[0] * RATIO * 0.1, self.flames.texture_size[1] * RATIO * 0.1
        self.flames.top = self.player.y
        self.flames.x = self.player.x
        anim2 = Animation(pos=(WINDOW_SIZE[0] * .20, WINDOW_SIZE[1] * 0.38 - self.flames.texture_size[1] * RATIO),
                          size=(self.flames.texture_size[0] * RATIO, self.flames.texture_size[1] * RATIO), duration=2.0)
        anim1 += Animation(pos=(WINDOW_SIZE[0], WINDOW_SIZE[1] * 0.5), duration=2)
        anim2 += Animation(pos=(WINDOW_SIZE[0], WINDOW_SIZE[1] * 0.5 - self.flames.texture_size[1] * RATIO), duration=2)
        anim1.bind(on_complete=partial(self.enter_animation))
        anim1.start(self.player)
        anim2.start(self.flames)

    def enter_animation(self, animation=None, widget=None):
        self.player.x = -WINDOW_SIZE[1] * 0.1
        self.flames.x = self.player.x
        anim = Animation(x=WINDOW_SIZE[0] * 0.3, duration=3)
        anim.start(self.player)
        anim.start(self.flames)


class TitleScreen(Screen):
    def on_enter(self, *args):
        self.init()

    def on_leave(self, *args):
        if hasattr(self, 'run'):
            self.run.cancel()
        self.render.clear_widgets()
        self.clear_widgets()

    def init(self):
        self.lock = True
        self.render = Widget()
        self.add_widget(load_image(LEVELS[LEVEL]['background'], stretch=True, _ratio=False))
        self.title = load_image('title', 0)
        self.title.center = WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.75
        self.title_shadow = load_image('titleshadow', 0)
        self.title_shadow.center = WINDOW_SIZE[0] / 2 + 5, WINDOW_SIZE[1] * 0.75 - 5
        self.render.add_widget(self.title_shadow)
        self.render.add_widget(self.title, canvas='after')
        self.clouds = Clouds()
        self.render.add_widget(self.clouds, canvas='before')
        self.ground = Ground()
        self.render.add_widget(self.ground, canvas='before')
        self.player_anim = LoadingAnimation()
        self.player_anim.start_animation()
        self.render.add_widget(self.player_anim)
        tap_text = shadow_text('Tap to Start!', (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.35), offset=5, size=40,
                               color1=yellow, color2=dark_grey)
        self.render.add_widget(tap_text[0], canvas='after')
        self.render.add_widget(tap_text[1], canvas='after')
        jono = shadow_text('Jono 2017', (WINDOW_SIZE[0] * 0.90, WINDOW_SIZE[1] * 0.05), offset=3, size=15,
                           color1=blue_grey, color2=black)
        self.render.add_widget(jono[0], canvas='after')
        self.render.add_widget(jono[1], canvas='after')
        alpha = shadow_text('Version: %s' % __version__, (WINDOW_SIZE[0] * 0.90, WINDOW_SIZE[1] * 0.02), offset=3,
                            size=16, color1=blue_grey, color2=black)
        self.render.add_widget(alpha[0], canvas='after')
        self.render.add_widget(alpha[1], canvas='after')
        self.add_widget(self.render)
        self.lock_time = Clock.schedule_once(lambda dt: self.toggle_lock(), 0.5)
        self.run = Clock.schedule_interval(lambda dt: self.update(), 1.0 / 60.0)

    def on_touch_down(self, touch):
        if not self.lock:
            self.manager.current = 'LEVEL'

    def update(self):
        self.clouds.update()

    def toggle_lock(self):
        self.lock = not self.lock


class LevelScreen(Screen):
    def on_enter(self, *args):
        self.init()

    def on_leave(self, *args):
        if hasattr(self, 'run'):
            self.run.cancel()
        self.clear_widgets()

    def init(self):
        self.add_widget(load_image(LEVELS[LEVEL]['background'], stretch=True, _ratio=False))
        side_pad = (WINDOW_SIZE[0] * 0.07) * X_RATIO
        top_pad = (WINDOW_SIZE[1] * 0.09) * X_RATIO
        layout = GridLayout(cols=2, rows=2, padding=(side_pad, top_pad, side_pad, top_pad / 3),
                            spacing=WINDOW_SIZE[0] * 0.05)
        self.unlock_str = ()
        _lvl1, _lvl2, _lvl3, _lvl4, _locktup = self.unlocks()
        self.button_1 = Button(background_normal=IMAGES[(LEVELS['level1']['Level'][_locktup[0]])][0],
                               text=_lvl1, font_size=56, strip=False, color=yellow, bold=True)
        self.button_1.bind(on_press=partial(self.go_to_level, 'ONE'))
        self.button_2 = Button(background_normal=IMAGES[(LEVELS['level2']['Level'][_locktup[1]])][0],
                               text=_lvl2, font_size=56, strip=False, color=yellow, bold=True)
        self.button_2.bind(on_press=partial(self.go_to_level, 'TWO'))
        self.button_3 = Button(background_normal=IMAGES[(LEVELS['level3']['Level'][_locktup[2]])][0],
                               text=_lvl3, font_size=56, strip=False, color=yellow, bold=True)
        self.button_3.bind(on_press=partial(self.go_to_level, 'THREE'))
        self.button_4 = Button(background_normal=IMAGES[(LEVELS['level4']['Level'][_locktup[3]])][0],
                               text=_lvl4, font_size=56, strip=False, color=yellow, bold=True)
        self.button_4.bind(on_press=partial(self.go_to_level, 'FOUR'))
        layout.add_widget(self.button_1)
        layout.add_widget(self.button_2)
        layout.add_widget(self.button_3)
        layout.add_widget(self.button_4)
        self.add_widget(layout)
        self.high_score_str = "High Score: %s" % HIGHSCORE
        self.high_score = shadow_text(self.high_score_str, (WINDOW_SIZE[0] * 0.15, WINDOW_SIZE[1] * 0.95),
                                      offset=3, size=25, align='leftcenter')
        self.add_widget(self.high_score[0])
        self.add_widget(self.high_score[1])
        self.gems_str = "Gems: %s" % GEMS
        self.gems_text = shadow_text(self.gems_str, (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.95),
                                     offset=3, size=25)
        self.add_widget(self.gems_text[0])
        self.add_widget(self.gems_text[1])

        self.run = Clock.schedule_interval(lambda dt: self.update(), 1.0 / 60.0)

    def update(self):
        pass

    def go_to_level(self, level, *args):
        global LEVEL, UNLOCKS, GEMS
        if level == 'ONE':
            if UNLOCKS[0]:
                LEVEL = 'level1'
                self.manager.current = 'GAME'
            elif GEMS >= 0:
                GEMS -= 0
                UNLOCKS[0] = 1
                STORE.put('Unlocks', Unlocked=UNLOCKS)
                STORE.put('Gems', Total=GEMS)
                self.init()
            else:
                return
        if level == 'TWO':
            if UNLOCKS[1]:
                LEVEL = 'level2'
                self.manager.current = 'GAME'
            elif GEMS >= 50:
                GEMS -= 50
                UNLOCKS[1] = 1
                STORE.put('Unlocks', Unlocked=UNLOCKS)
                STORE.put('Gems', Total=GEMS)
                self.init()
            else:
                return
        if level == 'THREE':
            if UNLOCKS[2]:
                LEVEL = 'level3'
                self.manager.current = 'GAME'
            elif GEMS >= 100:
                GEMS -= 100
                UNLOCKS[2] = 1
                STORE.put('Unlocks', Unlocked=UNLOCKS)
                STORE.put('Gems', Total=GEMS)
                self.init()
            else:
                return
        if level == 'FOUR':
            if UNLOCKS[3]:
                LEVEL = 'level4'
                self.manager.current = 'GAME'
            elif GEMS >= 200:
                GEMS -= 200
                UNLOCKS[3] = 1
                STORE.put('Unlocks', Unlocked=UNLOCKS)
                STORE.put('Gems', Total=GEMS)
                self.init()
            else:
                return

    def unlocks(self):
        if UNLOCKS[0]:
            _str1 = 'LEVEL 1\n START'
            _lock1 = 2
        else:
            _str1 = 'UNLOCK FOR\n     0 GEMS'
            _lock1 = 3
        if UNLOCKS[1]:
            _str2 = 'LEVEL 2\n START'
            _lock2 = 2
        else:
            _str2 = 'UNLOCK FOR\n    50 GEMS'
            _lock2 = 3
        if UNLOCKS[2]:
            _str3 = 'LEVEL 3\n START'
            _lock3 = 2
        else:
            _str3 = 'UNLOCK FOR\n   100 GEMS'
            _lock3 = 3
        if UNLOCKS[3]:
            _str4 = 'LEVEL 4\n START'
            _lock4 = 2
        else:
            _str4 = 'UNLOCK FOR\n   200 GEMS'
            _lock4 = 3
        _locktup = (_lock1, _lock2, _lock3, _lock4)
        return _str1, _str2, _str3, _str4, _locktup


class GameScreen(Screen):
    def on_enter(self, *args):
        self.init()
        self.add_background()
        self.render.add_widget(self.player, canvas='after')
        self.score_str = "Score: %s" % self.level.score
        self.score = shadow_text(self.score_str, (WINDOW_SIZE[0] * 0.85, WINDOW_SIZE[1] * 0.95), offset=3, size=25)
        self.render.add_widget(self.score[0], canvas='after')
        self.render.add_widget(self.score[1], canvas='after')
        self.high_score_str = "High Score: %s" % HIGHSCORE
        self.high_score = shadow_text(self.high_score_str, (WINDOW_SIZE[0] * 0.15, WINDOW_SIZE[1] * 0.95),
                                      offset=3, size=25, align='leftcenter')
        self.render.add_widget(self.high_score[0], canvas='after')
        self.render.add_widget(self.high_score[1], canvas='after')
        self.gems_str = "Gems: %s" % GEMS
        self.gems_text = shadow_text(self.gems_str, (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.95),
                                     offset=3, size=25)
        self.render.add_widget(self.gems_text[0], canvas='after')
        self.render.add_widget(self.gems_text[1], canvas='after')
        self.count = shadow_text('', (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.65), size=50)
        self.render.add_widget(self.count[0], canvas='after')
        self.render.add_widget(self.count[1], canvas='after')
        self.add_widget(self.render)
        self.player.enter_animation()
        self.start_countdown()
        self.starting = Clock.schedule_interval(lambda dt: self.start_countdown(), 1)
        self.run = Clock.schedule_interval(lambda dt: self.update(), 1.0 / 60.0)

    def on_leave(self, *args):
        if hasattr(self, 'player') and self.player and self.player.boost_sound:
            self.player.boost_sound.stop()
        if hasattr(self, 'run'):
            self.run.cancel()
        if hasattr(self, 'starting'):
            Clock.unschedule(self.starting)
        self.render.clear_widgets()
        self.clear_widgets()

    def init(self):
        self.lock = True
        self.explosion = SoundLoader.load(AUDIO['explosion'][0]) if 'explosion' in AUDIO else None
        self.beep1 = SoundLoader.load(AUDIO['beep1'][0]) if 'beep1' in AUDIO else None
        self.beep2 = SoundLoader.load(AUDIO['beep2'][0]) if 'beep2' in AUDIO else None
        self.gem_sound = SoundLoader.load(AUDIO['pickupGem1'][0]) if 'pickupGem1' in AUDIO else None
        if self.explosion:
            self.explosion.volume = 0.8
        if self.beep1:
            self.beep1.volume = 0.8
        if self.beep2:
            self.beep2.volume = 1
        self.render = Widget()
        self.clouds = Clouds()
        self.ground = Ground()
        self.level = Level()
        self.player = Player()
        self.obstacle_list = []
        self.gems_list = []
        self.count_str = 3

    def on_touch_down(self, touch):
        self.player.set_boost(True)

    def on_touch_up(self, touch):
        self.player.set_boost(False)

    def add_background(self):
        self.add_widget(load_image(LEVELS[LEVEL]['background'], stretch=True, _ratio=False))
        self.render.add_widget(self.clouds)
        self.render.add_widget(self.ground)

    def start_countdown(self):
        _str = ''
        if self.count_str > 0:
            if self.beep1:
                self.beep1.play()
            _str = 'Starting in: %s...' % self.count_str
        elif self.count_str == 0:
            self.lock = False
            if self.beep2:
                self.beep2.play()
            _str = 'START'
        else:
            self.player.player_lock = False
            self.player.update()
            if hasattr(self, 'count'):
                for w in self.count:
                    self.render.remove_widget(w)
            Clock.unschedule(self.starting)
        self.count[0].text = _str
        self.count[1].text = _str
        self.count_str -= 1

    def update(self):
        self.clouds.update()
        self.update_obstacles()
        self.update_score()
        self.player.update()
        self.check_collision()

    def check_collision(self):
        global SCORE, STORE, HIGHSCORE, GEMS
        player = self.player.get_player()
        _type, obj = collision(player, self.obstacle_list, self.gems_list)
        if _type is not None:
            if _type == 'obstacle' or _type == 'leftScreen':
                if self.explosion:
                    self.explosion.play()
                SCORE = int(self.level.score)
                if SCORE > HIGHSCORE:
                    HIGHSCORE = SCORE
                    STORE.put('HighScores', High=HIGHSCORE)
                STORE.put('Gems', Total=GEMS)
                self.manager.current = 'SCOREBOARD'
            elif _type == 'gem':
                if self.gem_sound:
                    self.gem_sound.play()
                GEMS += 1
                self.update_gems()
                if obj in self.gems_list:
                    self.gems_list.remove(obj)
                self.render.remove_widget(obj)

    def update_obstacles(self):
        if not self.lock:
            for each in self.obstacle_list:
                self.render.remove_widget(each)
            for each in self.gems_list:
                self.render.remove_widget(each)
            self.obstacle_list, self.gems_list = self.level.update()
            if self.obstacle_list:
                for each in self.obstacle_list:
                    self.render.add_widget(each)
            if self.gems_list:
                for each in self.gems_list:
                    self.render.add_widget(each)

    def update_score(self):
        self.score_str = "Score: %s" % (int(self.level.score))
        self.score[0].text = self.score_str
        self.score[1].text = self.score_str

    def update_gems(self):
        self.gems_str = "Gems: %s" % GEMS
        self.gems_text[0].text = self.gems_str
        self.gems_text[1].text = self.gems_str


class ScoreboardScreen(Screen):
    def on_enter(self, *args):
        self.init()

    def on_leave(self, *args):
        if hasattr(self, 'run'):
            self.run.cancel()
        self.clear_widgets()

    def init(self):
        self.lock = True
        self.add_widget(load_image(LEVELS[LEVEL]['background'], stretch=True, _ratio=False))
        self.clouds = Clouds()
        self.add_widget(self.clouds)
        self.ground = Ground()
        self.add_widget(self.ground)
        final_text = shadow_text('Final Score:', (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.65), size=50)
        self.add_widget(final_text[0])
        self.add_widget(final_text[1])
        score_text = shadow_text(str(int(SCORE)), (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.55),
                                 size=50, color1=orange)
        self.add_widget(score_text[0])
        self.add_widget(score_text[1])
        self.high_score_str = "High Score: %s" % HIGHSCORE
        self.high_score = shadow_text(self.high_score_str, (WINDOW_SIZE[0] * 0.15, WINDOW_SIZE[1] * 0.95),
                                      offset=3, size=25, align='leftcenter')
        self.add_widget(self.high_score[0])
        self.add_widget(self.high_score[1])
        self.gems_str = "Gems: %s" % GEMS
        self.gems_text = shadow_text(self.gems_str, (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] * 0.95),
                                     offset=3, size=25)
        self.add_widget(self.gems_text[0])
        self.add_widget(self.gems_text[1])
        self.lock_time = Clock.schedule_once(lambda dt: self.toggle_lock(), 1.5)
        self.screen_buttons()
        self.run = Clock.schedule_interval(lambda dt: self.update(), 1.0 / 60.0)

    def update(self):
        self.clouds.update()

    def toggle_lock(self):
        self.lock = not self.lock

    def screen_buttons(self):
        self.button_1 = Button(text='Try Again', font_size=40,
                               pos=(WINDOW_SIZE[0] * 0.1, WINDOW_SIZE[1] * 0.1))
        self.button_1.size_hint = .2, .1
        self.button_1.bind(on_press=partial(self.go_to, 'GAME'))
        self.button_2 = Button(text='Title Screen', font_size=40)
        self.button_2.size_hint = .2, .1
        self.button_2.pos = WINDOW_SIZE[0] * 0.7, WINDOW_SIZE[1] * 0.1
        self.button_2.bind(on_press=partial(self.go_to, 'TITLE'))
        self.add_widget(self.button_1)
        self.add_widget(self.button_2)

    def go_to(self, a_screen, touch):
        if a_screen == 'GAME':
            self.manager.current = 'GAME'
        elif a_screen == 'TITLE':
            self.manager.current = 'TITLE'


''' StateMachine(ScreenManager)
handles different screens so I can easily change between them'''


class StateMachine(ScreenManager):
    score = NumericProperty(0)

    def __init__(self):
        super(StateMachine, self).__init__()
        self.transition = NoTransition()
        self.add_widget(TitleScreen(name='TITLE'))
        self.add_widget(LevelScreen(name='LEVEL'))
        self.add_widget(GameScreen(name='GAME'))
        self.add_widget(ScoreboardScreen(name='SCOREBOARD'))

        self.on_resume()
        self.current = 'TITLE'

    def on_pause(self):
        return True

    def on_resume(self):
        pass


def store_setup(_dir):
    global STORE, HIGHSCORE, GEMS, UNLOCKS
    STORE = JsonStore(join(_dir, 'data.json'))
    if STORE.exists('Version'):
        try:
            HIGHSCORE = STORE.get('HighScores')['High']
        except KeyError:
            HIGHSCORE = 0
        try:
            GEMS = STORE.get('Gems')['Total']
        except KeyError:
            GEMS = 0
        try:
            UNLOCKS = list(STORE.get('Unlocks')['Unlocked'])
        except KeyError:
            UNLOCKS = [1, 0, 0, 0]
    else:
        STORE.put('Version', Version=__version__)
        STORE.put('HighScores', High=HIGHSCORE)
        STORE.put('Gems', Total=GEMS)
        STORE.put('Unlocks', Unlocked=list(UNLOCKS))


__version__ = '0.5.0'
STORE = None
SCORE = 0
HIGHSCORE = 0
GEMS = 0
UNLOCKS = [1, 0, 0, 0]


class RocketBootsApp(App):

    def build(self):
        global AUDIO, IMAGES, GIFS
        self.icon = join(DIRECTORY, 'icon.png')
        self.title = 'Rocket Boots'
        AUDIO, IMAGES, GIFS = load_assets()
        store_setup(self.user_data_dir)
        self.music = SoundLoader.load(join(DIRECTORY, 'sounds', 'Indiekid.wav'))
        if self.music:
            self.music.loop = True
            self.music.play()

        return StateMachine()


if __name__ in ('__main__', '__android__'):
    RocketBootsApp().run()
