import pygame
import datetime

from pygame.sprite import Sprite
from apscheduler.schedulers.background import BackgroundScheduler
from random import randint

from bullets.ship.ship_bullet import ShipBullet
from bullets.ship.ship_rocket import ShipRocket
from bullets.ship.ship_missile import ShipMissile

class Ship(Sprite):
    """管理飞船的类"""
    
    def __init__(self, ai_game):
        """初始化飞船并设置其初始位置"""
        super().__init__()
        self.screen = ai_game.screen
        self.ai_game = ai_game
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings
        self.player = ai_game.player

        # 飞船移动标志（刚开始不移动）
        self.moving_right = False
        self.moving_left = False

        # 加载飞船图像并获取其外接矩形
        self.image = pygame.image.load('images/processed_BluePlane.png')
        self.rect = self.image.get_rect()

        # 每艘新飞船都放在屏幕底部的中央
        self.rect.midbottom = self.screen_rect.midbottom
        # 在飞船的位置属性x中，存放一个浮点数
        self.x = float(self.rect.x)

        # 设置飞船是否隐身
        self.stealth_mode = False
        # 设置飞船是否显示
        self.ship_show = True

    def blitme(self):
        """在指定位置绘制飞船"""
        if self.ship_show:
            self.screen.blit(self.image, self.rect)

    def ship_center(self):
        """当飞船被击毁后让其重新居中"""
        self.rect.midbottom = self.screen_rect.midbottom
        # 不要忘记将self.x也重置，因为它才是负责计算飞船的位置
        self.x = float(self.rect.x)
        # 重置状态信息
        self.stealth_mode = False
        self.ship_show = True

    def fire_bullet(self):
        """飞船发射子弹"""
        if len(self.ai_game.ship_bullets) < self.settings.bullet_allow:
            new_bullet = ShipBullet(self.ai_game)
            self.ai_game.ship_bullets.add(new_bullet)
            self.player.play('fire_bullet', 0, 1)

    def launch_rocket(self):
        """"飞船发射火箭弹（一次同时发射左右两枚）"""
        if self.ship_show:
            # 创建两枚火箭弹，并标明其位置
            left_rocket = ShipRocket(self, 'left')
            right_rocket = ShipRocket(self,'right')
            
            # 将火箭弹加入到编组中
            self.ai_game.ship_bullets.add(left_rocket)
            self.ai_game.ship_bullets.add(right_rocket)

    def launch_missile(self):
        """飞船发射可以自动判断并跟踪最近外星人的导弹"""
        if self.ship_show:
            # 从外星舰队中随机的选择一个外星人作为射击目标
            aliens = self.ai_game.aliens.sprites()
            if len(aliens) > 0:
                # randint(a, b)函数返回包含a,b两端的值，所以作为列表索引b端要减1
                target = aliens[randint(0, len(aliens) - 1)]
                
                # 创建导弹
                missile = ShipMissile(self.ai_game)
                # 锁定目标
                missile.lock_target(target)
                # 加入飞船子弹编组
                self.ai_game.ship_bullets.add(missile)

    def update(self):
        """根据移动标志，调整飞船位置"""
        # 更新飞船的x属性的值，而不是其rect对象的x属性的值
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # 根据self.x更新飞船的rect对象
        self.rect.x = self.x

    def turn_on_stealth_mode(self):
        """开启飞船为隐身模式"""
        self.stealth_mode = True
        print("Start time: %s" % \
           datetime.datetime.now().strftime("%H:%M:%S"))
        # 创建任务调度器
        self.sched = BackgroundScheduler()

        # 添加任务并设置每隔0.1秒执行一次任务，并设置为多线程并发，最大线程数为3
        self.sched.add_job(
            self._ship_flash, 'interval', seconds=0.1, max_instances=3)
        
        # 隐身模式启动10秒后自动关闭
        # self.sched.add_job(
        #     self.turn_off_stealth_mode, 'interval', seconds=10, max_instances=3)
        self.sched.start()

    def turn_off_stealth_mode(self):
        """关闭飞船的隐身模式"""
        self.stealth_mode = False
        self.ship_show = True
        self.sched.remove_all_jobs()

    def _ship_flash(self):
        """不断的变换ship_show的值，在绘制飞船时会呈现闪烁的效果"""
        if self.ship_show:
            self.ship_show = False
        else:
            self.ship_show = True

        