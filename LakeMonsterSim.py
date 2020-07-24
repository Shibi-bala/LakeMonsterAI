import pygame, sys, math

class LakeMonsterSim:
        clock = pygame.time.Clock()
        width = 1024
        height = 720
        radius = 300.0
        goblin = 0.0
        boatx = 0.1 
        boaty = 0.0
        bspeed = 1.0
        gspeeds = [3.5, 4.0, 4.2, 4.4, 4.6]
        gspeed_ix = 0
        speed_mult = 3.0
        
        finished = False
        shouldRender = False

        goblinDist = 300.0
        dist = 300.0
        angle = 0
        vecX = 0
        vecY = 0

        reward = 0
        func = 0
        
        def calcReward(self):
                if self.goblinDist > self.radius:
                        self.reward += (self.goblinDist-self.radius)/self.radius

        
        def render(self,status):
                self.shouldRender = status
        
        def restart(self):
                self.reward = 0
                self.goblin = 0.0
                self.boatx = 0.1 
                self.boaty = 0.0

        pygame.init()
        window = pygame.display.set_mode((width, height)) 

        def clear(self):
                radius_mult = self.bspeed / self.gspeeds[self.gspeed_ix]

                self.window.fill((0,80,0))
                pygame.draw.circle(self.window, (0,0,128), (int(self.width/2), int(self.height/2)), int(self.radius*1.00), 0)
                pygame.draw.circle(self.window, (200,200,200), (int(self.width/2), int(self.height/2)), int(self.radius*radius_mult), 1)

        def redraw(self, draw_text=False,win=False):
                self.clear()

                pygame.draw.circle(self.window, (255,255,255), (int(self.width/2 + self.boatx),int(self.height/2 + self.boaty)), 6, 2)
                pygame.draw.circle(self.window, (255,0,0), (int(self.width/2 + self.radius*math.cos(self.goblin)),int(self.height/2 + self.radius*math.sin(self.goblin))), 6, 0)

                if draw_text:
                        font = pygame.font.Font(None, 72)
                        if win:
                                text = font.render("Escaped!", 1, (255, 255, 255))
                        else:
                                text = font.render("You Were Eaten", 1, (255, 0, 0))
                        textpos = text.get_rect()
                        textpos.centerx = self.window.get_rect().centerx
                        textpos.centery = self.height/2
                        self.window.blit(text, textpos)

                font = pygame.font.Font(None, 48)
                text = font.render("Goblin Speed: " + str(self.gspeeds[self.gspeed_ix]), 1, (255, 255, 255))
                textpos = text.get_rect()
                textpos.centerx = self.width/2
                textpos.centery = self.height - 20
                self.window.blit(text, textpos)
                        
                pygame.display.flip()

        def updateGoblin(self):
                global goblin
                gspeed = self.gspeeds[self.gspeed_ix]
                newang = math.atan2(self.boaty, self.boatx)
                diff = newang - self.goblin
                if diff < math.pi: diff += math.pi*2.0
                if diff > math.pi: diff -= math.pi*2.0
                if abs(diff)*self.radius <= gspeed * self.speed_mult:
                        self.goblin = newang
                else:
                        self.goblin += gspeed * self.speed_mult / self.radius if diff > 0.0 else -gspeed * self.speed_mult / self.radius
                if self.goblin < math.pi: self.goblin += math.pi*2.0
                if self.goblin > math.pi: self.goblin -= math.pi*2.0 

        def moveBoat(self,dx,dy):
                global boatx, boaty
                mag = math.sqrt(dx*dx + dy*dy)+0.001
                
                self.boatx += self.bspeed * self.speed_mult * dx/mag
                self.boaty += self.bspeed * self.speed_mult * dy/mag 
                
        def detectWin(self):
                global gspeed_ix
                if self.boatx*self.boatx + self.boaty*self.boaty > self.radius*self.radius:
                        diff = math.atan2(self.boaty, self.boatx) - self.goblin
                        if diff < math.pi: diff += math.pi*2.0
                        if diff > math.pi: diff -= math.pi*2.0
                        if abs(diff) > 0.000001:
                                self.reward += 10
                        else:
                                self.reward -= 10
                        self.finished = True            

        def updatePos(self):
                global goblinDist, angle,dist
                gx = math.cos(self.goblin)*self.radius
                gy = math.sin(self.goblin)*self.radius
                
                self.angle = math.atan2(gy-self.boaty,gx-self.boatx)
                self.goblinDist = math.sqrt((gy-self.boaty)**2+(gx-self.boatx)**2)
                self.dist = self.radius - math.sqrt((self.boaty)**2+(self.boatx)**2)

        def calcNewVec(self):
                if (self.func != 0):
                        v = self.func(self.dist,self.goblinDist, self.angle)
                        self.vecX = v[0]
                        self.vecY = v[1]
                else:
                        self.vecX = 1
                        self.vecY = 0 
        
        def start(self,steps=-1,moveFunc=0):
                self.func = moveFunc
                self.finished = False
                self.restart()
                t=0
                while t < steps or steps == -1:
                        x = None
                        for event in pygame.event.get(): 
                                if event.type == pygame.QUIT: 
                                        sys.exit(0)
                        self.calcReward()
                        self.moveBoat(self.vecX,self.vecY)
                        self.calcNewVec()
                        self.updateGoblin()
                        self.detectWin()
                        if self.shouldRender:
                                self.redraw()
                        self.updatePos()
                        #self.clock.tick(20)
                        if self.finished:
                                break
                        t+=1
