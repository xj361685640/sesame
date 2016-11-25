import numpy as np

try:
    import matplotlib.pyplot as plt
    mpl_enabled = True
    try:
        from mpl_toolkits import mplot3d
        has3d = True
    except ImportError:
        warnings.warn("3D plotting not available.", RuntimeWarning)
        has3d = False
except ImportError:
    warnings.warn("matplotlib is not available", RuntimeWarning)
    mpl_enabled = False

def plot_extra_charges(sys, ls='-o'):
    """
    Plot the sites containing additional charges. The length scale of the the
    graph is 1 micrometer.

    Parameters
    ----------
    sys: Builder
        The discretized system.
    ls: string
        Line style of the plotted paths.
    """
    if not mpl_enabled:
        raise RuntimeError("matplotlib was not found, but is required "
                           "for plot()")

    for c in sys.charges:
        if c.ya <= c.yb:
            xa, ya, za = get_indices(sys, (c.xa, c.ya, c.za))
            xb, yb, zb = get_indices(sys, (c.xb, c.yb, c.zb))
        else:
            xa, ya, za = get_indices(sys, (c.xb, c.yb, c.zb))
            xb, yb, zb = get_indices(sys, (c.xa, c.ya, c.za))

        # find the sites closest to the straight line defined by
        # (xa,ya,za) and (xb,yb,zb) and the associated dl       
        distance = lambda x, y:\
            abs((c.yb-c.ya)*x - (c.xb-c.xa)*y + c.xb*c.ya - c.yb*c.xa)/\
                np.sqrt((c.yb-c.ya)**2 + (c.xb-c.xa)**2)

        def condition(x, y):
            if xa <= xb:
                return x <= xb and y <= yb and x < sys.nx-1 and y < sys.ny-1
            else:
                return x >= xb and y <= yb and x > 1 and y < sys.ny-1

        x, y = xa, ya
        xcoord, ycoord = [xa], [ya]
        while condition(x, y):
            # distance between the point above (x,y) and the segment
            d1 = distance(sys.xpts[x], sys.ypts[y+1])
            # distance between the point right of (x,y) and the segment
            d2 = distance(sys.xpts[x+1], sys.ypts[y])
            # distance between the point left of (x,y) and the segment
            d3 = distance(sys.xpts[x-1], sys.ypts[y])

            if xa < xb: # overall direction is to the right
                if d1 < d2:
                    x, y = x, y+1
                else:
                    x, y = x+1, y
            else: # overall direction is to the left
                if d1 < d3:
                    x, y = x, y+1
                else:
                    x, y = x-1, y
            xcoord.append(x)
            ycoord.append(y)

        # plot the path of added charges
        sc = sys.xscale*1e6
        plt.plot(sys.xpts[xcoord]*sc, sys.ypts[ycoord]*sc, ls)
        plt.xlabel('x (µm)')
        plt.ylabel('y (µm)')

    plt.xlim(xmin=0, xmax=sys.xpts[-1]*sc)
    plt.ylim(ymin=0, ymax=sys.ypts[-1]*sc)
    plt.show()

def map2D(sys, data, cmap='gnuplot', alpha=1):
    """
    Plot a 2D map of data across the system.

    Parameters
    ----------

    sys: Builder
        The discretized system.
    data: numpy array
        One-dimensional array of data with size equal to the size of the system.
    cmap: string
        Name of the colormap used by Matplolib.
    alpha: float
        Transparency of the colormap.
    """

    if not mpl_enabled:
        raise RuntimeError("matplotlib was not found, but is required "
                           "for map2D()")

    xpts, ypts = sys.xpts * sys.xscale * 1e6, sys.ypts * sys.xscale * 1e6
    nx, ny = len(xpts), len(ypts)
    data = data.reshape(ny, nx).T
    xmax = sys.xpts[-1] * sys.xscale * 1e6
    ymax = sys.ypts[-1] * sys.xscale * 1e6
    plt.imshow(data, extent=[0, xmax, 0, ymax])
    plt.xlabel('x (µm)')
    plt.ylabel('y (µm)')
    plt.show()

def map3D(sys, data, cmap='gnuplot', alpha=1):
    """
    Plot a 3D map of data across the system.

    Parameters
    ----------

    sys: Builder
        The discretized system.
    data: numpy array
        One-dimensional array of data with size equal to the size of the system.
    cmap: string
        Name of the colormap used by Matplolib.
    alpha: float
        Transparency of the colormap.
    """

    if not mpl_enabled:
        raise RuntimeError("matplotlib was not found, but is required "
                           "for map3D()")
    if not has3d:
        raise RuntimeError("Installed matplotlib does not support 3d plotting")

    xpts, ypts = sys.xpts * sys.xscale * 1e6, sys.ypts * sys.xscale * 1e6
    nx, ny = len(xpts), len(ypts)
    data_xy = data.reshape(ny, nx).T
    X, Y = np.meshgrid(xpts, ypts)
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(1,1,1, projection='3d')
    Z = data_xy.T
    ax.plot_surface(X, Y, Z,  alpha=alpha, cmap=cmap)
    ax.mouse_init(rotate_btn=1, zoom_btn=3)
    plt.xlabel('x (µm)')
    plt.ylabel('y (µm)')
    plt.show()

