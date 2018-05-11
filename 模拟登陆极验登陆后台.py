# -*- coding: utf-8 -*-

"""
1. 模拟点击验证按钮
2. 识别滑块缺口位置
3. 拖动滑块到缺口位置
"""
import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GeeTest(object):
    def __init__(self):
        self.email = "craz@sdfsd.com"
        self.password = "asdasddsa"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)

    def open(self):
        self.browser.get("https://account.geetest.com/login")
        email = self.browser.find_element_by_id("email")
        email.send_keys(self.email)
        password = self.browser.find_element_by_id("password")
        password.send_keys(self.password)

    def get_geetest_button(self):
        botton = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_radar_tip")))
        # botton = self.browser.find_element_by_xpath("//div[@class='geetest_wait']/span[2]")
        return botton

    def get_all_img(self):
        """
        获取完整图片
        :return:
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "geetest_canvas_img")))
        print(img.location)
        print(img.size)
        time.sleep(2)
        top = img.location["y"]
        buttom = img.location["y"]+img.size["height"]
        left = img.location["x"]
        right = img.location["x"]+img.size["width"]
        return top, buttom, left, right

    def get_page_screen(self):
        screenshot = self.browser.get_screenshot_as_png()
        im = Image.open(BytesIO(screenshot))
        return im

    def get_captcha_pic(self, name="captcha.png"):
        top, buttom, left, right = self.get_all_img()
        im = self.get_page_screen()
        captcha = im.crop((left, top, right, buttom))
        captcha.save(name)
        return captcha

    def get_slider(self):
        slide = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_slider_button")))
        return slide

    def pixel_is_equal(self, image1, image2, x, y):
        """
        判断两张图片的像素是否相等,不想等即为缺口位置
        :param image1:
        :param image2:
        :param x:
        :param y:
        :return:
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60  # 像素色差
        if abs(pixel1[0]-pixel2[0]) < threshold and abs(pixel1[1]-pixel2[1])< threshold and abs(pixel1[2]-pixel2[2]) <threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口位置
        :param image1:完整图片
        :param image2: 带缺口的图片
        :return:
        """
        left = 60  # 设置一个起始量,因为验证码一般不可能在左边，加快识别速度
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.pixel_is_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def slide_path(self, gap):
        """
        滑动路径
        :param gap:
        :return: 滑动路径
        """
        """
                根据偏移量获取移动轨迹
                :param distance: 偏移量
                :return: 移动轨迹
                """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = gap * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < gap:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        print(track)
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def run(self):
        # 打开浏览器,输入账号密码
        self.open()
        # 获取点击按钮
        botton = self.get_geetest_button()
        botton.click()
        # 获取验证码图片
        image1 = self.get_captcha_pic("image1.png")
        # 点击验证码按钮,呼出残缺的验证码
        slide = self.get_slider()
        slide.click()
        # 获取残缺图片
        image2 = self.get_captcha_pic("image2.png")
        # 获取缺口的位置
        gap = self.get_gap(image1, image2)
        # 减去缺口位移
        gap -= 6
        # 获取滑动路径
        track = self.slide_path(gap)
        # 拖动滑块
        self.move_to_gap(slide, track)
        success = self.wait.until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
        print(success)

        # # 失败后重试
        # if not success:
        #     self.crack()
        # else:
        #     self.login()


if __name__ == "__main__":
    gt = GeeTest()
    gt.run()


