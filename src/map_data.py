#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import sys, os, re
# import colormaps as cmaps 

#====================================================================
def vec_par(LEVEL, data, catmxy, rivermap, nx, ny, cmap, norm, ax, figname, w=0.05, sup=2):
    """
    Optimized function to plot river segments for a given LEVEL using LineCollection.
    """
    width = (float(LEVEL)**sup) * w
    txt = f"{figname}_{LEVEL:02d}.txt"

    # Run external binary ONCE per LEVEL
    os.system(f"./bin/print_rivvec {figname}.txt 1 {LEVEL} > {txt}")

    with open(txt, "r") as f:
        lines = f.readlines()

    segments, colors = [], []

    for line in lines:
        parts = line.split()

        if len(parts) < 5:
            continue

        lon1, lat1, lon2, lat2 = float(parts[0]), float(parts[1]), float(parts[3]), float(parts[4])

        # High-resolution index
        ixx1 = int((lon1 - west) * 60.0)
        iyy1 = int((-lat1 + north0) * 60.0)


        if ixx1 < 0 or iyy1 < 0 or ixx1 >= catmxy.shape[2] or iyy1 >= catmxy.shape[1]:
            continue

        ix = catmxy[0, iyy1, ixx1] - 1
        iy = catmxy[1, iyy1, ixx1] - 1


        if ix < 0 or ix >= nx or iy < 0 or iy >= ny:
            continue

        if rivermap[iy,ix] == 0:
            continue

        if data[iy,ix] == -9999.0:
            continue

        # Longitude wrapping
        if lon1 - lon2 > 180.0:
            lon2 = 180.0
        elif lon2 - lon1 > 180.0:
            lon2 = -180.0

        segments.append([[lon1, lat1], [lon2, lat2]])
        colors.append(cmap(norm(data[iy, ix])))

    # Draw all segments at once
    if segments:
        lc = LineCollection(segments, colors=colors, linewidths=width, alpha=1.0,
                            zorder=110, transform=ccrs.PlateCarree())
        ax.add_collection(lc)

#====================================================================
def mk_dir(sdir):
    os.makedirs(sdir, exist_ok=True)

#====================================================================
# Inputs
dataname = sys.argv[1]
mapname  = sys.argv[2]
CaMa_dir = sys.argv[3]
rivnums  = sys.argv[4]
figname  = sys.argv[5]

# Map parameters
params_file = os.path.join(CaMa_dir, "map", mapname, "params.txt")
lines = open(params_file).readlines()
nx, ny = int(lines[0].split()[0]), int(lines[1].split()[0])
west, east = float(lines[4].split()[0]), float(lines[5].split()[0])
south, north = float(lines[6].split()[0]), float(lines[7].split()[0])

north0 = north  # for high-res mapping
north  = min(north,32.0)

print (west,east,south,north)

# Load map arrays
nextxy  = np.fromfile(os.path.join(CaMa_dir,"map",mapname,"nextxy.bin"), np.int32).reshape(2, ny, nx)
uparea  = np.fromfile(os.path.join(CaMa_dir,"map",mapname,"uparea.bin"), np.float32).reshape(ny, nx)
rivnum  = np.fromfile(rivnums,np.int32).reshape(ny,nx)
rivermap = ((rivnum == 1) & (nextxy[0] > 0) & (uparea > 0.0)).astype(float)

# High-resolution mapping
loc_file = os.path.join(CaMa_dir, "map", mapname, "1min", "location.txt")
lines = open(loc_file).readlines()
nXX = int(lines[2].split()[6])
nYY = int(lines[2].split()[7])
catmxy = np.fromfile(os.path.join(CaMa_dir, "map", mapname, "1min", "1min.catmxy.bin"), np.int16).reshape(2, nYY, nXX)

# Read mean discharge
data = np.fromfile(dataname, np.float32).reshape(-1, ny, nx)
data = (data < 1e19)*data*1.0
data = np.mean(data, axis=0)

# Colormap
cmap = plt.get_cmap("viridis_r")
# cmap = cmaps.speed
vmin, vmax = 0.0, np.max(data)
norm = Normalize(vmin=vmin, vmax=vmax)

# Figure setup
fig = plt.figure(figsize=(8.27/1.0, 11.69/3.0))  # A4 
ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
ax.set_extent([west, east, south, north], crs=ccrs.PlateCarree())

# Add shapefile
print ("plot shapefile")
shp = shpreader.Reader("GBM_basin/GBM_basin.shp")
ax.add_geometries(list(shp.geometries()), crs=ccrs.PlateCarree(),
                  facecolor='none', edgecolor='grey', linewidth=1.0)

# Run external txt_vector once
os.system(f"./bin/txt_vector {west} {east} {north} {south} {CaMa_dir} {mapname} > {figname}.txt")

# Plot rivers
print ("plot rivers")
for level in range(1,10+1):
    vec_par(LEVEL=level, data=data, catmxy=catmxy, rivermap=rivermap,
            nx=nx, ny=ny, cmap=cmap, norm=norm, ax=ax, figname=figname, w=0.05, sup=2)

# Title and clean axes
ax.set_title("Mena Discharge", fontsize=8)
for spine in ax.spines.values():
    spine.set_visible(False)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cax  = fig.add_axes([0.2, 0.05, 0.6, 0.02])  # adjust as needed
cbar = plt.colorbar(sm, cax=cax, orientation="horizontal", extend='both')
cbar.ax.tick_params(labelsize=6)
cbar.set_label("$Mean$ $Discharge$ $(m^3/s)$", fontsize=7)


# Save figure
mk_dir("./fig")
plt.tight_layout()
plt.savefig(os.path.join("./fig", f"{figname}.jpg"), dpi=300, bbox_inches="tight", pad_inches=0.0)
plt.close(fig)
os.system("rm -r "+figname+"*.txt")