import pygame
import random
import math


class Vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __add__(self, other):
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        return Vec2d(self.x * k, self.y * k)

    def int_pair(self):
        t = (int(self.x), int(self.y))
        return t


class Polyline:
    def __init__(self, drawing_parent):
        self.points = list()
        self.speeds = list()
        self.additional_speed = 2
        self.drawing_parent = drawing_parent

    def add_point_and_speed(self, point_coordinates, point_speed):
        self.points.append(Vec2d(point_coordinates[0], point_coordinates[1]))
        self.speeds.append(point_speed)

    def delete_point(self):
        if len(self.points) > 0:
            self.points.pop(len(self.points) - 1)
            self.speeds.pop(len(self.speeds) - 1)

    def accelerate(self):
        if self.additional_speed < 5:
            self.additional_speed += 1

    def slow_down(self):
        if self.additional_speed > 1:
            self.additional_speed -= 1

    def set_points(self):
        for i in range(len(self.points)):
            self.points[i] += Vec2d(self.speeds[i][0] * 0.5*self.additional_speed,
                                    self.speeds[i][1] * 0.5*self.additional_speed)
            if self.points[i].int_pair()[0] > self.drawing_parent.get_width() \
                    or self.points[i].int_pair()[0] < 0:
                self.speeds[i] = (-self.speeds[i][0], self.speeds[i][1])
            if self.points[i].int_pair()[1] > self.drawing_parent.get_height() \
                    or self.points[i].int_pair()[1] < 0:
                self.speeds[i] = (self.speeds[i][0], -self.speeds[i][1])

    def draw_points(self, color=(255, 255, 255)):
        for p in self.points:
            pygame.draw.circle(self.drawing_parent, color,
                               p.int_pair(), 3)


class Knot(Polyline):
    def __init__(self, drawing_parent, count=35):
        self.count = count
        self.knot_points = list()
        super(Knot, self).__init__(drawing_parent)

    def __set_knot_point(self, points, alpha, deg=None):
        if deg is None:
            deg = len(points) - 1
        if deg == 0:
            return points[0]
        return (points[deg] * alpha) + (self.__set_knot_point(points, alpha, deg - 1) * (1 - alpha))

    def __set_knot_points(self, base_points):
        alpha = 1 / self.count
        res = list()
        for i in range(self.count):
            res.append(self.__set_knot_point(base_points, i * alpha))
        return res

    def set_knot(self, count):
        self.knot_points.clear()
        if len(self.points) > 2:
            self.count = count
            for i in range(-2, len(self.points) - 2):
                temp_points = list()

                temp_points.append((self.points[i] + self.points[i + 1]) * 0.5)
                temp_points.append(self.points[i + 1])
                temp_points.append((self.points[i + 1] + self.points[i + 2]) * 0.5)

                self.knot_points.extend(self.__set_knot_points(temp_points))

    def draw_lines(self, color=(255, 255, 255)):
        for i in range(-1, len(self.knot_points) - 1):
            pygame.draw.line(self.drawing_parent, color,
                             self.knot_points[i].int_pair(), self.knot_points[i + 1].int_pair(), 3)


def draw_help():
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 24)
    font2 = pygame.font.SysFont("serif", 24)
    data = list()
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["N", "Create new polyline"])
    data.append(["Tab", "Select polyline"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["Left click", "Create point"])
    data.append(["Right click", "Delete point"])
    data.append(["W", "accelerate polyline"])
    data.append(["S", "slow down polyline"])
    data.append(["Right click", "Delete point"])
    data.append(["", ""])
    data.append([str(steps), "Current points"])
    data.append([str(len(knot_list)), "Number of polylines"])
    data.append([str(selected + 1), "Selected polyline"])
    data.append([str(max_knot_num), "Max. number of polylines"])

    pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
        (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 50 + 30 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (300, 50 + 30 * i))


if __name__ == "__main__":

    SCREEN_DIM = (800, 600)

    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    steps = 35
    working = True
    show_help = False
    pause = True

    max_knot_num = 5
    knot_list = list()
    knot_list.append(Knot(gameDisplay))
    selected = 0

    hue = 0
    line_color = pygame.Color(0)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    selected += 1
                    if selected >= len(knot_list):
                        selected = 0
                if event.key == pygame.K_n:
                    if len(knot_list) < max_knot_num:
                        knot_list.append(Knot(gameDisplay))
                        selected = len(knot_list) - 1
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    knot_list.clear()
                    knot_list.append(Knot(gameDisplay))
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_w:
                    knot_list[selected].accelerate()
                if event.key == pygame.K_s:
                    knot_list[selected].slow_down()
                if event.key == pygame.K_KP_PLUS:
                    steps += 1
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    steps -= 1 if steps > 1 else 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:   # left mouse button
                    knot_list[selected].add_point_and_speed(event.pos,
                                                            (random.random() * 2, random.random() * 2))
                if event.button == 3:   # right mouse button
                    knot_list[selected].delete_point()
                    if len(knot_list[selected].points) == 0 and len(knot_list) > 1:
                        knot_list.pop(selected)
                        selected = 0

        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        line_color.hsla = (hue, 100, 50, 100)

        for knot in knot_list:
            knot.draw_points()
            knot.set_knot(steps)
            knot.draw_lines(line_color)
        if not pause:
            for knot in knot_list:
                knot.set_points()
        if show_help:
            draw_help()

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
