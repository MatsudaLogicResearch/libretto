import argparse, re, os, shutil, subprocess
import numpy as np
import statistics as st

from pydantic import BaseModel, model_validator, Field, PrivateAttr
from typing import Any, Dict, List, DefaultDict,Annotated,Literal
from collections import defaultdict


#import myExpectLogic as Mel
from myExpectLogic    import MyExpectLogic as Mel

from myLibrarySetting import MyLibrarySetting as Mls 
from myLogicCell      import MyLogicCell as Mlc

from myFunc import my_exit

DictKey=Literal["prop","trans",
                "energy_start","energy_end",
                "q_in_dyn", "q_out_dyn", "q_vdd_dyn","q_vss_dyn","i_in_leak","i_vdd_leak","i_vss_leak",
                "eintl","ein","cin", "pleak"]
  
LutKey = Literal["prop","trans","eintl","ein"]

AvgKey = Literal["cin","pleak"]

NestedDefaultDict = Annotated[
    DefaultDict[float, float],  # slope -> value
    Field(default_factory=lambda: defaultdict(float))
]

Level2Dict = Annotated[
    DefaultDict[float, NestedDefaultDict],  # load -> (slope -> value)
    Field(default_factory=lambda: defaultdict(lambda: defaultdict(float)))
]

Level3Dict = Annotated[
    DefaultDict[DictKey, Level2Dict],  # name -> load -> slope -> value
    Field(default_factory=lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))
]

class MyConditionsAndResults(BaseModel):
  #=====================================
  # class variable
  
  #=====================================
  # instance variable by BaseModel
  #self.instance = None          ## instance name

  #-- reference
  mls: Mls
  mlc: Mlc
  
  #-- for myExpectLogic
  mel: Mel = Field(default_factory=Mel)

  direction_prop : str = ""
  direction_tran : str = ""
  direction_power: str = ""
  timing_type    : str = ""
  timing_sense   : str = ""
  timing_unate   : str = ""
  timing_when    : str = ""
  constraint     : str = ""

  target_relport        : str = ""
  target_relport_val    : str = ""
  target_outport        : str = ""
  target_outport_val    : str = ""
  
  stable_inport         : list[str] = Field(default_factory=list)
  stable_inport_val     : list[str] = Field(default_factory=list)
  nontarget_outport     : list[str] = Field(default_factory=list)
  nontarget_outport_val : list[str] = Field(default_factory=list)

  #-- hold result from spice simulation ([load][slope])
  dict_list2: Level3Dict  
    
  #dict_prop_in_out : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_trans_out   : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_energy_start: DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_energy_end  : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_q_in_dyn    : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_q_out_dyn   : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_q_vdd_dyn   : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_q_vss_dyn   : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_i_in_leak   : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_i_vdd_leak  : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #dict_i_vss_leak  : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float))); 
  #
  #dict_eintl       : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float)));
  #dict_ein         : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float)));
  #dict_cin         : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float)));
  #dict_pleak       : DefaultDict[str, NestedDefaultDict] = Field(default_factory=lambda: defaultdict(lambda: defaultdict(float)));
  
  #
  lut: dict[LutKey, list[float]] = Field(
    default_factory=lambda: {key: [] for key in LutKey.__args__}
  )

  lut_min2max: dict[LutKey, list[float]] = Field(
    default_factory=lambda: {key: [] for key in LutKey.__args__}
  )
  
  #
  avg: dict[AvgKey, float] = Field(
    default_factory=lambda: {key: [] for key in AvgKey.__args__}
  )
  
  #list2_prop        : list[float] = Field(default_factory=list)
  #lut_prop          : list[float] = Field(default_factory=list)
  #lut_prop_mintomax : list[float] = Field(default_factory=list)
  
  #list2_tran        : list[float] = Field(default_factory=list)
  #lut_tran          : list[float] = Field(default_factory=list)
  #lut_tran_mintomax : list[float] = Field(default_factory=list)

  #list2_eintl       : list[float] = Field(default_factory=list)
  #lut_eintl         : list[float] = Field(default_factory=list)
  #lut_eintl_mintomax: list[float] = Field(default_factory=list)

  #list2_ein         : list[float] = Field(default_factory=list)
  #lut_ein           : list[float] = Field(default_factory=list)
  #lut_ein_mintomax  : list[float] = Field(default_factory=list)

  #cin               : float       = 0.0
  #list2_cin         : list[float] = Field(default_factory=list)
  #lut_cin           : list[float] = Field(default_factory=list)
  #lut_cin_mintomax  : list[float] = Field(default_factory=list)

  #pleak               : float       = 0.0
  #list2_pleak         : list[float] = Field(default_factory=list)
  #lut_pleak           : list[float] = Field(default_factory=list)
  #lut_pleak_mintomax  : list[float] = Field(default_factory=list)
  
  #def __init__ (self):

  #@property
  #def mls(self) -> Mls:
  #  return self._mls;  #--- no setter
  #
  #@property
  #def mlc(self) -> Mlc:
  #  return self._mlc;  #--- no setter
  
  def set_update(self):
    self.set_timing_type()
    self.set_timing_sense()
    self.set_timing_when()
    self.set_direction()
    self.set_constraint()
    self.set_target_relport()
    self.set_target_outport()
    self.set_stable_inport()
    self.set_nontarget_outport()
    
  def set_direction(self):
    arc=self.mel.arc_otr[1]
    if(arc == 'r'):
      self.set_direction_rise()
    elif(arc == 'f'):
      self.set_direction_fall()
    else:
      print("Illegal arc: "+arc+", check direction in myExpectLogic2.py")
      my_exit()
      
  def set_direction_rise(self):
    self.direction_prop  = "cell_rise"
    self.direction_tran  = "rise_transition"
    self.direction_power = "rise_power"

  def set_direction_fall(self):
    self.direction_prop = "cell_fall"
    self.direction_tran = "fall_transition"
    self.direction_power = "fall_power"

  def set_timing_type(self):
    self.timing_type = self.mel.tmg_type

  def set_timing_sense(self):
    if(self.mel.tmg_sense== 'pos'):
      self.timing_sense = "positive_unate"
    elif(self.mel.tmg_sense== 'neg'):
      self.timing_sense = "negative_unate"
    elif(self.mel.tmg_sense == 'non'):
      self.timing_sense = "non_unate"
    else:
      print("Illegal input: " + self.mel.tmg_sense+", check tmg_sense.")
      my_exit()
      
  def set_timing_when(self):
    self.timing_when = self.mel.tmg_when

  def set_constraint(self):
    arc=self.mel.arc_otr[1]
    if (arc == "r"):
      self.constraint = "rise_constraint"
    elif (arc == "f"):
      self.constraint = "fall_constraint"
    else:
      print("Illegal arc_t: "+ arc +", check arc")

  def set_function(self):
    self.function = self.mel.function 

#  def set_target_inport(self, inport="tmp", val="01"):
#    self.target_inport = inport
#    self.target_inport_val = val
#    #print(self.target_inport_val)
#    #print(self.target_inport)

  def set_target_relport(self):
    rel=self.mel.pin_otr[2]
    pin=rel[0]
    pos=int(rel[1:])

    ival = self.mel.ival;          #initial value dict
    nval = self.mel.mondrv_otr[2]; #next    value of relatedpin
    
    val0 = ival[pin][pos] if (pin in ival and pos < len(ival[pin])) else ""

    if val0 and nval:
      self.target_relport      = rel
      self.target_relport_val  = val0 + nval
    else :
      print(f"Error related port value error(ival={val0},mondrv={nval}).")
      my_exit();

#  def set_target_outport(self, outport="tmp", function="tmp", val="01"):
#    self.target_outport = outport
#    self.target_function = function
#    self.target_outport_val = val
#    
#    #print(self.target_outport_val)
#    #print(self.target_outport)
#    #print(self.target_function)

  def set_target_outport(self):
    out=self.mel.pin_otr[0]
    pin=out[0]
    pos=int(out[1:])

    ival = self.mel.ival;          #initial value dict
    nval = self.mel.mondrv_otr[0]; #next    value of outport
    
    val0 = ival[pin][pos] if (pin in ival and pos < len(ival[pin])) else ""

    if val0 and  nval:
      self.target_outport      = out
      self.target_outport_val  = val0 + nval
    else :
      print(f"Error out port value error(ival={val0},mondrv={nval}).")
      my_exit();

#  def set_stable_inport(self, inport="tmp", val="1"):
#    self.stable_inport.append(inport)
#    self.stable_inport_val.append(val)
#    #print(self.stable_inport)
#    #print(self.stable_inport_val)

  def set_stable_inport(self):
    rel_pin=self.mel.pin_otr[2]
    for typ in ["i", "b", "c", "r", "s"]:
      values=self.mel.ival.get(typ,[])
      for i in range (len(values)):
        pin=typ+"{:}".format(i)
        if rel_pin != pin:
          self.stable_inport.append(pin)
          self.stable_inport_val.append(self.mel.ival[typ][i])

          
#  def set_nontarget_outport(self, outport="tmp"):
#    self.stable_nontarget.append(outport)
#    #print(self.outport)

  def set_nontarget_outport(self, outport="tmp"):
    typ="o"
    values=self.mel.ival.get(typ,[])
    out_pin=self.mel.pin_otr[0]
    for i in range (len(values)):
      pin=typ+"{:}".format(i)
      if out_pin != pin:
        self.nontarget_outport.append(pin)
        self.nontarget_outport.append(self.mel.ival[typ][i])

#  def set_target_clock(self, inport="tmp", val="01"):
#    self.target_clock = inport
#    self.target_clock_val = val
#    #print(self.target_clock_val)
#    #print(self.target_clock)
#
#  def set_target_reset(self, inport="tmp", val="01"):
#    self.target_reset = inport
#    self.target_reset_val = val
#    #print(self.target_reset_val)
#    #print(self.target_reset)
#
#  def set_target_set(self, inport="tmp", val="01"):
#    self.target_set = inport
#    self.target_set_val = val
#    #print(self.target_set_val)
#    #print(self.target_set)
#
#  def invert_set_reset_val(self):
#    if(self.target_reset_val == '01'):
#      self.target_reset_val = '10'
#    elif(self.target_reset_val == '10'):
#      self.target_reset_val = '01'
#    if(self.target_set_val == '01'):
#      self.target_set_val = '10'
#    elif(self.target_set_val == '10'):
#      self.target_set_val = '01'
#
#  def invert_outport_val(self):
#    if(self.target_outport_val == '01'):
#      self.target_outport_val = '10'
#    elif(self.target_outport_val == '10'):
#      self.target_outport_val = '01'

  ## propagation delay table
  #def set_list2_prop(self, list2_prop=[]):
  #  self.list2_prop = list2_prop 
  #
  #def print_list2_prop(self, ilist, jlist):
  #  for i in range(len(ilist)):
  #    for j in range(len(jlist)):
  #      print(self.list2_prop[i][j])
  
  #def print_lut_prop(self):
  #  for i in range(len(self.lut_prop)):
  #    print(self.lut_prop[i])

#  def write_list2_prop(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_prop = []
#    self.lut_prop_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_prop.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_prop.append(outline)
#    ## values
#    self.lut_prop.append("values ( \\")
#    #print(self.list2_prop)
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_prop[i][j])+", "
#        #print("i,j"+str(i)+","+str(j))
#        #print(len(ilist))
#        #print(len(jlist)-1)
#        #print(len(self.list2_prop))
#        #print([len(v) for v in self.list2_prop])
#        #print(self.list2_prop[i][j])
#        tmp_line = str("{:5f}".format(self.list2_prop[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_prop[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_prop[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_prop[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_prop[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_prop.append(outline)
#    self.lut_prop.append(");")
#    
#    # store min/center/max for doc
#    # min
#    #self.lut_prop_mintomax.append(str("{:5f}".format(self.list2_prop[0][0]/targetLib.time_mag)))
#    self.lut_prop_mintomax.append(str("{:5f}".format(np.amin(self.list2_prop)/targetLib.time_mag)))
#    
#    # center
#    #self.lut_prop_mintomax.append(str("{:5f}".format(self.list2_prop[int(len(ilist))-1][int(len(jlist))-1]/targetLib.time_mag)))
#    self.lut_prop_mintomax.append(str("{:5f}".format(np.median(self.list2_prop)/targetLib.time_mag)))
#
#    # max
#    #self.lut_prop_mintomax.append(str("{:5f}".format(self.list2_prop[-1][-1]/targetLib.time_mag)))
#    self.lut_prop_mintomax.append(str("{:5f}".format(np.amax(self.list2_prop)/targetLib.time_mag)))

#  def write_list2_prop(self, targetLib, tergetCell):
#    ## index_1
#    outline = ""
#    self.lut_prop = []
#    self.lut_prop_mintomax = []
#
#    ## index_1
#    outline = "index_1(\"" + ','.join(targetCell.slope) + "\");"
#    self.lut_prop.append(outline)
#    
#    ## index_2
#    outline = "index_2(\"" + ','.join(targetCell.load) + "\");"
#    self.lut_prop.append(outline)
#    
#    ## values
#    self.lut_prop.append("values ( \\")
#
#    for i,load in enumerate(targetCell.load):
#      outline = "\""
#
#      ## do not add "," 
#      str_colon=""
#      for slope in targetCell.slope:
#        tmp_line = str_colon + str("{:5f}".format(self.dict_prop_in_out[load][slope]/targetLib.time_mag))
#        outline += tmp_line
#
#        str_colon = ","
#        
#      ## do not add \ for last line
#      if i == len(targetCell.load - 1):
#        outline += tmp_line + "\""
#      else:
#        outline += tmp_line + "\",\\"
#
#      ## 
#      self.lut_prop.append(outline)
#
#      
#    self.lut_prop.append(");")
#    
#    # store min/center/max in middle load for doc
#    load_index=int(len(targetCell.load)/2)
#    load=targetCell.load[load_index]
#    
#    # min
#    #self.lut_prop_mintomax.append(str("{:5f}".format(self.list2_prop[0][0]/targetLib.time_mag)))
#    #self.lut_prop_mintomax.append(str("{:5f}".format(np.amin(self.list2_prop)/targetLib.time_mag)))
#    self.lut_prop_mintomax.append(str("{:5f}".format(min(self.dict_prop_in_out[load].values())/targetLib.time_mag)))
#    
#    # center
#    #self.lut_prop_mintomax.append(str("{:5f}".format(self.list2_prop[int(len(ilist))-1][int(len(jlist))-1]/targetLib.time_mag)))
#    #self.lut_prop_mintomax.append(str("{:5f}".format(np.median(self.list2_prop)/targetLib.time_mag)))
#    self.lut_prop_mintomax.append(str("{:5f}".format(median(self.dict_prop_in_out[load].values())/targetLib.time_mag)))
#
#    # max
#    #self.lut_prop_mintomax.append(str("{:5f}".format(self.list2_prop[-1][-1]/targetLib.time_mag)))
#    #self.lut_prop_mintomax.append(str("{:5f}".format(np.amax(self.list2_prop)/targetLib.time_mag)))
#    self.lut_prop_mintomax.append(str("{:5f}".format(max(self.dict_prop_in_out[load].values())/targetLib.time_mag)))
#
    
  ## transient delay table
  #def set_list2_tran(self, list2_tran=[]):
  #  self.list2_tran = list2_tran 

  #def print_list2_tran(self, ilist, jlist):
  #  for i in range(len(ilist)):
  #    for j in range(len(jlist)):
  #      print(self.list2_tran[i][j])
  
  #def print_lut_tran(self):
  #  for i in range(len(self.lut_tran)):
  #    print(self.lut_tran[i])

  def set_lut(self, name:str):
    outline=""
    self.lut[name]         = []
    self.lut_min2max[name] = []

    mag = self.mls.energy_mag if name in ["eintl","ein"] else self.mls.time_mag
    
    ## index_1
    #outline = "index_1(\"" + ','.join(self.mlc.slope) + "\");"
    outline = 'index_1("' + ','.join(map(str, self.mlc.slope)) + '");'
    
    self.lut[name].append(outline)
    
    ## index_2
    #outline = "index_1(\"" + ','.join(self.mlc.load) + "\");"
    outline = 'index_2("' + ','.join(map(str, self.mlc.load)) + '");'
    
    self.lut[name].append(outline)
    
    ## values
    self.lut[name].append("values ( \\")

    for i,load in enumerate(self.mlc.load):
      outline = "\""

      ## do not add "," 
      str_colon=""
      for slope in self.mlc.slope:
        tmp_line = str_colon + str("{:5f}".format(self.dict_list2[name][load][slope]/mag))
        outline += tmp_line
        
        str_colon = ","

      ## do not add \ for last line
      if i == (len(self.mlc.load) - 1):
        outline += "\""
      else:
        outline += "\",\\"

      ##
      self.lut[name].append(outline)
      
    self.lut[name].append(");")
    
    # store min/center/max for doc
    load_index=int(len(self.mlc.load)/2)
    load=self.mlc.load[load_index]
    
    # min
    #self.lut_tran_mintomax.append(str("{:5f}".format(np.amin(self.list2_tran)/targetLib.time_mag)))
    self.lut_min2max[name].append(str("{:5f}".format(min(self.dict_list2[name][load].values())/mag)))
    
    # center
    #self.lut_tran_mintomax.append(str("{:5f}".format(np.median(self.list2_tran)/targetLib.time_mag)))
    self.lut_min2max[name].append(str("{:5f}".format(st.median(self.dict_list2[name][load].values())/mag)))
    
    # max
    #self.lut_tran_mintomax.append(str("{:5f}".format(np.amax(self.list2_tran)/targetLib.time_mag)))
    self.lut_min2max[name].append(str("{:5f}".format(max(self.dict_list2[name][load].values())/mag)))

  
  
#  def write_list2_tran(self, targetLib, targetCell):
#    outline=""
#    self.lut_tran = []
#    self.lut_tran_mintomax = []
#
#    ## index_1
#    outline = "index_1(\"" + ','.join(targetCell.slope) + "\");"
#    self.lut_tran.append(outline)
#    
#    ## index_2
#    outline = "index_1(\"" + ','.join(targetCell.load) + "\");"
#    self.lut_tran.append(outline)
#    
#    ## values
#    self.lut_tran.append("values ( \\")
#
#    for i,load in enumerate(targetCell.load):
#      outline = "\""
#    
#      ## do not add "," 
#      str_colon=""
#      for slope in targetCell.slope:
#        tmp_line = str_colon + str("{:5f}".format(self.dict_trans_out[load][slope]/targetLib.time_mag))
#        outline += tmp_line
#        
#        str_colon = ","
#
#      ## do not add \ for last line
#      if i == len(targetCell.load - 1):
#        outline += tmp_line + "\""
#      else:
#        outline += tmp_line + "\",\\"
#
#      ##
#      self.lut_tran.append(outline)
#      
#    self.lut_tran.append(");")
#    
#    # store min/center/max for doc
#    load_index=int(len(targetCell.load)/2)
#    load=targetCell.load[load_index]
#    
#    # min
#    #self.lut_tran_mintomax.append(str("{:5f}".format(np.amin(self.list2_tran)/targetLib.time_mag)))
#    self.lut_tran_mintomax.append(str("{:5f}".format(min(self.dict_tran_out[load].values())/targetLib.time_mag)))
#    
#    # center
#    #self.lut_tran_mintomax.append(str("{:5f}".format(np.median(self.list2_tran)/targetLib.time_mag)))
#    self.lut_tran_mintomax.append(str("{:5f}".format(median(self.dict_tran_out[load].values())/targetLib.time_mag)))
#    
#    # max
#    #self.lut_tran_mintomax.append(str("{:5f}".format(np.amax(self.list2_tran)/targetLib.time_mag)))
#    self.lut_tran_mintomax.append(str("{:5f}".format(max(self.dict_tran_out[load].values())/targetLib.time_mag)))

  ## propagation delay table for set
  #def set_list2_prop_set(self, list2_prop_set=[]):
  #  self.list2_prop_set = list2_prop_set 

  #def print_list2_prop_set(self, ilist, jlist):
  #  for i in range(len(ilist)):
  #    for j in range(len(jlist)):
  #      print(self.list2_prop_set[i][j])
  
#  def print_lut_prop_set(self):
#    for i in range(len(self.lut_prop_set)):
#      print(self.lut_prop_set[i])
#
#  def write_list2_prop_set(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_prop_set = []
#    self.lut_prop_set_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_prop_set.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_prop_set.append(outline)
#    ## values
#    self.lut_prop_set.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_prop_set[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_prop_set[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_prop_set[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_prop_set[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_prop_set.append(outline)
#    self.lut_prop_set.append(");")
#    
#    # store min/center/max for doc
#    # min
#    self.lut_prop_set_mintomax.append(str("{:5f}".format(np.amin(self.list2_prop_set)/targetLib.time_mag)))
#    # center
#    self.lut_prop_set_mintomax.append(str("{:5f}".format(np.median(self.list2_prop_set)/targetLib.time_mag)))
#    # max
#    self.lut_prop_set_mintomax.append(str("{:5f}".format(np.amax(self.list2_prop_set)/targetLib.time_mag)))
#
#  ## transient delay table for set
#  def set_list2_tran_set(self, list2_tran_set=[]):
#    self.list2_tran_set = list2_tran_set 
#
#  def print_list2_tran_set(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_tran_set[i][j])
#  
#  def print_lut_tran_set(self):
#    for i in range(len(self.lut_tran_set)):
#      print(self.lut_tran_set[i])
#
#  def write_list2_tran_set(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_tran_set = []
#    self.lut_tran_set_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_tran_set.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_tran_set.append(outline)
#    ## values
#    self.lut_tran_set.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_tran_set[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_tran_set[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_tran_set[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_tran_set.append(outline)
#    self.lut_tran_set.append(");")
#    
#    # store min/center/max for doc
#    # min
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.amin(self.list2_tran_set)/targetLib.time_mag)))
#    # center
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.median(self.list2_tran_set)/targetLib.time_mag)))
#    # max
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.amax(self.list2_tran_set)/targetLib.time_mag)))
#
#  ## propagation delay table for reset
#  def set_list2_prop_reset(self, list2_prop_reset=[]):
#    self.list2_prop_reset = list2_prop_reset 
#
#  def print_list2_prop_reset(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_prop_reset[i][j])
#  
#  def print_lut_prop_reset(self):
#    for i in range(len(self.lut_prop_reset)):
#      print(self.lut_prop_reset[i])
#
#  def write_list2_prop_reset(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_prop_reset = []
#    self.lut_prop_reset_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_prop_reset.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_prop_reset.append(outline)
#    ## values
#    self.lut_prop_reset.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_prop_reset[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_prop_reset[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_prop_reset[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_prop_reset[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_prop_reset.append(outline)
#    self.lut_prop_reset.append(");")
#    
#    # store min/center/max for doc
#    # min
#    self.lut_prop_reset_mintomax.append(str("{:5f}".format(np.amin(self.list2_prop_reset)/targetLib.time_mag)))
#    # center
#    self.lut_prop_reset_mintomax.append(str("{:5f}".format(np.median(self.list2_prop_reset)/targetLib.time_mag)))
#    # max
#    self.lut_prop_reset_mintomax.append(str("{:5f}".format(np.amax(self.list2_prop_reset)/targetLib.time_mag)))
#
#  ## transient delay table for set
#  def set_list2_tran_set(self, list2_tran_set=[]):
#    self.list2_tran_set = list2_tran_set 
#
#  def print_list2_tran_set(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_tran_set[i][j])
#  
#  def print_lut_tran_set(self):
#    for i in range(len(self.lut_tran_set)):
#      print(self.lut_tran_set[i])
#
#  def write_list2_tran_set(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_tran_set = []
#    self.lut_tran_set_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_tran_set.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_tran_set.append(outline)
#    ## values
#    self.lut_tran_set.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_tran_set[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_tran_set[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_tran_set[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_tran_set.append(outline)
#    self.lut_tran_set.append(");")
#
#    # store min/center/max for doc
#    # min
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.amin(self.list2_tran_set)/targetLib.time_mag)))
#    # center
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.median(self.list2_tran_set)/targetLib.time_mag)))
#    # max
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.amax(self.list2_tran_set)/targetLib.time_mag)))
    
#  ## internal power (energy) table 
#  def set_list2_eintl(self, list2_eintl=[]):
#    self.list2_eintl = list2_eintl 
#
#  def print_list2_eintl(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_eintl[i][j])
#  
#  def print_lut_eintl(self):
#    for i in range(len(self.lut_eintl)):
#      print(self.lut_eintl[i])

#  def write_list2_eintl(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_eintl = []
#    self.lut_eintl_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_eintl.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_eintl.append(outline)
#    ## values
#    self.lut_eintl.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_eintl[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_eintl[i][j]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_eintl[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_eintl[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_eintl[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_eintl[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\" \\"
#      self.lut_eintl.append(outline)
#    self.lut_eintl.append(");")
#    
#    # store min/center/max for doc
#    # min
#    self.lut_eintl_mintomax.append(str("{:5f}".format(np.amin(self.list2_eintl)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # center
#    self.lut_eintl_mintomax.append(str("{:5f}".format(np.median(self.list2_eintl)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # max
#    self.lut_eintl_mintomax.append(str("{:5f}".format(np.amax(self.list2_eintl)*targetLib.voltage_mag/targetLib.energy_mag)))
#
#  ## propagation delay table for reset
#  def set_list2_prop_reset(self, list2_prop_reset=[]):
#    self.list2_prop_reset = list2_prop_reset 
#
#  def print_list2_prop_reset(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_prop_reset[i][j])
#  
#  def print_lut_prop_reset(self):
#    for i in range(len(self.lut_prop_reset)):
#      print(self.lut_prop_reset[i])
#
#  def write_list2_prop_reset(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_prop_reset = []
#    self.lut_prop_reset_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_prop_reset.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_prop_reset.append(outline)
#    ## values
#    self.lut_prop_reset.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_prop_reset[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_prop_reset[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_prop_reset[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_prop_reset[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_prop_reset.append(outline)
#    self.lut_prop_reset.append(");")
#
#    # store min/center/max for doc
#    # min
#    self.lut_prop_reset_mintomax.append(str("{:5f}".format(np.amin(self.list2_prop_reset)/targetLib.time_mag)))
#    # center
#    self.lut_prop_reset_mintomax.append(str("{:5f}".format(np.median(self.list2_prop_reset)/targetLib.time_mag)))
#    # max
#    self.lut_prop_reset_mintomax.append(str("{:5f}".format(np.amax(self.list2_prop_reset)/targetLib.time_mag)))
#
#    
#  ## transient delay table for reset
#  def set_list2_tran_reset(self, list2_tran_reset=[]):
#    self.list2_tran_reset = list2_tran_reset 
#
#  def print_list2_tran_reset(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_tran_reset[i][j])
#  
#  def print_lut_tran_reset(self):
#    for i in range(len(self.lut_tran_reset)):
#      print(self.lut_tran_reset[i])
#
#  def write_list2_tran_reset(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_tran_reset = []
#    self.lut_tran_reset_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_tran_reset.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_tran_reset.append(outline)
#    ## values
#    self.lut_tran_reset.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_tran_reset[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_tran_reset[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_tran_reset[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_tran_reset[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_reset[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_tran_reset.append(outline)
#    self.lut_tran_reset.append(");")
#
#    # store min/center/max for doc
#    # min
#    self.lut_tran_reset_mintomax.append(str("{:5f}".format(np.amin(self.list2_tran_reset)/targetLib.time_mag)))
#    # center
#    self.lut_tran_reset_mintomax.append(str("{:5f}".format(np.median(self.list2_tran_reset)/targetLib.time_mag)))
#    # max
#    self.lut_tran_reset_mintomax.append(str("{:5f}".format(np.amax(self.list2_tran_reset)/targetLib.time_mag)))
#    
#  ## propagation delay table for set
#  def set_list2_prop_set(self, list2_prop_set=[]):
#    self.list2_prop_set = list2_prop_set 
#
#  def print_list2_prop_set(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_prop_set[i][j])
#  
#  def print_lut_prop_set(self):
#    for i in range(len(self.lut_prop_set)):
#      print(self.lut_prop_set[i])
#
#  def write_list2_prop_set(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_prop_set = []
#    self.lut_prop_set_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_prop_set.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_prop_set.append(outline)
#    ## values
#    self.lut_prop_set.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_prop_set[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_prop_set[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_prop_set[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_prop_set[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_prop_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_prop_set.append(outline)
#    self.lut_prop_set.append(");")
#
#    # store min/center/max for doc
#    # min
#    self.lut_prop_set_mintomax.append(str("{:5f}".format(np.amin(self.list2_prop_set)/targetLib.time_mag)))
#    # center
#    self.lut_prop_set_mintomax.append(str("{:5f}".format(np.median(self.list2_prop_set)/targetLib.time_mag)))
#    # max
#    self.lut_prop_set_mintomax.append(str("{:5f}".format(np.amax(self.list2_prop_set)/targetLib.time_mag)))
#    
#  ## transient delay table for set
#  def set_list2_tran_set(self, list2_tran_set=[]):
#    self.list2_tran_set = list2_tran_set 
#
#  def print_list2_tran_set(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_tran_set[i][j])
#  
#  def print_lut_tran_set(self):
#    for i in range(len(self.lut_tran_set)):
#      print(self.lut_tran_set[i])
#
#  def write_list2_tran_set(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_tran_set = []
#    self.lut_tran_set_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_tran_set.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_tran_set.append(outline)
#    ## values
#    self.lut_tran_set.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_tran_set[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_tran_set[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_tran_set[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_tran_set[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_tran_set.append(outline)
#    self.lut_tran_set.append(");")
#    
#    # store min/center/max for doc
#    # min
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.amin(self.list2_tran_set)/targetLib.time_mag)))
#    # center
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.median(self.list2_tran_set)/targetLib.time_mag)))
#    # max
#    self.lut_tran_set_mintomax.append(str("{:5f}".format(np.amax(self.list2_tran_set)/targetLib.time_mag)))
#
#
#  ## internal power (energy) table 
#  def set_list2_eintl(self, list2_eintl=[]):
#    self.list2_eintl = list2_eintl 
#
#  def print_list2_eintl(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_eintl[i][j])
#  
#  def print_lut_eintl(self):
#    for i in range(len(self.lut_eintl)):
#      print(self.lut_eintl[i])
#
#  def write_list2_eintl(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_eintl = []
#    self.lut_eintl_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_eintl.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_eintl.append(outline)
#    ## values
#    self.lut_eintl.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_eintl[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_eintl[i][j]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_eintl[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_eintl[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_eintl[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_eintl[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\" \\"
#      self.lut_eintl.append(outline)
#    self.lut_eintl.append(");")
#    # store min/center/max for doc
#    # min
#    self.lut_eintl_mintomax.append(str("{:5f}".format(np.amin(self.list2_eintl)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # center
#    self.lut_eintl_mintomax.append(str("{:5f}".format(np.median(self.list2_eintl)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # max
#    self.lut_eintl_mintomax.append(str("{:5f}".format(np.amax(self.list2_eintl)*targetLib.voltage_mag/targetLib.energy_mag)))
#    
#  ## input energy 
#  def set_list2_ein(self, list2_ein=[]):
#    self.list2_ein = list2_ein 
#
#  def print_list2_ein(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_ein[i][j])
#  
#  def print_lut_ein(self):
#    for i in range(len(self.lut_ein)):
#      print(self.lut_ein[i])
#
#  def write_list2_ein(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_ein = []
#    self.lut_ein_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_ein.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_ein.append(outline)
#    ## values
#    self.lut_ein.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_ein[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_ein[i][j]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_ein[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_ein[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_ein[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_ein[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_ein.append(outline)
#    self.lut_ein.append(");")
#    # store min/center/max for doc
#    # min
#    self.lut_ein_mintomax.append(str("{:5f}".format(np.amin(self.list2_ein)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # center
#    self.lut_ein_mintomax.append(str("{:5f}".format(np.median(self.list2_ein)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # max
#    self.lut_ein_mintomax.append(str("{:5f}".format(np.amax(self.list2_ein)*targetLib.voltage_mag/targetLib.energy_mag)))
#
#  ## input capacitance 
#  def set_list2_cin(self, list2_cin=[]):
#    self.list2_cin = list2_cin 
#
#  def print_list2_cin(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_cin[i][j])
#  
#  def print_lut_cin(self):
#    for i in range(len(self.lut_cin)):
#      print(self.lut_cin[i])

#  def average_list2_cin(self, targetLib, ilist, jlist):
#    ## output average of input capacitance
#    ## (do not write table)
#    self.lut_cin = 0;
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        self.lut_cin += self.list2_cin[i][j]
#    #self.cin = str(self.lut_cin / (len(ilist) * len(jlist))/targetLib.capacitance_mag) ## use average
#    self.cin = str(self.lut_cin / (len(ilist) * len(jlist))) ## use average
#      
#    #print("store cin:"+str(self.cin))


  def set_average(self, name:str):
    ## output average of input capacitance
    ## (do not write table)

    mag = self.mls.capacitance_mag if name in ["cin"] else self.mls.energy_mag

    avg_list=[]
    for load in self.mlc.load:
      avg_list.append(st.mean(self.dict_list2[name][load].values()))

    self.avg[name] = st.mean(avg_list)/mag

    
#  ## clock input energy 
#  def set_list2_eclk(self, list2_eclk=[]):
#    self.list2_eclk = list2_eclk 
#
#  def print_list2_eclk(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_eclk[i][j])
#  
#  def print_lut_eclk(self):
#    for i in range(len(self.lut_eclk)):
#      print(self.lut_eclk[i])
#
#  def write_list2_eclk(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_eclk = []
#    self.lut_eclk_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_eclk.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_eclk.append(outline)
#    ## values
#    self.lut_eclk.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_eclk[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_eclk[i][j]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+", "
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_eclk[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_eclk[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_eclk[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_eclk[i][len(jlist)-1]*targetLib.voltage_mag/targetLib.energy_mag))
#        outline += tmp_line+"\", \\"
#      self.lut_eclk.append(outline)
#    self.lut_eclk.append(");")
#    # store min/center/max for doc
#    # min
#    self.lut_eclk_mintomax.append(str("{:5f}".format(np.amin(self.list2_eclk)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # center
#    self.lut_eclk_mintomax.append(str("{:5f}".format(np.median(self.list2_eclk)*targetLib.voltage_mag/targetLib.energy_mag)))
#    # max
#    self.lut_eclk_mintomax.append(str("{:5f}".format(np.amax(self.list2_eclk)*targetLib.voltage_mag/targetLib.energy_mag)))
#
#  ## clock input capacitance 
#  def set_list2_cclk(self, list2_cclk=[]):
#    self.list2_cclk = list2_cclk 
#
#  def print_list2_cclk(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_cclk[i][j])
#  
#  def print_lut_cclk(self):
#    for i in range(len(self.lut_cclk)):
#      print(self.lut_cclk[i])
#
#  def average_list2_cclk(self, targetLib, ilist, jlist):
#    ## output average of input capacitance
#    ## (do not write table)
#    self.lut_cclk = 0;
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        self.lut_cclk += self.list2_cclk[i][j]
#    #self.cclk = str(self.lut_cclk / (len(ilist) * len(jlist))/targetLib.capacitance_mag) ## use average
#    self.cclk = str(self.lut_cclk / (len(ilist) * len(jlist))) ## use average
#    #print("store cclk:"+str(self.cclk))
#
#  ## leak power
#  def set_list2_pleak(self, list2_pleak=[]):
#    self.list2_pleak = list2_pleak 
#
#  def print_list2_pleak(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_pleak[i][j])
#  
#  def print_lut_pleak(self):
#    for i in range(len(self.lut_pleak)):
#      print(self.lut_pleak[i])
#
#  def write_list2_pleak(self, targetLib, ilist, jlist):
#    ## output average of leak power
#    ## (do not write table)
#    self.lut_pleak = 0;
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        self.lut_pleak += self.list2_pleak[i][j]
#    #self.pleak = str(self.lut_pleak / (len(ilist) * len(jlist))/targetLib.leakage_power_mag) # use average
#    self.pleak = str("{:5f}".format(self.lut_pleak / (len(ilist) * len(jlist))/targetLib.leakage_power_mag)) # use average
#  
#  ## setup (for flop)
#  def set_list2_setup(self, list2_setup=[]):
#    self.list2_setup = list2_setup 
#
#  def print_list2_setup(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_setup[i][j])
#  
#  def print_lut_setup(self):
#    for i in range(len(self.lut_setup)):
#      print(self.lut_setup[i])
#
#  def write_list2_setup(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_setup = []
#    self.lut_setup_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_setup.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_setup.append(outline)
#    ## values
#    self.lut_setup.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_setup[i][j])+", "
##        targetLib.print_msg(str(i)+" "+str(j))
##        targetLib.print_msg(self.list2_setup)
##        targetLib.print_msg(str("{:5f}".format(self.list2_setup[i][j]/targetLib.time_mag)))
#        tmp_line = str("{:5f}".format(self.list2_setup[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_setup[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_setup[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_setup[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_setup[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#
#      self.lut_setup.append(outline)
#
#    self.lut_setup.append(");")
#    # store min/center/max for doc
#    # min
#    self.lut_setup_mintomax.append(str("{:5f}".format(np.amin(self.list2_setup)/targetLib.time_mag)))
#    # center
#    self.lut_setup_mintomax.append(str("{:5f}".format(np.median(self.list2_setup)/targetLib.time_mag)))
#    # max
#    self.lut_setup_mintomax.append(str("{:5f}".format(np.amax(self.list2_setup)/targetLib.time_mag)))
#
#  ## hold (for flop)
#  def set_list2_hold(self, list2_hold=[]):
#    self.list2_hold = list2_hold 
#
#  def print_list2_hold(self, ilist, jlist):
#    for i in range(len(ilist)):
#      for j in range(len(jlist)):
#        print(self.list2_hold[i][j])
#  
#  def print_lut_hold(self):
#    for i in range(len(self.lut_hold)):
#      print(self.lut_hold[i])
#
#  def write_list2_hold(self, targetLib, ilist, jlist):
#    ## index_1
#    outline = "index_1(\""
#    self.lut_hold = []
#    self.lut_hold_mintomax = []
#    for j in range(len(jlist)-1):
#      outline += str(jlist[j])+", " 
#    outline += str(jlist[len(jlist)-1])+"\");" 
#    #print(outline)
#    self.lut_hold.append(outline)
#    ## index_2
#    outline = "index_2(\""
#    for i in range(len(ilist)-1):
#      outline += str(ilist[i])+", " 
#    outline += str(ilist[len(ilist)-1])+"\");" 
#    self.lut_hold.append(outline)
#    ## values
#    self.lut_hold.append("values ( \\")
#    for i in range(len(ilist)):
#      outline = "\""
#      for j in range(len(jlist)-1):
#        #outline += str(self.list2_hold[i][j])+", "
#        tmp_line = str("{:5f}".format(self.list2_hold[i][j]/targetLib.time_mag))
#        outline += tmp_line+", "
#
#      ## do not add "," for last line
#      if(i == (len(ilist)-1)): 
#        #outline += str(self.list2_hold[i][len(jlist)-1])+"\" \\"
#        tmp_line = str("{:5f}".format(self.list2_hold[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\" \\"
#      ##  add "," for else 
#      else: 
#        #outline += str(self.list2_hold[i][len(jlist)-1])+"\", \\"
#        tmp_line = str("{:5f}".format(self.list2_hold[i][len(jlist)-1]/targetLib.time_mag))
#        outline += tmp_line+"\", \\"
#
#      self.lut_hold.append(outline)
#
#    self.lut_hold.append(");")
#
#    # store min/center/max for doc
#    # min
#    self.lut_hold_mintomax.append(str("{:5f}".format(np.amin(self.list2_hold)/targetLib.time_mag)))
#    # center
#    self.lut_hold_mintomax.append(str("{:5f}".format(np.median(self.list2_hold)/targetLib.time_mag)))
#    # max
#    self.lut_hold_mintomax.append(str("{:5f}".format(np.amax(self.list2_hold)/targetLib.time_mag)))

  #def gen_instance_for_tb(self, targetLib:Mls, targetCell:Mlc) -> str :
  def gen_instance_for_tb(self) -> str :

    # parse subckt definition
    tmp_array = self.mlc.instance.split()

    #tmp_line = tmp_array[0] # remove XDUT
    tmp_line = tmp_array.pop(0)
    cell_name = tmp_array.pop(-1); # remove cell name
    
    #targetLib.print_msg(tmp_line)
    
    for w1 in tmp_array:

      # match tmp_array and harness 
      # search target inport
      is_matched = 0
      #w2 = self.target_inport
      
      w2 = self.target_relport
      if(w1 == w2):
        tmp_line += ' IN'
        is_matched += 1
        continue
      
      # search stable inport
      for w2 in self.stable_inport:
        if(w1 == w2):
          # this is stable inport
          # search index for this port
          index_val = self.stable_inport_val[self.stable_inport.index(w2)]
          if(index_val == '1'):
            tmp_line += ' HIGH'
            is_matched += 1
          elif(index_val == '0'):
            tmp_line += ' LOW'
            is_matched += 1
          else:
            print('Illigal input value for stable input')
            my_exit()

          continue
            
      # one target outport for one simulation
      w2 = self.target_outport
      #targetLib.print_msg(w1+" "+w2+"\n")
      if(w1 == w2):
        tmp_line += ' OUT'
        is_matched += 1
        continue
        
      # search non-terget outport
      for w2 in self.nontarget_outport:
        if(w1 == w2):
          # this is non-terget outport
          # search outdex for this port
          index_val = self.nontarget_outport_val[self.nontarget_outport.index(w2)]
          tmp_line += ' WFLOAT'+str(index_val)
          is_matched += 1
          continue

      # VDD/VSS
      if(w1.upper() == self.mls.vdd_name.upper()):
          # tmp_line += ' '+w1.upper() 
          tmp_line += ' VDD' 
          is_matched += 1
          continue
        
      if(w1.upper() == self.mls.vss_name.upper()):
          # tmp_line += ' '+w1.upper() 
          tmp_line += ' VSS' 
          is_matched += 1
          continue
        
      if(w1.upper() == self.mls.pwell_name.upper()):
          # tmp_line += ' '+w1.upper() 
          tmp_line += ' VPW' 
          is_matched += 1
          continue
        
      if(w1.upper() == self.mls.nwell_name.upper()):
          # tmp_line += ' '+w1.upper() 
          tmp_line += ' VNW' 
          is_matched += 1
          continue
        
    ## show error if this port has not matched
    if(is_matched == 0):
      ## if w1 is wire name, abort
      ## check this is instance tmp_array[0] or circuit name tmp_array[-1]
      if((w1 != tmp_array[0]) and (w1 != tmp_array[-1])): 
        print("port: "+str(w1)+" has not matched in netlist parse!! " + tmp_array[0] + " or " + tmp_array[-1])
        my_exit()
          
    #tmp_line += " "+str(tmp_array[len(tmp_array)-1])+"\n" # CIRCUIT NAME
    tmp_line += " "+cell_name+"\n"

    return(tmp_line)
    
