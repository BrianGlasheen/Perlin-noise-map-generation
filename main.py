import noise
from PIL import Image, ImageTk
import tkinter as tk 
import numpy as np
from random import randint
import math

root = tk.Tk()
root.wm_geometry("900x700")

canvas = tk.Canvas(root, width=700, height=700)
canvas.grid(row=0, column=0, rowspan=20)

wtr_e = tk.Entry(root)
wtr_e.grid(row=0, column=2)
wtr_e.insert(tk.END, '.05')
wtr_l = tk.Label(root, text="Water ")
wtr_l.grid(row=0, column=1)

snd_e = tk.Entry(root)
snd_e.grid(row=1, column=2)
snd_e.insert(tk.END, '0.10')
snd_l = tk.Label(root, text="Sand ")
snd_l.grid(row=1, column=1)

lnd_e = tk.Entry(root)
lnd_e.grid(row=2, column=2)
lnd_e.insert(tk.END, '0.40')
lnd_l = tk.Label(root, text="Land ")
lnd_l.grid(row=2, column=1)

mtn_e = tk.Entry(root)
mtn_e.grid(row=3, column=2)
mtn_e.insert(tk.END, '0.75')
mtn_l = tk.Label(root, text="Mountain ")
mtn_l.grid(row=3, column=1)

planet_radius = tk.Scale(root, from_=1, to=500, orient=tk.HORIZONTAL)
planet_radius.set(500)
planet_radius.grid(row=4, column=2)
plt_l = tk.Label(root, text="Radius ")
plt_l.grid(row=4, column=1)

gradient = tk.Scale(root, from_=1, to=50, orient=tk.HORIZONTAL)
gradient.set(50)
gradient.grid(row=5, column=2)
grd_l = tk.Label(root, text="Gradient ")
grd_l.grid(row=5, column=1)

arch_bool = tk.IntVar()
arch_mode = tk.Checkbutton(root, text='Archipelago mode', variable=arch_bool)
arch_mode.grid(row=6, column=1, columnspan=2, sticky=tk.NSEW)

update_button = tk.Button(root, text="Update map", command=lambda: button_press('update', canvas, noise_map))
update_button.grid(row=9, column=1, columnspan=2, sticky=tk.NSEW)

new_map_button = tk.Button(root, text="New map", command=lambda: button_press('new', canvas))
new_map_button.grid(row=10, column=1, columnspan=2, sticky=tk.NSEW)

save_button = tk.Button(root, text="Save", command=lambda: button_press('save'))
save_button.grid(row=11, column=1, columnspan=2, sticky=tk.NSEW)

log = tk.Text(root, height=4, width=23, font=("Arial", 10))
log.grid(row=16, column=1, rowspan=4, columnspan=3)

def button_press(s, canvas=0, noise_map=0):
    if s == 'new':
        new_map(canvas)
    elif s == 'update':
        update_map(canvas, noise_map)
    elif s == 'save':
        save_img()

def gen_noise(shape, scale, octaves, persistence, lacunarity):

    log.insert(tk.END, "generating noise\n")
    map_ = np.zeros(shape)

    z = randint(0,100000)
    for i in range(shape[0]):
        for j in range(shape[1]):
            map_[i][j] = noise.pnoise3(i/scale, j/scale, z,
                                    octaves=octaves, persistence=persistence, lacunarity=lacunarity, 
                                    repeatx=shape[0], repeaty=shape[1], base=0)

    if arch_bool.get():
        factor = int(gradient.get())

        center_x, center_y = shape[1] // 2, shape[0] // 2
        circle_grad = np.zeros_like(map_)

        for y in range(shape[0]):
            for x in range(shape[1]):
                distx = abs(x - center_x)
                disty = abs(y - center_y)
                dist = math.sqrt(distx*distx + disty*disty)
                circle_grad[y][x] = dist

        max_grad = np.max(circle_grad)
        circle_grad = circle_grad / max_grad
        circle_grad -= 0.5
        circle_grad *= 2.0
        circle_grad = -circle_grad

        for y in range(shape[0]):
            for x in range(shape[1]):
                if circle_grad[y][x] > 0:
                    circle_grad[y][x] *= factor

        max_grad = np.max(circle_grad)
        circle_grad = circle_grad / max_grad

        world_noise = np.zeros_like(map_)

        for i in range(shape[0]):
            for j in range(shape[1]):
                world_noise[i][j] = (map_[i][j] * circle_grad[i][j])
                if world_noise[i][j] > 0:
                    world_noise[i][j] *= factor

        max_grad = np.max(world_noise)
        map_ = world_noise / max_grad

    log.insert(tk.END, "noise generation complete\n")
    return map_

def color_map(map_):
    log.insert(tk.END, "coloring noise\n")
    colors = {
        'water': (0,0,255),
        'sand': (255,255,0),
        'land': (0,255,0),
        'mountain': (50,50,50),
        'snow': (255,255,255)}

    colored_map = np.zeros(map_.shape+(3,))  
    colored_map = np.zeros_like(colored_map)   
    threshold = 0

    wtr = float(wtr_e.get())
    snd = float(snd_e.get())
    lnd = float(lnd_e.get())
    mtn = float(mtn_e.get())

    a, b = 350, 350
    n = 700
    r = int(planet_radius.get())
    y ,x = np.ogrid[-350:350, -350:350]
    mask = x**2+y**2 <= r**2

    for i in range(700):
        for j in range(700):
            if mask[i][j]:
                if map_[i][j] < threshold + wtr:
                    colored_map[i][j] = colors['water']
                elif map_[i][j] < threshold + snd:
                    colored_map[i][j] = colors['sand']
                elif map_[i][j] < threshold + lnd:
                    colored_map[i][j] = colors['land']
                elif map_[i][j] < threshold + mtn:
                    colored_map[i][j] = colors['mountain']
                else:
                    colored_map[i][j] = colors['snow']
            else:
                colored_map[i][j] = 0,0,0

    log.insert(tk.END, "noise coloration complete\n")
    return colored_map

def new_map(canvas):
    shape = (700,700) #y, x
    scale = 100.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0

    global noise_map

    noise_map = gen_noise(shape, scale, octaves, persistence, lacunarity)
    current_map = color_map(noise_map)

    plot_map(canvas, current_map)

def update_map(canvas, noise_map):
    current_map = color_map(noise_map)
    plot_map(canvas, current_map)

def plot_map(canvas, map_):

    global image 
    global tk_img
    
    image = Image.fromarray(map_.astype('uint8'), 'RGB')

    tk_img = ImageTk.PhotoImage(image)
    canvas.delete('all')
    imagesprite = canvas.create_image(350,350,image=tk_img)

def save_img():
    try:
        image.save("map.png")
    except NameError:
        log.insert(tk.END, "No image\n")
root.mainloop()