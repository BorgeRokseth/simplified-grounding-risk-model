if __name__ == '__main__':

    import seacharts

    size = 19000, 19000
    center = 182602, 7098749
    files = ['Trondelag.gdb']
    enc = seacharts.ENC(files=files, border=True, center=center,size=size)

    # (id, easting, northing, heading, color)
    ships = [
        (1, 182602, 7098849, 132, 'orange'),
        (2, 182602, 7098749, 57, 'yellow'),
        (3, 182702, 7098349, 178, 'red'),
        (4, 182402, 7098149, 86, 'green'),
        (5, 182902, 7099349, 68, 'pink'),
    ]

    enc.add_vessels(*ships)

    import shapely.geometry as geo

    x, y = center
    width, height = 1900, 1900
    box = geo.Polygon((
        (x - width, y - height),
        (x + width, y - height),
        (x + width, y + height),
        (x - width, y + height),
    ))
    areas = list(box.difference(enc.seabed[10].geometry))
    enc.draw_circle(center, 1000, 'yellow', thickness=2,
                    edge_style='--')
    enc.draw_rectangle(center, (600, 1200), 'blue', rotation=20)
    enc.draw_circle(center, 700, 'green', edge_style=(0, (5, 8)),
                    thickness=3, fill=False)
    enc.draw_line([(center[0], center[1] + 800), center,
                   (center[0] - 300, center[1] - 400)], 'white')
    enc.draw_line([(center[0] - 300, center[1] + 400), center,
                   (center[0] + 200, center[1] - 600)],
                  'magenta', width=0.0, thickness=5.0,
                  edge_style=(0, (1, 4)))
    enc.draw_arrow(center, (center[0] + 700, center[1] + 600), 'orange',
                   head_size=300, width=50, thickness=5)
    enc.draw_polygon(enc.seabed[100].geometry[-3], 'cyan')
    enc.draw_polygon(enc.shore.geometry[56], 'highlight')
    for area in areas[3:8] + [areas[14], areas[17]] + areas[18:21]:
        enc.draw_polygon(area, 'red')
    enc.draw_rectangle(center, (width, height), 'pink', fill=False,
                       edge_style=(0, (10, 10)), thickness=1.5)

    enc.save_image('example1', extension='svg')

    enc.show_display()