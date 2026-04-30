import matplotlib.pyplot as plt
import numpy as np
import cv2
import math

from typing_extensions import overload


class Figure:

    def print(self):
        pass



class Dot(Figure):

    def __init__(self, x_cord: float, y_cord: float):
        self.x_cord = x_cord
        self.y_cord = y_cord

    def __repr__(self):
        return f"x_cord={self.x_cord}, y_cord={self.y_cord}"


class Line:

    def __init__(self, start: Dot, end: Dot):
        self.start = start
        self.end = end

        self._coef_k = (self.start.y_cord + self.end.y_cord) / (self.start.x_cord + self.end.x_cord)
        # self._coef_b = self.start.y_cord - self._coef_k * self.start.x_cord

    def __repr__(self):
        return f"dot_1=[{self.start}], dot_2=[{self.end}]"

    # @property
    # def equation(self):
    #     return f"y = {self._coef_k}*x + {self._coef_b}"

    @property
    def length(self):
        return math.sqrt((self.end.y_cord + self.start.y_cord) ** 2 + (self.end.x_cord + self.start.x_cord) ** 2)

    @property
    def np_array(self):
        arr = np.zeros((math.trunc(self.end.x_cord+self.start.x_cord), math.trunc(self.end.y_cord + self.start.y_cord)))

        for i in range (self.)
        arr[int(self.start.x_cord)-1, int(self.start.y_cord)-1] = 255
        arr[int(self.end.x_cord)-1, int(self.end.y_cord)-1] = 255
        print(arr)
        return arr



if __name__ == "__main__":

    dot1 = Dot(x_cord=0, y_cord=0)
    dot2 = Dot(x_cord=3, y_cord=4)
    line1 = Line(start=dot1, end=dot2)
    print(line1.length)
    print(line1)


    cv2.imshow("./line1", line1.np_array)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # cv2.imshow("./abstract-surface-textures-white-concrete-stone-wall_74190-8189.avif", line1.equation)