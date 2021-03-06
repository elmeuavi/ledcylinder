# WS2812 LED Matrix Cylinder
# by M Oehler
# https://hackaday.io/project/162035-led-matrix-cylinder
# Released under a "Simplified BSD" license

import time, random, sys
import argparse
from font5x3 import font5x3
from itertools import chain
import numpy
#sudo apt-get install libatlas-base-dev
#

# False for simulation mode, True for using a Raspberry PI
PI=True

if PI:
    #from neopixel import *
    #I'm using this other libraries,... but you can change to generic neopixel.
    from rpi_ws281x import *
    #how to install this libraries to empty raspberry
    #      sudo apt-get update
    #      sudo pip3 install adafruit-circuitpython-neopixel
    #      sudo pip3 install rpi_ws281x
    #      sudo python3 -m pip install --force-reinstall adafruit-blinka
    #      sudo apt-get -y install build-essential python-dev git scons swig
    #      git clone http://github.com/jgarff/rpi_ws281x.git


else:
    import pygame
    from pygame.locals import *

SIZE=20;
OFFSET_BEGIN=60
BOARDWIDTH = 15
BOARDHEIGHTLETTER = 5
BLANK = '.'

mask = bytearray([1,2,4,8,16,32,64,128])

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (255,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 255,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 255)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (255, 255,   0)
LIGHTYELLOW = (175, 175,  20)
CYAN        = (  0, 255, 255)
MAGENTA     = (255,   0, 255)
ORANGE      = (255, 100,   0)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (BLUE,GREEN,RED,YELLOW,CYAN,MAGENTA,ORANGE)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)

# LED strip configuration:
LED_COUNT      = 210     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

if PI:
    # Create NeoPixel object 
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Init lib
    strip.begin()
else:
    strip=[]

# Zig-Zag resorting array for cylinder matrix: Example of 5x20 led's
#matrix =  [0, 9, 10, 19, 20, 29, 30, 39, 40, 49, 50, 59, 60, 69, 70, 79, 80, 89, 90, 99,
#	1, 8, 11, 18, 21, 28, 31, 38, 41, 48, 51, 58, 61, 68, 71, 78, 81, 88, 91, 98,
#	2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 82, 87, 92, 97,
#	3, 6, 13, 16, 23, 26, 33, 36, 43, 46, 53, 56, 63, 66, 73, 76, 83, 86, 93, 96,
#	4, 5, 14, 15, 24, 25, 34, 35, 44, 45, 54, 55, 64, 65, 74, 75, 84, 85, 94, 95]
    
matrixOrdenada =   [9,10,29,30,49,50,69,70,89,90,109,110,129,130,149,
            8,11,28,31,48,51,68,71,88,91,108,111,128,131,148,
            7,12,27,32,47,52,67,72,87,92,107,112,127,132,147,
            6,13,26,33,46,53,66,73,86,93,106,113,126,133,146,
            5,14,25,34,45,54,65,74,85,94,105,114,125,134,145,
            4,15,24,35,44,55,64,75,84,95,104,115,124,135,144,
            3,16,23,36,43,56,63,76,83,96,103,116,123,136,143,
            2,17,22,37,42,57,62,77,82,97,102,117,122,137,142,
            1,18,21,38,41,58,61,78,81,98,101,118,121,138,141,
            0,19,20,39,40,59,60,79,80,99,100,119,120,139,140]

#for 5x5 letter font, i moved the initial rows to the middel
matrixGirada = [7,12,27,32,47,52,67,72,87,92,107,112,127,132,147,
            6,13,26,33,46,53,66,73,86,93,106,113,126,133,146,
            5,14,25,34,45,54,65,74,85,94,105,114,125,134,145,
            4,15,24,35,44,55,64,75,84,95,104,115,124,135,144,
            3,16,23,36,43,56,63,76,83,96,103,116,123,136,143,
            2,17,22,37,42,57,62,77,82,97,102,117,122,137,142,
            1,18,21,38,41,58,61,78,81,98,101,118,121,138,141,
            0,19,20,39,40,59,60,79,80,99,100,119,120,139,140,
            9,10,29,30,49,50,69,70,89,90,109,110,129,130,149,
            8,11,28,31,48,51,68,71,88,91,108,111,128,131,148]

matrix = matrixOrdenada 


display_cursor = 0 ;

display = [[0 for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHTLETTER)]
print(display)

# Main program logic follows:
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, matrix
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    if not PI:
		# init pygame simualator
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((20*SIZE, 5*SIZE))
        BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
        BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
        pygame.display.set_caption('Pi Cylinder')
        DISPLAYSURF.fill(BGCOLOR)
        pygame.display.update()
    try:

        while True:
            if not PI:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
            print ('Color wipe animations.')
            
            #time.sleep(5)
            matrix = matrixGirada 
            scroll_text_display('F R E E D O M   C A T A L A N   P O L I T I C A L   P R I S I O N E R S .   F R E E D O M   P U I G D E M O N T .  ',random.randrange(0,0xFFFFFF,2),75)
            
            colorRandom(strip, 5000)
            clear_display()
            matrix = matrixOrdenada 
            colorWipe(strip, 0, 255, 0,25)  # GREEN wipe
            colorWipe(strip, 0, 0, 255,25)  # BLUE wipe
            colorWipe(strip, 255, 0, 0,25)  # RED wipe
            clear_display()

    except KeyboardInterrupt:
        if args.clear:
            matrix = matrixOrdenada 
            colorWipe(strip, 0,0,0, 10)

def colorWipe(strip, r,g,b, wait_ms=50):
    for i in range(LED_COUNT-OFFSET_BEGIN):
        draw_pixel(int(i%BOARDWIDTH),int(i/BOARDWIDTH),r,g,b)
        time.sleep(wait_ms/1000.0)

def colorRandom(strip, cycles):
    for i in range(0,cycles):
        a= random.randrange(0,LED_COUNT-OFFSET_BEGIN,1);
        c=random.randrange(0,0xFFFFFF,1);
        drawPixel(int(a%BOARDWIDTH),int(a/BOARDWIDTH),c)
        time.sleep(1/1000.0)

def drawPixel(x,y,color):
    if color == BLANK:
        return
    if PI:
        if (x>=0 and y>=0 and color >=0):
            strip.setPixelColor(y*BOARDWIDTH+x+OFFSET_BEGIN,color)
            strip.show()
    else:
        pygame.draw.rect(DISPLAYSURF, (color>>16,(color>>8)&0xFF,color&0xFF), (x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()

def clear_display():
    global display
    display = [[0 for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHTLETTER)]
    draw_display()

def draw_display():
    if PI:
        for x in range(0,BOARDWIDTH):
            for y in range(0,BOARDHEIGHTLETTER):
                if y<5:  # xevi
                    strip.setPixelColor(matrix[y*BOARDWIDTH+x]+OFFSET_BEGIN,
                                        Color(   int((display[y][x]>>8)&0xFF)   , int(display[y][x]>>16)   , int(display[y][x]&0xFF)  ))
                # ORIGINAL #strip.setPixelColor(matrix[y*20+x],
                # ORIGINAL #                        (Color(display[y][x]>>8)&0xFF, display[y][x]>>16, display[y][x]&0xFF))
        strip.show()
    else:
        for x in range (0,20):
            for y in range(0,5):
                pygame.draw.rect(DISPLAYSURF, (display[y][x]>>16,(display[y][x]>>8)&0xFF,display[y][x]&0xFF), (x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()

def print_char(char,cursor):
    for i in range(0,3):
        a=font5x3[ord(char)][i]
        for j in range(0,5):
            if a&mask[j]:
                draw_pixel(cursor+i,j,255,0,0)
            else:
                draw_pixel(cursor+i,j,0,0,0)

def scroll_text_display(string,color,wait_ms):
    global display
    cursor=0
    for c in range(0,len(string)):     #c = caràcter de la cadena de caràters
        for i in range(0,3):            #i = amplada del caràcter
            a=font5x3[ord(string[c])][i]
            for j in range(0,5):       # alçada
                if a&mask[j]:
                    display[j][BOARDWIDTH-1]=color;
                else:
                    display[j][BOARDWIDTH-1] =0;
            draw_display()
            display = numpy.roll(display,-1,axis=1)
            time.sleep(wait_ms / 1000.0)
        # add zero coulumn after every letter
        for j in range(0, 5):
            display[j][BOARDWIDTH-1] = 0;
        draw_display()
        display = numpy.roll(display,-1,axis=1)
        time.sleep(wait_ms / 1000.0)
    #shift text out of display (20 pixel)
    for i in range(0,BOARDWIDTH):
        for j in range(0, 5):
            display[j][BOARDWIDTH-1] = 0;
        draw_display()
        display = numpy.roll(display, -1, axis=1)
        time.sleep(wait_ms / 1000.0)


def draw_pixel(x,y,r,g,b):
    if PI:
        strip.setPixelColor(matrix[y*BOARDWIDTH+x]+OFFSET_BEGIN,Color(r, g, b))
        strip.show()
    else:
        pygame.draw.rect(DISPLAYSURF, (r,g,b), (x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()


if __name__ == '__main__':
    main()
