import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def load_results(path):
    path = Path(path)
    with open(path,"r") as f:
        result = json.load(f)
    return result

def get_gradient_list(col1, col2, n):
    col1 = mcolors.to_rgba(col1)
    col2 = mcolors.to_rgba(col2)
    red_step = (col2[0] - col1[0]) / (n-1)
    green_step = (col2[1] - col1[1]) / (n-1)
    blue_step = (col2[2] - col1[2]) / (n-1)
    colors = []
    for i in range(n):
        red = col1[0] + red_step*i
        green = col1[1] + green_step*i
        blue = col1[2] + blue_step*i
        colors.append((red,green,blue))
    return colors

def get_2_gradients_list(col1, col2, col3, n):
    colors = get_gradient_list(col1, col2, n = int(n/2)+1)[:-1] + get_gradient_list(col2, col3, n=int(n/2) + n%2)
    return colors

def Histogram(dict):
    plt.hist
    pass


def Piechart(dict:dict):
    plt.pie(list(dict.values()),labels=list(dict.keys()))
    
    pass