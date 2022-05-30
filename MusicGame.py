# !pip install pygame keyboard

import json
import sys
import threading
import time
from pathlib import Path
from pprint import pprint
from traceback import TracebackException
from typing import (
    Tuple,
    Optional,
    Union,
    List,
    Dict,
    Any, Sequence
)


import pygame as pg
from pygame.mixer import Sound
from pygame.rect import Rect, RectType
from pygame.sprite import Group
from pygame.surface import Surface, SurfaceType
from pygame.time import Clock
import keyboard as kb

# TODO add music
point = 0


# Opening the file and reading the data.
with open("resource/music/10c.json") as f:
    data = json.loads(f.read())
    try:
        # BPM 等を読み込み
        pprint(data)
        BPM = int(data["BPM"])
        LPB = int(data["notes"][0]["LPB"])
        OFFSET = int(data["offset"]) / 1000 + 0.2
        length = len(data["notes"])
        print(length)
        speed = BPM / (60 * LPB * 4)
        print(OFFSET)

    except UnicodeDecodeError as u:
        TracebackException.from_exception(u)
        print("Encordingtype is not UTF8.")

    except KeyError as k:
        TracebackException.from_exception(k)
        print("No data.")


def sound_load(file: Path) -> None:
    """"Loads a sound file."
    The first line is a docstring. It's a string that describes the function. It's
    optional, but it's good practice to include one
    Parameters
    ----------
    file : Path
        The path to the sound file.
    """
    time.sleep(OFFSET)
    Sound(file).play()


class Screen:
    width: int
    height: int

    def __init__(
            self,
            path: Path,
            wh: Tuple[int, int],
            title: str
    ):
        """This class shows screen.
        Parameters
        ----------
        path : Path
            background picture source
        wh : tuple
            screen size (height, width)
        title : str
            The title this game
        """
        self.width, self.height = wh
        self.display: Optional[Surface] = pg.display.set_mode(wh)
        self.rect: Optional[Rect, RectType] = self.display.get_rect()
        self.image = pg.image.load(path)


class Note(pg.sprite.Sprite):
    def __init__(
            self,
            pos: int
    ):
        """Generate note.
        Parameters
        ----------
        pos : int
            the position which start note.
        """
        self.note: Union[Surface, SurfaceType] = pg.image.load("resource/note.png")
        self.image = pg.transform.rotozoom(self.note, 0, 1)
        self.rect = self.note.get_rect()
        self.rect.centerx = pos
        self.rect.centery = 10
        super().__init__()

    def update(self, screen: Screen):
        self.rect.move_ip(0, 4)


class JudgeBar(pg.sprite.Sprite):
    def __init__(
            self,
            screen: Screen,
            width: int,
            pos: Tuple[int, int, int, int],
            color: Tuple[int, int, int],
            vxy: Tuple[int, int]
    ):
        """Draw baseline.
        Parameters
        ----------
        screen : Screen
        width : int
        pos : tuple
        color : tuple
        vxy : tuple
        """
        self.image = pg.Surface((width, 20))
        pg.draw.rect(surface=self.image, color=color, rect=Rect(pos), width=0)
        print(pos)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.centery = 600
        self.vx, self.vy = vxy
        super().__init__()


def notes_manager(screen: Screen, clock: Clock, line: Group) -> None:
    """It generates notes and checks if they collide with the line
    Parameters
    ----------
    screen : Screen
        Screen
    clock : Clock
        Clock
    line : Group
        The line that the notes will collide with.
    """
    global t, flag, now_t, point
    speed = BPM / (60 * LPB * 4)
    print(speed)
    print(length)
    notes = pg.sprite.Group()
    notes_data: List[Dict[str, Any]] = data["notes"]
    t_start = time.perf_counter()
    flag = True
    t = 0
    now = 0
    f = 0
    point = 0
    font = pg.font.Font(None, 55)

    while True:
        # time.sleep(speed)
        if length <= f: break

        # time.sleep(speed)
        now_t = time.perf_counter()
        t = int(4 * (now_t - t_start) // (60 / BPM))
        # print(f"{now_t - t_start} now: {now} | t: {t} | num: {notes_data[f]['num']}")

        if now != t:
            flag = True

        if ((now != t) & (int(notes_data[f]["num"]) == t)) or (f == 0):
            print(f"gen: {f}")
            notes.add(Note(screen.width / 2))
            flag = False
            f += 1

        notes.update(screen=screen)
        notes.draw(screen.display)
        pg.display.update()
        key = pg.key.get_pressed()

        if len(pg.sprite.groupcollide(notes, line, False, False)) != 0:
            gc = pg.sprite.groupcollide(notes, line, False, False)

            if kb.is_pressed("w"):
                for _k, _v in gc.items():
                    _k.kill()
                point += 10
                print("Killed")

        now = t
        clock.tick(100)


def main():
    global point
    # music = sound_load(file="resource/music/10c.wav")
    # point = 0
    clock = Clock()
    screen = Screen(
        path="resource/img_1.png",
        wh=(480, 700),
        title="WWW"
    )
    screen.display.blit(screen.image, (0, 0))

    # 線を作成
    line = pg.sprite.Group()
    line.add(
        JudgeBar(
            screen=screen,
            width=screen.width,
            pos=(0, 0, screen.width, 20),
            color=(250, 0, 0),
            vxy=(2, 2)
        )
    )
    # notes = pg.sprite.Group()
    # notes.add(Note(pos=screen.width / 2))
    k = 0

    t_note = threading.Thread(target=notes_manager, args=(screen, clock, line))
    t_offset = threading.Thread(target=sound_load, args=("resource/music/10c.wav",))
    # t_note.start()
    # t_offset.start()
    font = pg.font.Font(None, 55)

    while True:
        screen.display.blit(screen.image, (0, 0))

        line.draw(screen.display)
        # whileがスタートした最初のループでスレッド作成
        if k == 0:
            t_note.start()
            t_offset.start()
            k = 100

        # notes.update(screen=screen)
        # notes.draw(screen.display)
        # key = pg.event.get()

        text = font.render(str(point), True, (0, 255, 127))
        screen.display.blit(text, (20, 100))

        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
