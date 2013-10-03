import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import vislab


def plot__frequencies(df, column, top_k=20):
    """
    Plot bar chart of frequencies of top_k values of a column in the df.
    """
    column_vals = vislab.dataset_stats.top_k_vals(df, column, top_k)
    fig = plt.figure(figsize=(12, 4))
    ax = column_vals.plot(fig, kind='bar', title='{} Frequency'.format(
        column))
    ax.set_xlabel('')
    fig.autofmt_xdate()
    return fig


def plot_conditional_occurence(
        df_m, size=None, cmap=plt.cm.gray_r, color_anchor=[0, 1],
        x_tick_rot=90, title=None, plot_vals=True):
    """
    Plot the occurrence of the columns of the given DataFrame
    conditioned on the occurrence of its rows.
    Each row therefore sums to 1, excepting the last column, which
    is the prior probability of the row value.

    Parameters
    ----------
    df_m: pandas.DataFrame
        Cells contain joint occurrences between index and column.
    size: tuple [None]
        Optional argument to figsize.
    cmap: matplotlib.cmap [gray]
    color_anchor: ?
    x_tick_rot: float
    title: string
    plot_vals: bool [True]
        If true, actual values are plotted.
    """
    df_m = vislab.dataset_stats.condition_df_on_row(df_m)
    df_m = df_m.sort('prior', ascending=False)
    M, N = df_m.shape

    # Initialize figure of given size.
    if size is None:
        w = max(12, N)
        h = max(12, M)
        size = (w, h)
    fig = plt.figure(figsize=size)
    ax_im = fig.add_subplot(111)

    # Make axes for colorbar.
    divider = make_axes_locatable(ax_im)
    ax_cb = divider.new_vertical(size="5%", pad=0.1, pack_start=True)
    fig.add_axes(ax_cb)

    # The call to imshow produces the matrix plot.
    im = ax_im.imshow(df_m, origin='upper', interpolation='nearest',
                      vmin=color_anchor[0], vmax=color_anchor[1], cmap=cmap)

    # Formatting.
    ax = ax_im
    ax.set_xticks(np.arange(N))
    ax.set_xticklabels(df_m.columns)
    for tick in ax.xaxis.iter_ticks():
        tick[0].label2On = True
        tick[0].label1On = False
        tick[0].label2.set_rotation(x_tick_rot)
        tick[0].label2.set_fontsize('x-large')

    ax.set_yticks(np.arange(M))
    ax.set_yticklabels(df_m.index, size='x-large')

    ax.yaxis.set_minor_locator(
        mpl.ticker.FixedLocator(np.arange(-.5, M + 0.5)))
    ax.xaxis.set_minor_locator(
        mpl.ticker.FixedLocator(np.arange(-.5, N - 0.5)))
    ax.grid(False, which='major')
    ax.grid(True, which='minor', ls='-', lw=7, c='w')

    # Make the major and minor tick marks invisible
    for line in ax.xaxis.get_ticklines() + ax.yaxis.get_ticklines():
            line.set_markeredgewidth(0)
    for line in ax.xaxis.get_minorticklines() + ax.yaxis.get_minorticklines():
            line.set_markeredgewidth(0)

    # Limit the area of the plot
    ax.set_ybound([-0.5, M - 0.5])
    ax.set_xbound([-0.5, N - 0.5])

    # The following produces the colorbar and sets the ticks
    # Set the ticks - if 0 is in the interval of values, set that, as well
    # as the maximal and minimal values:
    # Extract the minimum and maximum values for scaling
    max_val = np.nanmax(df_m)
    min_val = np.nanmin(df_m)
    if min_val < 0:
        ticks = [color_anchor[0], min_val, 0, max_val, color_anchor[1]]
    # Otherwise - only set the maximal value:
    else:
        ticks = [color_anchor[0], max_val, color_anchor[1]]

    # Plot line separating 'nothing' and 'prior' from rest of plot
    l = ax.add_line(mpl.lines.Line2D(
        [N - 1.5, N - 1.5], [-.5, M - 0.5],
        ls='--', c='gray', lw=2))
    l.set_zorder(3)

    # Display the actual values in the cells
    if plot_vals:
        for i in xrange(0, M):
            for j in xrange(0, N):
                val = df_m.iloc[i, j]
                if np.isnan(val):
                    continue
                if val > 0.5:
                    ax.text(j - 0.2, i + 0.1, '%.2f' % val, color='w')
                else:
                    ax.text(j - 0.2, i + 0.1, '%.2f' % val, color='k')

    # Hide the black frame around the plot
    # Doing ax.set_frame_on(False) results in weird thin lines
    # from imshow() at the edges. Instead, we set the frame to white.
    for spine in ax.spines.values():
        spine.set_edgecolor('w')

    # Set title
    if title is not None:
        ax.set_title(title)

    # Plot the colorbar and remove its frame as well.
    cb = fig.colorbar(im, cax=ax_cb, orientation='horizontal',
                      cmap=cmap, ticks=ticks, format='%.2f')
    cb.ax.artists.remove(cb.outline)
