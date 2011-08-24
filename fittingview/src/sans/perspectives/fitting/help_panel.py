#!/usr/bin/python

import wx
import wx.html as html
from wx.lib.splitter import MultiSplitterWindow
import os


class HelpWindow(wx.Frame):
    """
    """
    def __init__(self, parent, id, title= 'HelpWindow', pageToOpen=None):
        wx.Frame.__init__(self, parent, id, title, size=(850, 530))
        """
        contains help info
        """
      
        splitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        rpanel = wx.Panel(splitter, -1)
        lpanel = wx.Panel(splitter, -1,style=wx.BORDER_SUNKEN)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        header = wx.Panel(rpanel, -1)
        header.SetBackgroundColour('#6666FF')
        header.SetForegroundColour('WHITE')
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(header, -1, 'Contents', (5, 5))
        font = st.GetFont()
        font.SetPointSize(10)
        st.SetFont(font)
        hbox.Add(st, 1, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
        header.SetSizer(hbox)
        vbox.Add(header, 0, wx.EXPAND)
       
        vboxl= wx.BoxSizer(wx.VERTICAL)
        headerl = wx.Panel(lpanel, -1, size=(-1, 20))
       
        headerl.SetBackgroundColour('#6666FF')
        headerl.SetForegroundColour('WHITE')
        hboxl = wx.BoxSizer(wx.HORIZONTAL)
        lst = wx.StaticText(headerl, -1, 'Menu', (5, 5))
        fontl = lst.GetFont()
        fontl.SetPointSize(10)
        lst.SetFont(fontl)
        hboxl.Add(lst, 1, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
        headerl.SetSizer(hboxl)
        vboxl.Add(headerl, 0, wx.EXPAND)
        self.lhelp = html.HtmlWindow(lpanel, -1, style=wx.NO_BORDER)
        self.rhelp = html.HtmlWindow(rpanel, -1, style=wx.NO_BORDER, size=(500,-1))

        # get the media path
        if pageToOpen != None:
            path = os.path.dirname(pageToOpen)
        else:
            from sans.models import get_data_path as model_path
            # Get models help model_function path
            path = model_path(media='media')

        self.path = os.path.join(path,"model_functions.html")
        self.path_pd = os.path.join(path,"pd_help.html")
        self.path_sm = os.path.join(path,"smear_computation.html")
        from sans.perspectives.fitting import get_data_path as fit_path
        fitting_path = fit_path(media='media')
        
        _html_file = {"status_bar_help.html":"Status Bar Help",
                      "load_data_help.html":"Load a File",
                      "simultaneous_fit_help.html":"Simultaneous Fit",
                      "single_fit_help.html":"Single Fit",
                      "model_use_help.html":"Model Selection",
                      "key_help.html":"Key Combination",
                      }

                    
        page1="""<html>
            <body>
             <p>Select topic on Menu</p>
            </body>
            </html>"""
        page="""<html>
            <body>
            <ul>
            """
        for p, title in _html_file.iteritems():
            pp = os.path.join(fitting_path, p)
            page += """<li><a href ="%s" target="showframe">%s</a><br></li>""" % (pp, title)
          
        page += """
            <li><a href ="%s" target="showframe">Model Functions</a><br></li>
            <li><a href ="%s" target="showframe">Polydispersion Distributions</a><br></li>
            <li><a href ="%s" target="showframe">Smear Computation</a><br></li>
            </ul>
            </body>
            </html>""" % (self.path, self.path_pd, self.path_sm)
        
        self.rhelp.SetPage(page1)
        self.lhelp.SetPage(page)
        self.lhelp.Bind(wx.html.EVT_HTML_LINK_CLICKED,self.OnLinkClicked )
        
        #open the help frame a the current page
        if  pageToOpen!= None:
            self.rhelp.LoadPage(str( pageToOpen))
            
        vbox.Add(self.rhelp,1, wx.EXPAND)
        vboxl.Add(self.lhelp, 1, wx.EXPAND)
        rpanel.SetSizer(vbox)
        lpanel.SetSizer(vboxl)
        lpanel.SetFocus()
        
        vbox1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox1.Add(splitter,1,wx.EXPAND)
        splitter.AppendWindow(lpanel, 200)
        splitter.AppendWindow(rpanel)
        self.SetSizer(vbox1)
       
        self.Centre()
        self.Show(True)
        
    def OnButtonClicked(self, event):
        """
        Function to diplay Model html page related to the hyperlinktext selected
        """
        
        self.rhelp.LoadPage(self.path)
        
    def OnLinkClicked(self, event):
        """
        Function to diplay html page related to the hyperlinktext selected
        """
        link= event.GetLinkInfo().GetHref()
        
        self.rhelp.LoadPage(os.path.abspath(link))
        
"""
Example: ::

    class ViewApp(wx.App):
        def OnInit(self):
            frame = HelpWindow(None, -1, 'HelpWindow')    
            frame.Show(True)
            self.SetTopWindow(frame)
            
            return True
            
    
    if __name__ == "__main__": 
    app = ViewApp(0)
    app.MainLoop()  

"""   
