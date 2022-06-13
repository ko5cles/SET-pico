import board
import time
import terminalio
import displayio
import busio
import time
from adafruit_display_text import label as ll
from adafruit_st7735r import ST7735R
from adafruit_bitmap_font import bitmap_font

select_color=0x00FF00
default_color=0xFFFFFF

# Setting up the display

# Release any resources currently in use for the displays
displayio.release_displays()

spi = busio.SPI(clock=board.GP2,MOSI=board.GP3,MISO=board.GP4)
tft_cs = board.GP5
tft_dc = board.GP6

display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=board.GP9
)

display = ST7735R(display_bus, width=160, height=128, rotation=90, bgr=True)

# Load fonts
font_24=bitmap_font.load_font("/fonts/OpenSans-Regular-24.bdf")
font_18=bitmap_font.load_font("/fonts/OpenSans-Regular-18.bdf")
font_12=bitmap_font.load_font("/fonts/OpenSans-Regular-12.bdf")

# Navigatin class
class button:
    def __init__(self, bound, text, font_size, transit_target, action):
        
        global font_24
        global font_18
        global font_12
        global default_color
        global select_color
        
        self.font_size=font_size
        if font_size==12:
            self.dabel=ll.Label(font_12,text=text)
        elif font_size==18:
            self.dabel=ll.Label(font_18,text=text)
        elif font_size==24:
            self.dabel=ll.Label(font_24,text=text)
            
        self.dabel.color=default_color
        self.dabel.x=bound[0]
        self.dabel.y=(bound[1]+bound[3])//2
        
        self.transit_target=transit_target
        self.action=action
        self.is_selected=False

    def select(self):
        global select_color
        self.is_selected = True
        self.dabel.color=select_color

    def deselect(self):
        global default_color
        self.is_selected = False
        self.dabel.color=default_color

class label:
    def __init__(self, bound, text, font_size):
        
        global font_24
        global font_18
        global font_12
        global default_color
        
        if font_size==12:
            self.dabel=ll.Label(font_12,text=text)
        if font_size==18:
            self.dabel=ll.Label(font_18,text=text)
        elif font_size==24:
            self.dabel=ll.Label(font_24,text=text)
            
        self.dabel.color=default_color
        self.dabel.x=bound[0]
        self.dabel.y=(bound[1]+bound[3])//2
        self.is_selected=False
        
    def select(self):
        global select_color
        self.dabel.color=select_color
        self.is_selected=True
    
    def deselect(self):
        global default_color
        self.dabel.color=default_color
        self.is_selected=False

class rating_bar:

    def __init__(self,bound,text,font_size, max_rating=5, initial_rating=0):
        
        global select_color
        
        self.max_rating=max_rating
        self.cur_rating=initial_rating
        self.is_selected = False
        
        self.button=button((bound[0],bound[1],bound[2]//2,bound[3]), text, font_size, None, None)
        self.label=label(((3*bound[2]-bound[0])//4,bound[1],bound[2],bound[3]),str(initial_rating), font_size)
        self.left_cursor=label(((3*bound[2]-bound[0])//4-15,bound[1],bound[2],bound[3]),"<",font_size)
        self.right_cursor=label(((3*bound[2]-bound[0])//4+15,bound[1],bound[2],bound[3]),">",font_size)
        
        self.left_cursor.dabel.color=select_color
        self.right_cursor.dabel.color=select_color

class screen:
    
    def __init__(self, type_, name):
        
        self.adjunct = [None, None, None, None, None, None, None, None]
        self.cur_pos=None
        self.movable_pos=[]
        self.type=type_
        self.name=name
        self.group=displayio.Group()
        
        if type_ == 'A':
            self.loc = [(0, 0, 53, 24), (53, 0, 106, 24), (106, 0, 159, 24), (0, 24, 160, 104), (0, 104, 53, 128),
                    (53, 104, 106, 128), (106, 104, 159, 128)]
        elif type_ == 'B':
            self.loc = [(0, 0, 80, 128), (80, 0, 160, 32), (80, 32, 160, 64), (80, 64, 160, 96), (80, 96, 160, 128)]
        elif type_ == 'C':
            self.loc = [(0, 0, 106, 32), (106, 0, 159, 32), (0, 32, 160, 64), (0, 64, 160, 96), (0, 96, 53, 128), (53,96,106,128),(106, 96, 160, 128)]
            
        
    def add_button(self, num, text, font_size, transit_target=None, action=None):
            
        b=button(self.loc[num],text,font_size,transit_target,action)
            
        self.adjunct[num]=b
        self.group.append(b.dabel)
            
        self.movable_pos.append(num)
        self.movable_pos.sort()
            
        if self.cur_pos==None:
            self.cur_pos=num
            self.adjunct[num].select()
            
    def add_label(self, num, text, font_size):
        
        l=label(self.loc[num],text,font_size)
        self.adjunct[num]=l
        self.group.append(l.dabel)
    
    def add_rating_bar(self, num, text, font_size, max_rating=5, initial_rating=0):
        
        r=rating_bar(self.loc[num], text, font_size, max_rating, initial_rating)
        self.adjunct[num]=r
        self.group.append(r.button.dabel)
        self.group.append(r.label.dabel)
        
        self.movable_pos.append(num)
        self.movable_pos.sort()
        
        if self.cur_pos==None:
            self.cur_pos=num
            self.select(num)
            
    def rate_rating_bar(self,num,rating):
    
        r=self.adjunct[num]
        if r.is_selected==False or rating==r.cur_rating or rating<0 or rating>r.max_rating:
            return
        else:
            if r.cur_rating==0:
                self.group.append(r.left_cursor.dabel)
            elif r.cur_rating==5:
                self.group.append(r.right_cursor.dabel)
            else:
                if rating==0:
                    self.group.remove(r.left_cursor.dabel)
                elif rating==5:
                    self.group.remove(r.right_cursor.dabel)
                    
            r.cur_rating=rating
            r.label.dabel.text=str(rating)
    
    def add_img(self, num, url):
        
        bmp=displayio.OnDiskBitmap(url)
        tile_grid=displayio.TileGrid(bmp,pixel_shader=bmp.pixel_shader)
        bound=self.loc[num]
        tile_grid.x=bound[0]
        tile_grid.y=bound[1]
        self.group.append(tile_grid)
    
      
    def select(self,num):
        
        t=self.adjunct[num]
        if isinstance(t,button):
            if t.is_selected:
                return
            else:
                t.select()
        elif isinstance(t,rating_bar):
            if t.is_selected:
                return
            else:
                t.label.select()
                if t.cur_rating==0:
                    self.group.append(t.right_cursor.dabel)
                elif t.cur_rating==t.max_rating:
                    self.group.append(t.left_cursor.dabel)
                else:
                    self.group.append(t.right_cursor.dabel)
                    self.group.append(t.left_cursor.dabel)
                t.is_selected=True
                t.button.select()
                
    def deselect(self,num):
        
        t=self.adjunct[num]
        if isinstance(t,button):
            if not t.is_selected:
                return
            else:
                t.deselect()
        elif isinstance(t,rating_bar):
            if not t.is_selected:
                return
            else:
                t.label.deselect()
                if t.cur_rating==0:
                    self.group.remove(t.right_cursor.dabel)
                elif t.cur_rating==t.max_rating:
                    self.group.remove(t.left_cursor.dabel)
                else:
                    self.group.remove(t.right_cursor.dabel)
                    self.group.remove(t.left_cursor.dabel)
                t.is_selected=False
                t.button.deselect()

class lcd:
    def __init__(self,display):
        self.display=display
        self.adjunct={}
        self.cur_screen=None
        
    def add_screen(self,screen):
        if self.cur_screen==None:
            self.cur_screen=screen
        self.adjunct[screen.name]=screen
        
    def refresh(self):
        if self.cur_screen==None:
            return
        else:
            self.display.show(self.cur_screen.group)
            
    def navigate(self,dir):
        if dir!='y' and len(self.cur_screen.movable_pos)<2:
            return
        
        cur_num=self.cur_screen.cur_pos
        movable_pos=self.cur_screen.movable_pos
        cur_index=movable_pos.index(cur_num)
        
        
        
        if type(self.cur_screen.adjunct[cur_num]) is button:
            b=self.cur_screen.adjunct[cur_num]
            if dir=='y':
                if b.action!=None:
                    if b.action in globals().keys():
                        globals()[b.action]()
                if b.transit_target==None:
                    return
                else:
                    self.cur_screen=self.adjunct[b.transit_target]
                    self.refresh()
                    return
            elif dir=='w':
                new_index=(cur_index-2)%len(movable_pos)
            elif dir=='s':
                new_index=(cur_index+2)%len(movable_pos)
            elif dir=='a':
                new_index=(cur_index-1)%len(movable_pos)
            elif dir=='d':
                new_index=(cur_index+1)%len(movable_pos)
            else:
                return
            new_num=movable_pos[new_index]
            
        elif type(self.cur_screen.adjunct[cur_num]) is rating_bar:
            b=self.cur_screen.adjunct[cur_num]

            if dir=='w':
                new_index=(cur_index-1)%len(movable_pos)
            elif dir=='s':
                new_index=(cur_index+1)%len(movable_pos)
            elif dir=='a':
                self.cur_screen.rate_rating_bar(cur_num,b.cur_rating-1)
                return
            elif dir=='d':
                self.cur_screen.rate_rating_bar(cur_num,b.cur_rating+1)
                return
            else:
                return
            new_num=movable_pos[new_index]
            
        self.cur_screen.cur_pos=new_num
        self.cur_screen.deselect(cur_num)
        self.cur_screen.select(new_num)
        
def hello():
    print("hello")
    
                
lcd=lcd(display)

screen_1=screen('C','rating_screen')
screen_1.add_button(0,'  back  ',12)
screen_1.add_button(1,'schedule',12)
screen_1.add_rating_bar(2,'Fatigue',12)
screen_1.add_rating_bar(3,'Headache',12)
screen_1.add_button(4,'prev',12)
screen_1.add_label(5,'1/1',12)
screen_1.add_button(6,'next',12,transit_target='initial_screen',action='hello')
lcd.add_screen(screen_1)

screen_2=screen('A','initial_screen')
screen_2.add_button(0,'nothing',12)
screen_2.add_button(2,'next',12,'rating_screen')
screen_2.add_img(3,'/imgs/picture_compress.bmp')
lcd.add_screen(screen_2)

lcd.refresh()


while True:
    direction=input("enter a direction: ")
    lcd.navigate(direction)
    
    
    

    



