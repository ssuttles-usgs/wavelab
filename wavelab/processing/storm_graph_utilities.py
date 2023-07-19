'''
Created on Feb 11, 2016

@author: chogg
'''
import numpy as np
import matplotlib.image as image
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox
from wavelab.utilities.get_image import get_image


def plot_wind_data(ax, so, time_nums):

    so.wind_speed = np.array(so.wind_speed)
    wind_speed_max = np.nanmax(so.wind_speed)
    
    logo = image.imread(get_image('north.png'), None)
    bbox2 = Bbox.from_bounds(210, 330, 30, 40)
#     trans_bbox2 = bbox2.transformed(ax.transData)
    bbox_image2 = BboxImage(bbox2)
    bbox_image2.set_data(logo)
    ax.add_image(bbox_image2)
    
#     for x in range(0,len(time_nums),100):
    U = so.u
    V = so.v

    Q = ax.quiver(time_nums, -.15,
                  U,
                  V,
                  headlength=0,
                  headwidth=0,
                  headaxislength=0,
                  alpha=1,
                  color='#045a8d',
                  width=.0015,
                  scale=wind_speed_max*5)

    ax.quiverkey(Q,
                 0.44,
                 0.84,
                 wind_speed_max * .6,
                 labelpos='N',
                 label = ' ' * 34 + '0 mph' + ' ' * 27 + '%.2f mph' % wind_speed_max
                 )
#                    fontproperties={'weight': 'bold'}
#             else:
#                 ax.quiver(time_nums[x], -.15, 0,1, headlength=0, 
#                           headwidth=0, headaxislength=0, alpha=.3, color='#045a8d', width=.0030)


def get_second_coordinate(y1, yorigin, angle):
    
    newy = (y1 - yorigin) * np.sin(angle * np.pi / 180)
    return newy
