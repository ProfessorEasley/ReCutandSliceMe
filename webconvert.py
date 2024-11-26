# Usage:
# 1. Run the Cut and Slice me script in photoshop with the "Export Cut Infos" option enabled
# 2. Run this script as "python webconvert.py <assetdir>", where <assetdir> is the directory where the cut assets were placed
# 3. This script will generate an HTML file "webpage.html" inside the asset directory, which will automatically be opened in your web browser

import argparse
import os.path
import webbrowser
import glob
import json
import re
from PIL import Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('assets_folder')
    args = parser.parse_args()

    info_path = os.path.join(args.assets_folder, 'exported_assets_info.txt')
    if not os.path.exists(info_path):
        print('Error: Did not find exported_assets_info.txt in the specified directory')
        exit(1)

    min_x = float('inf')
    min_y = float('inf')
    max_x = -float('inf')
    max_y = -float('inf')
    assets = []
    with open(info_path, 'r') as f:
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break
            line = line.strip()
            if len(line) == 0:
                continue
            elem = json.loads(line)
            asset_name = elem['name']
            name = asset_name.strip().replace(' ', '-')
            pos_x = elem['x']
            pos_y = elem['y']
            bounds_w = elem['width']
            bounds_h = elem['height']
            min_x = min(min_x, pos_x - bounds_w/2.0)
            max_x = max(max_x, pos_x + bounds_w/2.0)
            min_y = min(min_y, pos_y - bounds_h/2.0)
            max_y = max(max_y, pos_y + bounds_h/2.0)
            lyr_idx = elem['index']
            if name.endswith('_BTN'):
                path_normal = glob.glob(os.path.join(args.assets_folder, name + '.normal*.png'))[0]
                path_pressed = glob.glob(os.path.join(args.assets_folder, name + '.pressed*.png'))[0]
            else:
                path_normal = glob.glob(os.path.join(args.assets_folder, name + '*.png'))[0]
                path_pressed = None
            fname_normal = os.path.basename(path_normal)
            fname_pressed = os.path.basename(path_pressed) if path_pressed is not None else None
            path_normal = os.path.join(args.assets_folder, fname_normal)
            img_normal = Image.open(path_normal)
            img_width = img_normal.width
            img_height = img_normal.height
            assets.append((name, fname_normal, fname_pressed, pos_x, pos_y, img_width, img_height, lyr_idx))

    wp_width = max_x - min_x
    wp_height = max_y - min_y

    html_src = f'''
    <!doctype html>
    <html>
    <head>
    <style type="text/css">'''

    def norm_name(name):
        return re.sub(r'[^a-zA-Z0-9]', '_', name.replace(' ', '_').replace('@', ''))

    for (name, fname_normal, fname_pressed, pos_x, pos_y, w, h, lyr_idx) in assets:
        html_src += f"#{norm_name(name)} {{ background: url('{fname_normal}'); background-size: {w}px {h}px; z-index: {lyr_idx}; }}"
        if fname_pressed is not None:
            html_src += f"#{norm_name(name)}:hover {{ background: url('{fname_pressed}'); background-size: {w}px {h}px; }}\n"

    html_src += f'''
    </style>
    </head>
    <body>
    <div style="width: {wp_width}px; height: {wp_height}px;">
    '''

    for (name, fname_normal, fname_pressed, pos_x, pos_y, w, h, lyr_idx) in assets:
        x = pos_x - min_x
        y = pos_y - min_y
        style = 'position: absolute;\n'
        style += f'width: {w}px;\n'
        style += f'height: {h}px;\n'
        style += f'left: {x - w/2.0}px;\n'
        style += f'top: {y - h/2.0}px;\n'
        html_src += f'<div id="{norm_name(name)}" style="{style}"></div>\n'

    html_src += f'''
    </div>
    </body>
    </html>
    '''

    wp_path = os.path.join(args.assets_folder, 'webpage.html')
    with open(wp_path, 'w') as f:
        f.write(html_src)

    print(f'Wrote {wp_path}')
    webbrowser.open(wp_path)
