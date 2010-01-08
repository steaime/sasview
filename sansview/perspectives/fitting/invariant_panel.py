"""
    This module provide GUI for the neutron scattering length density calculator
    @author: Gervaise B. Alina
"""

import wx
import sys

from sans.invariant import invariant
from sans.guiframe.dataFitting import Theory1D
from sans.guiframe.utils import format_number, check_float
from sans.guicomm.events import NewPlotEvent, StatusEvent

# The minimum q-value to be used when extrapolating
Q_MINIMUM  = 1e-5
# The maximum q-value to be used when extrapolating
Q_MAXIMUM  = 10
# the number of points to consider during fit
NPTS = 10
#Default value for background
BACKGROUND = 0.0
#default value for the scale
SCALE = 1.0
#Invariant panel size 
_BOX_WIDTH = 76
_SCALE = 1e-6

if sys.platform.count("win32")>0:
    _STATICBOX_WIDTH = 450
    PANEL_WIDTH = 500
    PANEL_HEIGHT = 700
    FONT_VARIANT = 0
else:
    _STATICBOX_WIDTH = 480
    PANEL_WIDTH = 530
    PANEL_HEIGHT = 700
    FONT_VARIANT = 1
    
class InvariantPanel(wx.Panel):
    """
        Provides the Invariant GUI.
    """
    ## Internal nickname for the window, used by the AUI manager
    window_name = "Invariant"
    ## Name to appear on the window title bar
    window_caption = "Invariant"
    ## Flag to tell the AUI manager to put this panel in the center pane
    CENTER_PANE = True
    def __init__(self, parent, data=None, base=None):
        wx.Panel.__init__(self, parent)
        #Font size 
        self.SetWindowVariant(variant=FONT_VARIANT)
        #Object that receive status event
        self.parent = base
      
        #Default power value
        self.power_law_exponant = 4 
        
        #Data uses for computation
        self.data = data
        #Draw the panel
        self._do_layout()
        self.SetAutoLayout(True)
        self.Layout()
       
    def compute_invariant(self, event):
        """
            compute invariant 
        """
        #clear outputs textctrl 
        self._reset_output()
        background = self.background_ctl.GetValue().lstrip().rstrip()
        scale = self.scale_ctl.GetValue().lstrip().rstrip()
        if background == "":
            background = 0
        if scale == "":
            scale = 1
        if check_float(self.background_ctl) and check_float(self.scale_ctl):
            inv = invariant.InvariantCalculator(data=self.data,
                                      background=float(background),
                                       scale=float(scale))
            
            low_q = self.enable_low_cbox.GetValue() 
            high_q = self.enable_high_cbox.GetValue()
            
            #Get the number of points to extrapolated
            npts_low = self.npts_low_ctl.GetValue()
            if check_float(self.npts_low_ctl):
                npts_low = float(npts_low)
            power_low = self.power_low_ctl.GetValue()
            if check_float(self.power_low_ctl):
                power_low = float(power_low)
            npts_high = self.npts_high_ctl.GetValue()    
            if check_float(self.npts_high_ctl):
                npts_high = float(npts_high)
            power_high = self.power_high_ctl.GetValue()
            if check_float(self.power_high_ctl):
                power_high = float(power_high)
            # get the function
            if self.power_law_low.GetValue():
                function_low = "power_law"
            if self.guinier.GetValue():
                function_low = "guinier"
                #power_low = None
                
            function_high = "power_law"
            if self.power_law_high.GetValue():
                function_high = "power_law"
            #check the type of extrapolation
            extrapolation = None
            if low_q  and not high_q:
                extrapolation = "low"
            elif not low_q  and high_q:
                extrapolation = "high"
            elif low_q and high_q:
                extrapolation = "both"
                
            #Set the invariant calculator
            inv.set_extrapolation(range="low", npts=npts_low,
                                       function=function_low, power=power_low)
            inv.set_extrapolation(range="high", npts=npts_high,
                                       function=function_high, power=power_high)
            #Compute invariant
            try:
                qstar, qstar_err = inv.get_qstar_with_error()
                self.invariant_ctl.SetValue(format_number(qstar))
                self.invariant_err_ctl.SetValue(format_number(qstar))
                check_float(self.invariant_ctl)
                check_float(self.invariant_err_ctl)
            except:
                raise
                #msg= "Error occurs for invariant: %s"%sys.exc_value
                #wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
                #return
            #Compute qstar extrapolated to low q range
            #Clear the previous extrapolated plot
            self._plot_data( name=self.data.name+" Extra_low_Q")
            self._plot_data( name=self.data.name+" Extra_high_Q")
            if low_q:
                try: 
                    qstar_low = inv.get_qstar_low()
                    self.invariant_low_ctl.SetValue(format_number(qstar_low))
                    check_float(self.invariant_low_ctl)
                    #plot data
                    low_data = inv.get_extra_data_low()
                    self._plot_data(data=low_data, name=self.data.name+" Extra_low_Q")
                except:
                    raise
                    #msg= "Error occurs for low q invariant: %s"%sys.exc_value
                    #wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
            if high_q:
                try: 
                    qstar_high = inv.get_qstar_high()
                    self.invariant_high_ctl.SetValue(format_number(qstar_high))
                    check_float(self.invariant_high_ctl)
                    #plot data
                    high_data = inv.get_extra_data_high()
                    self._plot_data(data=high_data, name=self.data.name+" Extra_high_Q")
                except:
                    raise
                    #msg= "Error occurs for high q invariant: %s"%sys.exc_value
                    #wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
            try:
                qstar_total, qstar_total_err = inv.get_qstar_with_error(extrapolation)
                self.invariant_total_ctl.SetValue(format_number(qstar_total))
                self.invariant_total_err_ctl.SetValue(format_number(qstar_total))
                check_float(self.invariant_total_ctl)
                check_float(self.invariant_total_err_ctl)
            except:
                raise
                #msg= "Error occurs for total invariant: %s"%sys.exc_value
                #wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
                
            contrast = self.contrast_ctl.GetValue().lstrip().rstrip()
            if not check_float(self.contrast_ctl):
                contrast = None
            else:
                contrast = float(contrast)
            porod_const = self.porod_const_ctl.GetValue().lstrip().rstrip()
            if not check_float(self.porod_const_ctl):
                porod_const = None
            else:
                porod_const = float(porod_const)
            try:
                v, dv = inv.get_volume_fraction_with_error(contrast=contrast)
                self.volume_ctl.SetValue(format_number(v))
                self.volume_err_ctl.SetValue(format_number(dv))
                check_float(self.volume_ctl)
                check_float(self.volume_err_ctl)
            except:
                raise
                #msg= "Error occurs for volume fraction: %s"%sys.exc_value
                #wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
            try:
                s, ds = inv.get_surface_with_error(contrast=contrast,
                                        porod_const=porod_const)
                self.surface_ctl.SetValue(format_number(s))
                self.surface_err_ctl.SetValue(format_number(ds))
                check_float(self.surface_ctl)
                check_float(self.surface_err_ctl)
            except:
                raise
                #msg= "Error occurs for surface: %s"%sys.exc_value
                #wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
                
        else:
            msg= "invariant: Need float for background and scale"
            wx.PostEvent(self.parent, StatusEvent(status= msg, type="stop"))
            return
        
    def _plot_data(self, data=None, name="Unknown"):
        """
            Receive a data and post a NewPlotEvent to parent
            @param data: data created frome xtrapolation to plot
            @param name: Data's name to use for the legend
        """
        # Create a plottable data
        new_plot = Theory1D(x=[], y=[], dy=None)
        if data is not None:
            new_plot.copy_from_datainfo(data) 
            data.clone_without_data(clone=new_plot) 
            
        new_plot.name = name
        title = self.data.name
        new_plot.xaxis(self.data._xaxis, self.data._xunit)
        new_plot.yaxis(self.data._yaxis, self.data._yunit)
        new_plot.group_id = self.data.group_id
        new_plot.id = self.data.id + name
        ##post data to plot
        wx.PostEvent(self.parent, NewPlotEvent(plot=new_plot, title=title))
        
    def _reset_output(self):
        """
            clear outputs textcrtl
        """
        self.invariant_ctl.Clear()
        self.invariant_err_ctl.Clear()
        self.invariant_low_ctl.Clear()
        self.invariant_high_ctl.Clear()
        self.invariant_total_ctl.Clear()
        self.invariant_total_err_ctl.Clear()
        self.volume_ctl.Clear()
        self.volume_err_ctl.Clear()
        self.surface_ctl.Clear()
        self.surface_err_ctl.Clear()
        
    def _do_layout(self):
        """
            Draw window content
        """
        unit_invariant = '[1/cm][1/A]'
        unit_volume = ''
        unit_surface = ''
        uncertainty = "+/-"
        npts_hint_txt = "Number of points to consider during extrapolation."
        power_hint_txt = "Exponent to apply to the Power_law function."
        
        sizer_input = wx.FlexGridSizer(5,4)#wx.GridBagSizer(5,5)
        sizer_output = wx.GridBagSizer(5,5)
        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer1.SetMinSize((_STATICBOX_WIDTH, -1))
        sizer2.SetMinSize((_STATICBOX_WIDTH, -1))
        sizer3.SetMinSize((_STATICBOX_WIDTH, -1))
        #---------inputs----------------
        data_txt = wx.StaticText(self, -1, 'Data : ')
        data_name = ""
        data_range = "[? - ?]"
        if self.data is not None:
            data_name = self.data.name
            data_qmin = min (self.data.x)
            data_qmax = max (self.data.x)
            data_range = "[%s - %s]"%(str(data_qmin), str(data_qmax))
            
        data_name_txt = wx.StaticText(self, -1, str(data_name))
        data_range_txt = wx.StaticText(self, -1, "Range : ")
        data_range_value_txt = wx.StaticText(self, -1, str(data_range))
        
        background_txt = wx.StaticText(self, -1, 'Background')
        self.background_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.background_ctl.SetValue(str(BACKGROUND))
        self.background_ctl.SetToolTipString("Background to subtract to data.")
        scale_txt = wx.StaticText(self, -1, 'Scale')
        self.scale_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.scale_ctl.SetValue(str(SCALE))
        self.scale_ctl.SetToolTipString("Scale to apply to data.")
        contrast_txt = wx.StaticText(self, -1, 'Contrast')
        self.contrast_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.contrast_ctl.SetToolTipString("Contrast in q range.")
        porod_const_txt = wx.StaticText(self, -1, 'Porod Constant')
        self.porod_const_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.porod_const_ctl.SetToolTipString("Invariant in q range.")
       
        sizer_input.Add(data_txt, 0, wx.LEFT, 5)
        sizer_input.Add(data_name_txt)
        sizer_input.Add(data_range_txt, 0, wx.LEFT, 10)
        sizer_input.Add(data_range_value_txt)
        sizer_input.Add(background_txt, 0, wx.ALL, 5)
        sizer_input.Add(self.background_ctl, 0, wx.ALL, 5)
        sizer_input.Add((10,10))
        sizer_input.Add((10,10))
        sizer_input.Add(scale_txt, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer_input.Add(self.scale_ctl, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer_input.Add((10,10))
        sizer_input.Add((10,10))
        sizer_input.Add(contrast_txt, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer_input.Add(self.contrast_ctl, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer_input.Add((10,10))
        sizer_input.Add((10,10))
        sizer_input.Add(porod_const_txt, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer_input.Add(self.porod_const_ctl, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        #-------------Extrapolation sizer----------------
        sizer_low_q = wx.GridBagSizer(5,5)
        
        self.enable_low_cbox = wx.CheckBox(self, -1, "Enable low Q")
        self.enable_low_cbox.SetValue(False)
        self.enable_high_cbox = wx.CheckBox(self, -1, "Enable High Q")
        self.enable_high_cbox.SetValue(False)
        
        self.guinier = wx.RadioButton(self, -1, 'Guinier',
                                         (10, 10),style=wx.RB_GROUP)
        self.power_law_low = wx.RadioButton(self, -1, 'Power_law', (10, 10))
        #self.Bind(wx.EVT_RADIOBUTTON, self._set_dipers_Param,
        #           id=self.guinier.GetId())
        #self.Bind(wx.EVT_RADIOBUTTON, self._set_dipers_Param,
        #           id=self.power_law_law.GetId())
        #MAC needs SetValue
        self.guinier.SetValue(True)
        
        npts_low_txt = wx.StaticText(self, -1, 'Npts')
        self.npts_low_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/3, -1))
        self.npts_low_ctl.SetValue(str(NPTS))
        self.power_low_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/3, -1))
        self.power_low_ctl.SetValue(str(self.power_law_exponant))
        self.power_low_ctl.SetToolTipString(power_hint_txt)
        iy = 0
        ix = 0
        sizer_low_q.Add(self.guinier,(iy, ix),(1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        iy += 1
        ix = 0
        sizer_low_q.Add(self.power_law_low,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        sizer_low_q.Add(self.power_low_ctl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        iy += 1
        ix = 0
        sizer_low_q.Add(npts_low_txt,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        sizer_low_q.Add(self.npts_low_ctl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        iy += 1
        ix = 0
        sizer_low_q.Add(self.enable_low_cbox,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        sizer_high_q = wx.GridBagSizer(5,5)
        self.power_law_high = wx.RadioButton(self, -1, 'Power_law',
                                              (10, 10), style=wx.RB_GROUP)
        #self.Bind(wx.EVT_RADIOBUTTON, self._set_dipers_Param,
        #           id=self.power_law_high.GetId())
        #MAC needs SetValue
        self.power_law_high.SetValue(True)
        npts_high_txt = wx.StaticText(self, -1, 'Npts')
        self.npts_high_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/3, -1))
        self.npts_high_ctl.SetValue(str(NPTS))
        self.power_high_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH/3, -1))
        self.power_high_ctl.SetValue(str(self.power_law_exponant))
        self.power_high_ctl.SetToolTipString(power_hint_txt)
        
        iy = 1
        ix = 0
        sizer_high_q.Add(self.power_law_high,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        sizer_high_q.Add(self.power_high_ctl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        iy += 1
        ix = 0
        sizer_high_q.Add(npts_high_txt,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        sizer_high_q.Add(self.npts_high_ctl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        iy += 1
        ix = 0
        sizer_high_q.Add(self.enable_high_cbox,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        
        high_q_box = wx.StaticBox(self, -1, "High Q")
        boxsizer_high_q = wx.StaticBoxSizer(high_q_box, wx.VERTICAL)
        boxsizer_high_q.Add(sizer_high_q)
        
        low_q_box = wx.StaticBox(self, -1, "Low Q")
        boxsizer_low_q = wx.StaticBoxSizer(low_q_box, wx.VERTICAL)
        boxsizer_low_q.Add(sizer_low_q)
        
        #-------------Enable extrapolation-------
        extra_hint = "Extrapolation Maximum Range: "
        extra_hint_txt= wx.StaticText(self, -1,extra_hint )
        enable_sizer = wx.BoxSizer(wx.HORIZONTAL)
        extra_range = "[%s - %s]"%(str(Q_MINIMUM), str(Q_MAXIMUM))
        extra_range_value_txt = wx.StaticText(self, -1, str(extra_range))
        enable_sizer.Add(extra_hint_txt, 0, wx.ALL, 5)
        enable_sizer.Add(extra_range_value_txt, 0, wx.ALL, 5)
        
        type_extrapolation_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_extrapolation_sizer.Add((10,10))
        type_extrapolation_sizer.Add(boxsizer_low_q, 0, wx.ALL, 10)
        type_extrapolation_sizer.Add((20,20))
        type_extrapolation_sizer.Add(boxsizer_high_q, 0, wx.ALL, 10)
        type_extrapolation_sizer.Add((10,10))
        
        extrapolation_box = wx.StaticBox(self, -1, "Extrapolation")
        boxsizer_extra = wx.StaticBoxSizer(extrapolation_box, wx.VERTICAL)
        boxsizer_extra.Add(enable_sizer, 0, wx.ALL, 10)
        boxsizer_extra.Add(type_extrapolation_sizer)
    
        inputbox = wx.StaticBox(self, -1, "Input")
        boxsizer1 = wx.StaticBoxSizer(inputbox, wx.VERTICAL)
        boxsizer1.SetMinSize((_STATICBOX_WIDTH,-1))
        boxsizer1.Add(sizer_input)
        boxsizer1.Add(boxsizer_extra, 0, wx.ALL, 10)
        sizer1.Add(boxsizer1,0, wx.EXPAND | wx.ALL, 10)
        
        #---------Outputs sizer--------
        invariant_txt = wx.StaticText(self, -1, 'Invariant')
        self.invariant_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_ctl.SetEditable(False)
        self.invariant_ctl.SetToolTipString("Invariant in q range.")
        self.invariant_err_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_err_ctl.SetEditable(False)
        self.invariant_err_ctl.SetToolTipString("Uncertainty on invariant.")
        invariant_units_txt = wx.StaticText(self, -1, unit_invariant)
        
        invariant_total_txt = wx.StaticText(self, -1, 'Invariant Total')
        self.invariant_total_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_total_ctl.SetEditable(False)
        self.invariant_total_ctl.SetToolTipString("Invariant in q range and extra\
                   polated range.")
        self.invariant_total_err_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_total_err_ctl.SetEditable(False)
        self.invariant_total_err_ctl.SetToolTipString("Uncertainty on invariant.")
        invariant_total_units_txt = wx.StaticText(self, -1, unit_invariant)
        
        volume_txt = wx.StaticText(self, -1, 'Volume Fraction')
        self.volume_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.volume_ctl.SetEditable(False)
        self.volume_ctl.SetToolTipString("volume fraction.")
        self.volume_err_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.volume_err_ctl.SetEditable(False)
        self.volume_err_ctl.SetToolTipString("Uncertainty of volume fraction.")
        volume_units_txt = wx.StaticText(self, -1, unit_volume)
        
        surface_txt = wx.StaticText(self, -1, 'Surface')
        self.surface_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.surface_ctl.SetEditable(False)
        self.surface_ctl.SetToolTipString("Surface.")
        self.surface_err_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.surface_err_ctl.SetEditable(False)
        self.surface_err_ctl.SetToolTipString("Uncertainty of surface.")
        surface_units_txt = wx.StaticText(self, -1, unit_surface)
        
        invariant_low_txt = wx.StaticText(self, -1, 'Invariant in low Q')
        self.invariant_low_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_low_ctl.SetEditable(False)
        self.invariant_low_ctl.SetToolTipString("Invariant compute in low Q")
        invariant_low_units_txt = wx.StaticText(self, -1,  unit_invariant)
        
        invariant_high_txt = wx.StaticText(self, -1, 'Invariant in high Q')
        self.invariant_high_ctl = wx.TextCtrl(self, -1, size=(_BOX_WIDTH,-1))
        self.invariant_high_ctl.SetEditable(False)
        self.invariant_high_ctl.SetToolTipString("Invariant compute in high Q")
        invariant_high_units_txt = wx.StaticText(self, -1,  unit_invariant)
       
        iy = 0
        ix = 0
        sizer_output.Add(invariant_low_txt, (iy, ix), (1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix +=1
        sizer_output.Add(self.invariant_low_ctl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 2
        sizer_output.Add(invariant_low_units_txt, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        iy += 1
        ix = 0 
        sizer_output.Add(invariant_high_txt, (iy, ix), (1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix +=1
        sizer_output.Add(self.invariant_high_ctl, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, )
        ix += 2
        sizer_output.Add(invariant_high_units_txt, (iy, ix), (1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        iy += 1
        ix = 0
        sizer_output.Add(invariant_txt,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        sizer_output.Add(self.invariant_ctl,(iy, ix),(1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        sizer_output.Add( wx.StaticText(self, -1, uncertainty),
                         (iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        sizer_output.Add(self.invariant_err_ctl
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        sizer_output.Add(invariant_units_txt
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        iy += 1
        ix = 0
        sizer_output.Add(invariant_total_txt,(iy, ix),(1,1),
                            wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix += 1
        sizer_output.Add(self.invariant_total_ctl,(iy, ix),(1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix += 1
        sizer_output.Add( wx.StaticText(self, -1, uncertainty),
                         (iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        sizer_output.Add(self.invariant_total_err_ctl
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        sizer_output.Add(invariant_total_units_txt,(iy, ix),
                        (1,1),wx.RIGHT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        iy += 1
        ix = 0
        sizer_output.Add(volume_txt,(iy, ix),(1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix +=1
        sizer_output.Add(self.volume_ctl,(iy, ix),(1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        sizer_output.Add(wx.StaticText(self, -1, uncertainty)
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        sizer_output.Add(self.volume_err_ctl
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)  
        ix += 1
        sizer_output.Add(volume_units_txt
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        iy += 1
        ix = 0
        sizer_output.Add(surface_txt,(iy, ix),(1,1),
                             wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        ix +=1
        sizer_output.Add(self.surface_ctl,(iy, ix),(1,1),
                            wx.EXPAND|wx.ADJUST_MINSIZE, 0) 
        ix +=1
        sizer_output.Add(wx.StaticText(self, -1, uncertainty)
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        ix += 1
        sizer_output.Add(self.surface_err_ctl
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)  
        ix +=1
        sizer_output.Add(surface_units_txt
                         ,(iy, ix),(1,1),wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        
        outputbox = wx.StaticBox(self, -1, "Output")
        boxsizer2 = wx.StaticBoxSizer(outputbox, wx.VERTICAL)
        boxsizer2.SetMinSize((_STATICBOX_WIDTH,-1))
        boxsizer2.Add( sizer_output )
        sizer2.Add(boxsizer2,0, wx.EXPAND|wx.ALL, 10)
        #-----Button  sizer------------
        id = wx.NewId()
        button_calculate = wx.Button(self, id, "Compute")
        button_calculate.SetToolTipString("Compute SlD of neutrons.")
        self.Bind(wx.EVT_BUTTON, self.compute_invariant, id = id)   
        
        sizer_button.Add((250, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_button.Add(button_calculate, 0, wx.RIGHT|wx.ADJUST_MINSIZE,20)
        sizer3.Add(sizer_button)
        #---------layout----------------
        vbox  = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sizer1)
        vbox.Add(sizer2)
        vbox.Add(sizer3)
        vbox.Fit(self) 
        self.SetSizer(vbox)
    
class InvariantDialog(wx.Dialog):
    def __init__(self, parent=None, id=1,data=None, title="Invariant",base=None):
        wx.Dialog.__init__(self, parent, id, title, size=( PANEL_WIDTH,
                                                             PANEL_HEIGHT))
        self.panel = InvariantPanel(self, data=data, base=base)
        self.Centre()
        self.Show(True)
        
class InvariantWindow(wx.Frame):
    def __init__(self, parent=None, id=1,data=None, title="SLD Calculator",base=None):
        wx.Frame.__init__(self, parent, id, title, size=( PANEL_WIDTH,
                                                             PANEL_HEIGHT))
        
        self.panel = InvariantPanel(self, data=data, base=base)
        self.Centre()
        self.Show(True)
        
class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = InvariantWindow()
        frame.Show(True)
        self.SetTopWindow(frame)
        
        return True
        #wx.InitAllImageHandlers()
        #dialog = InvariantDialog(None)
        #if dialog.ShowModal() == wx.ID_OK:
        #    pass
        #dialog.Destroy()
        #return 1
   
# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()