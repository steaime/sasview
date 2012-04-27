"""
    This module allows more interaction with the plot
"""
import plottables
from BaseInteractor import _BaseInteractor


class PointInteractor(_BaseInteractor):
    """
    """
    def __init__(self, base, axes, color='black', zorder=3, id=''):
        """
        """
        _BaseInteractor.__init__(self, base, axes, color=color)
        self.zorder = zorder
        self.id = id
        self.color = color
        self.colorlist = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self.symbollist = ['o', 'x', '^', 'v', '<', '>',
                           '+', 's', 'd', 'D', 'h', 'H', 'p', '-']
        self.markersize = None
        self.marker = None
        self.marker2 = None
        self._button_down = False
        self._context_menu = False
        self._dragged = False
        self.connect_markers([self.axes])
        
    def _color(self, c):
        """Return a particular colour"""
        return self.colorlist[c % len(self.colorlist)]
    
    def _symbol(self, s):
        """Return a particular symbol"""
        return self.symbollist[s % len(self.symbollist)]

    def points(self, x, y, dx=None, dy=None, color=0, symbol=0, markersize=5,
               label=None, hide_error=False):
        """
        """
        #Draw curve
        if self._symbol(symbol) == '-':
            return self.curve(x=x, y=y, color=color, label=label)
            #return
        if not self.marker == None:
            self.base.connect.clear([self.marker])
        self.color = self._color(color)
        if self.markersize != None:
            markersize = self.markersize
        # Convert tuple (lo,hi) to array [(x-lo),(hi-x)]
        if dx != None and type(dx) == type(()):
            dx = nx.vstack((x-dx[0], dx[1]-x)).transpose()
        if dy != None and type(dy) == type(()):
            dy = nx.vstack((y-dy[0], dy[1]-y)).transpose()
        
        if dx == None and dy == None:
            zorder = 1
            self.marker = self.axes.plot(x, y, color=self.color,
                                         marker=self._symbol(symbol),
                                         markersize=markersize,
                                         linestyle='', label=label,
                                         zorder=zorder)[0]
        else:
            
            if hide_error:
                zorder = 1
                self.marker = self.axes.plot(x, y, color=self.color,
                                             marker=self._symbol(symbol),
                                             markersize=markersize,
                                             linestyle='', label=label,
                                             zorder=zorder)[0]
            else:
                zorder = 2
                self.marker = self.axes.errorbar(x, y, yerr=dy,
                                                 xerr=None,
                                                 ecolor=self.color,
                                                 color=self.color,
                                                 capsize=2,
                                                 linestyle='',
                                                 barsabove=False,
                                                 marker=self._symbol(symbol),
                                                 markersize=markersize,
                                                 lolims=False, uplims=False,
                                                 xlolims=False, xuplims=False,
                                                 label=label,
                                                 zorder=zorder)[0]
            
        self.connect_markers([self.marker])
        self.update()
        
    def curve(self, x, y, dy=None, color=0, symbol=0, label=None):
        """
        """
        if not self.marker == None:
            self.base.connect.clear([self.marker])
        self.color = self._color(color)
        self.marker = self.axes.plot(x, y, color=self.color, lw=1.5,
                                     marker='', linestyle='-', label=label)[0]
            
        self.connect_markers([self.marker])
        self.update()
        
    def connect_markers(self, markers):
        """
        Connect markers to callbacks
        """
        for h in markers:
            connect = self.base.connect
            connect('enter', h, self._on_enter)
            connect('leave', h, self._on_leave)
            connect('click', h, self._on_click)
            connect('release', h, self._on_release)
            connect('key', h, self.onKey)

    def clear(self):
        print "plottable_interactor.clear()"
        
    def _on_click(self, evt):
        """
        Called when a mouse button is clicked
        from within the boundaries of an artist.
        """
        if self._context_menu == True:
            self._context_menu = False
            evt.artist = self.marker
            self._on_leave(evt)

    def _on_release(self, evt):
        """
        Called when a mouse button is released
        within the boundaries of an artist
        """
        # Check to see whether we are about to pop
        # the context menu up
        if evt.button == 3:
            self._context_menu = True
        
    def _on_enter(self, evt):
        """
        Called when we are entering the boundaries
        of an artist.
        """
        if not evt.artist.__class__.__name__ == "AxesSubplot":
            self.base.plottable_selected(self.id)
            
            if evt.artist.get_color() == 'y':
                try:
                    evt.artist.set_color('b')
                except:
                    evt.artist.set_color_cycle('b')
                if hasattr(evt.artist, "set_facecolor"):
                    evt.artist.set_facecolor('b')
                if hasattr(evt.artist, "set_edgecolor"):
                    evt.artist.set_edgecolor('b')
            else:
                try:
                    evt.artist.set_color('y')
                except:
                    evt.artist.set_color_cycle('y')
                if hasattr(evt.artist, "set_facecolor"):
                    evt.artist.set_facecolor('y')
                if hasattr(evt.artist, "set_edgecolor"):
                    evt.artist.set_edgecolor('y')

            self.axes.figure.canvas.draw_idle()
        
    def _on_leave(self, evt):
        """
        Called when we are leaving the boundaries
        of an artist.
        """
        if not evt.artist.__class__.__name__ == "AxesSubplot":
            if self._context_menu == False:
                self.base.plottable_selected(None)
                try:
                    evt.artist.set_color(self.color)
                except:
                    evt.artist.set_color_cycle(self.color)
                if hasattr(evt.artist, "set_facecolor"):
                    evt.artist.set_facecolor(self.color)
                if hasattr(evt.artist, "set_edgecolor"):
                    evt.artist.set_edgecolor(self.color)
                self.axes.figure.canvas.draw_idle()
    
    def update(self):
        """
        Update
        """
        pass
