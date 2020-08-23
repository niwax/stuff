from skimage.io import imread, imsave
import numpy as np
import math

import PIL

PIL.Image.MAX_IMAGE_PIXELS = 933120000
scale = 1 / 21600 * 2 * math.pi

def GetPoint(lng, lat, offset):
    lng_rad = lng * scale
    lat_rad = lat * scale - math.pi / 2

    z = math.sin(lat_rad)
    r = abs(math.cos(lat_rad))
    x = math.cos(lng_rad) * r
    y = math.sin(lng_rad) * r

    return (x * (6371000 + offset), y * (6371000 + offset), z * (6371000 + offset))

def GetLength(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2 + (p0[2] - p1[2]) ** 2)

def GetTriangleSize(points):
    a = GetLength(points[0], points[1])
    b = GetLength(points[1], points[2])
    c = GetLength(points[2], points[0])

    s = (a + b + c) / 2

    return math.sqrt(s * (s - a) * (s - b) * (s - c))

def GetRectSize(points):
    return GetTriangleSize([points[0, 0], points[1, 1], points[0, 1]]) + \
           GetTriangleSize([points[0, 0], points[1, 1], points[1, 0]])

def GetPatchSize(lng, lat, offset = np.zeros((4,4))):
    sum = 0

    points = np.empty(offset.shape, "object")

    for x in range(offset.shape[0]):
        for y in range(offset.shape[1]):
            points[x, y] = GetPoint(x + lng, y + lat, offset[x, y])

    for x in range(offset.shape[0] - 1):
        for y in range(offset.shape[1] - 1):
            sum += GetRectSize(points[x:x+2, y:y+2])

    return sum

def ColorScale(perc):
    if perc <= 0:
        return [0, 0, 0]

    if perc <= 0.06:
        return [math.sqrt(perc / 0.06) * 255, 0, 0]

    if perc <= 0.12:
        return [255, math.sqrt((perc - 0.06) / 0.06) * 255, 0]

    if perc <= 0.18:
        return [math.sqrt((0.18 - perc) / 0.06) * 255, 255, 0]

    return [0, 255, 0]

img = np.transpose(imread("gebco_08_rev_elev_21600x10800.png"))

out = np.zeros((img.shape[0], img.shape[1], 3))
sizes = np.zeros((img.shape[0], img.shape[1]))

for lng in range(2, img.shape[0] - 2):
    for lat in range(2, img.shape[1] - 2):
        patch = img[lng-2:lng+2, lat-2:lat+2]

        if 0 in patch or 255 in patch:
            out[lng, lat] = [5, 30, 192]
        else:
            flat = GetPatchSize(lng - 2, lat - 2)
            topology = GetPatchSize(lng - 2, lat - 2, patch / 255 * 6400)
            sizes[lng, lat] = (topology / flat - 1)
            out[lng, lat] = ColorScale(topology / flat - 1)

imsave("out.png", np.transpose(out.astype("uint8"), (1, 0, 2)))
