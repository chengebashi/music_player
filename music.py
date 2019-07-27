import pygame
from pygame.locals import *
import os
import os.path

SCREEN_SIZE = (800, 600)   #画出一个800*600的界面
# 存放音乐文件的位置
MUSIC_PATH = "F:\CloudMusic"

def get_music(path):
    raw_filenames = os.listdir(path)  # 从文件夹来读取所有的音乐文件
    music_files = []    #定义一个列表存放文件夹里的歌曲
    for filename in raw_filenames:  #遍历所有音乐文件
        if filename.lower().endswith('.mp3'):   #删选后缀为.mp3格式的歌曲
            music_files.append(os.path.join(MUSIC_PATH, filename))   #将歌曲文件路径拼接成为绝对地址，放在music_files中

    return sorted(music_files)  #返回按文件名排序的歌曲列表


class Button(object):  #这个类是一个按钮，判断按钮是否被按上

    def __init__(self, image_filename, position):  #初始化
        self.position = position
        self.image = pygame.image.load(image_filename)

    def render(self, surface):
        # 家常便饭的代码了
        x, y = self.position
        w, h = self.image.get_size()
        x -= w / 2
        y -= h / 2
        surface.blit(self.image, (x, y))

    def is_over(self, point):
        # 如果point在自身范围内，返回True
        point_x, point_y = point
        x, y = self.position
        w, h = self.image.get_size()
        x -= w / 2
        y -= h / 2

        in_x = point_x >= x and point_x < x + w
        in_y = point_y >= y and point_y < y + h
        return in_x and in_y


def run():
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    #pygame.mixer.pre_init对应的四个参数 (frequency, size, stereo, buffer)
    # frequency – 声音文件的采样率   size – 量化精度  stereo – 立体声效果，1：mono，2：stereo   buffer – 缓冲大小，2的倍数

    pygame.init()  #初始化
    close = False
    screen = pygame.display.set_mode(SCREEN_SIZE, 0)
    img = pygame.image.load("images/sea.jpg")
    # screen.blit(img, (0, 0))
    #font = pygame.font.SysFont("default_font", 50, False)
    # 为了显示中文，我这里使用了这个字体
    font = pygame.font.SysFont("simsunnsimsun", 30, False)

    #定位按钮坐标
    x = 80
    y = 60
    button_width = 80   #按钮间距
    buttons = {}
    buttons["play"] = Button("images/play.png", (x, y))
    buttons["pause"] = Button("images/pause.png", (x, y+ button_width * 1))
    buttons["stop"] = Button("images/stop.png", (x, y+ button_width * 2))
    buttons["prev"] = Button("images/prev.png", (x, y+ button_width * 3))
    buttons["next"] = Button("images/next.png", (x, y+ button_width * 4))

    music_filenames = get_music(MUSIC_PATH)
    if len(music_filenames) == 0:
        print("No music files found in ", MUSIC_PATH)
        return

    #white = (255, 255, 200)   #填充色白色，但是被背景图片代替掉了，所以注释
    label_surfaces = []
    # 一系列的文件名render
    for filename in music_filenames:
        txt = os.path.split(filename)[-1]
        print("Track:", txt)
        # 这是简体中文Windows下的文件编码，根据自己系统情况请酌情更改
        #        txt = txt.split('.')[0].decode('gb2312')
        surface = font.render(txt, True, (100, 0, 100))
        label_surfaces.append(surface)

    current_track = 0
    max_tracks = len(music_filenames)
    pygame.mixer.music.load(music_filenames[current_track])

    clock = pygame.time.Clock()
    playing = False
    paused = False

    # USEREVENT作为一个事件，捕捉鼠标动作，并且显示出来鼠标刚刚点击的事件
    TRACK_END = USEREVENT + 1
    pygame.mixer.music.set_endevent(TRACK_END)

    while True:

        button_pressed = None

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                exit
                close = True

            if event.type == MOUSEBUTTONDOWN:

                # 判断哪个按钮被按下
                for button_name, button in buttons.items():
                    if button.is_over(event.pos):
                        print(button_name, "pressed")
                        button_pressed = button_name
                        break

            if event.type == TRACK_END:
                # 如果一曲播放结束，就“模拟”按下"next"
                button_pressed = "next"
        if close:
            break


        #当按钮时间不为空，则判断是哪个按钮正在进行动作
        if button_pressed is not None:

            if button_pressed == "next":
                current_track = (current_track + 1) % max_tracks
                pygame.mixer.music.load(music_filenames[current_track])
                if playing:
                    pygame.mixer.music.play()

            elif button_pressed == "prev":

                # prev的处理方法：
                # 已经播放超过3秒，从头开始，否则就播放上一曲
                if pygame.mixer.music.get_pos() > 3000:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                else:
                    current_track = (current_track - 1) % max_tracks
                    pygame.mixer.music.load(music_filenames[current_track])
                    if playing:
                        pygame.mixer.music.play()

            elif button_pressed == "pause":
                if paused:
                    pygame.mixer.music.unpause()
                    paused = False
                else:
                    pygame.mixer.music.pause()
                    paused = True

            elif button_pressed == "stop":
                pygame.mixer.music.stop()
                playing = False

            elif button_pressed == "play":
                if paused:
                    pygame.mixer.music.unpause()
                    paused = False
                else:
                    if not playing:
                        pygame.mixer.music.play()
                        playing = True

        screen.blit(img, (0, 0))
        #screen.fill(white)  #填充色白色，但是被背景图片代替掉了，所以注释

        # 写一下当前歌名
        label = label_surfaces[current_track]
        w, h = label.get_size()
        screen_w = SCREEN_SIZE[0]
        screen.blit(label, ((screen_w - w) / 2, 30))

        # 画所有按钮
        for button in buttons.values():
            button.render(screen)

        # 因为基本是不动的，这里帧率设的很低
        clock.tick(5)
        pygame.display.update()

if __name__ == "__main__":
    run()