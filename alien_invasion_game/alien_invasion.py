# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 19:36:21 2024

@author: yiyao
"""

from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard

from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button

running = True

class AlienInvasion:
    """管理游戏资源和行为的类"""
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.clock = pygame.time.Clock() #pygame.time module Clock() object
        self.settings = Settings() # Settings() object
        
        #让游戏一开始处于一个非活动状态
        self.game_active = False #boolean data type
        
        #全屏模式
        """
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        """
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # function for setting the display mode
        self.settings.screen_width = self.screen.get_rect().width # screen object's method that returns an integer
        self.settings.screen_width = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        #创建一个用于储存游戏统计星系的实例,记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group() # Object
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
        #创造play按钮
        self.play_button = Button(self, "Play")
        
        
        
        
    def run_game(self):
        """开始游戏的主循环"""
        global running
        while running:
            """监听键盘和鼠标事件"""
            self._check_events()
            
            if self.game_active: # returns a boolean data type True or False
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()  
            
            #让最近绘制的屏幕可见
            pygame.display.flip()
            self.clock.tick(60)
            
        
                    
        
    def _check_events(self):
         """响应案件和鼠标事件"""
         global running
         for event in pygame.event.get(): # a function in the module "event" that returns a list
            if event.type == pygame.QUIT: # boolean type
                running=False
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
    def _check_play_button(self, mouse_pos):
        """在玩家点击play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos) # methode
        if button_clicked and not self.game_active:
            #还原游戏设置
            self.settings.initialize_dynamic_settings()
            
            #重置游戏统计信息
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            
            self.game_active = True
            
            #清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()
            
            #创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()
            
            #隐藏光标
            pygame.mouse.set_visible(False)
     
    def _check_keydown_events(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            global running
            running=False
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应释放"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
    def _fire_bullet(self):
        """创造一颗子弹，并将其加入编组bullets"""
        if len(self.bullets) < self.settings.bullets_allowed: # object's attribute that returns an integer
           new_bullet = Bullet(self)
           self.bullets.add(new_bullet)
          
           
    def _update_bullets(self):
        """更新子弹的位置并删除已消失的子弹"""
        #更新子弹的位置
        self.bullets.update()
        
        #删除已消失的子弹
        for bullet in self.bullets.copy(): # object that returns a lst
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
                
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人的碰撞"""
        #删除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True) # funtion in the object (sprite) that returns a dictionary
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            
        
        if not self.aliens:
            #删除现有的子弹并创建一个新的外星舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            #提高等级
            self.stats.level += 1
            self.sb.prep_level()
            

    
    def _create_fleet(self):
        """创建一个外星舰队"""
        #创造一个外星人，再不断添加，直到没有空间添加外星人为止
        #外星人的间距为外星人的宽度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 6 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
                
            #添加一行外星人后，重置x值并递增y值
            current_x = alien_width
            current_y += 2 * alien_height
            
    def _create_alien(self, x_position, y_position):
        """创建一个外星人，并将其加入外形舰队"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)
    
    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites(): # object that returns a list
            if alien.check_edges(): # method that returns a boolean type
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """将整个外星舰队向下移动，并改编他们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _ship_hit(self):
        """响应飞船和外星人的碰撞"""
        if self.stats.ships_left > 0:
            #将ship_left减1，并更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            #清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()
            
            #创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()
            
            #暂停
            sleep(0.5)
            
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)
        
    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕的下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #像飞船被撞到一样进行处理
                self._ship_hit()
                break
        
    def _update_aliens(self):
        """检查是否有外星人位于屏幕边缘，并更新外星舰队中所有外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()
    
        #检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            
        #检查是否有外星人到达了屏幕的下边缘
        self._check_aliens_bottom()
        
        
    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        
        #显示得分
        self.sb.show_score()
        
        #如果游戏处于非游戏状态，就绘制Play按钮
        if not self.game_active:
            self.play_button.draw_button()
            
if __name__ == '__main__':
    """创建游戏实例并运行游戏"""
    ai = AlienInvasion()
    ai.run_game()

    
pygame.quit()