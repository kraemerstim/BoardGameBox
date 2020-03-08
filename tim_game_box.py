 #! /usr/bin/env python
'''
Generates Inkscape SVG file containing box components needed to 
laser cut a tabbed construction box taking kerf into account

Copyright (C) 2018 Thore Mehr thore.mehr@gmail.com
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
__version__ = "1.0" ### please report bugs, suggestions etc to bugs@twot.eu ###

import math,inkex,simplestyle

def draw_SVG_String(size,color,parent,kerf,position=(0,0),text='', labels=False):# Adding an SVG_String to the drawing
  transform='translate('+str(position[0])+','+str(position[1])+')'
  group = {inkex.addNS('label', 'inkscape'):text, 'transform':transform}
  parent = inkex.etree.SubElement(parent, inkex.addNS('g'), group)

  SVG_String='M 0 0 h ' + str(size[0] + kerf) + ' v ' + str(size[1] + kerf) + ' h ' + str(-size[0]-kerf) + 'z'
  name='part'
  style = { 'stroke': color[0], 'fill': 'none','stroke-width':str(max(kerf,0.2))}
  drw = {'style':simplestyle.formatStyle(style), inkex.addNS('label','inkscape'):name,'d':SVG_String}
  inkex.etree.SubElement(parent, inkex.addNS('path','svg'), drw )
  if labels and len(text) > 0:
    style = { 'text-anchor': 'middle', 'font-size':'2px', 'fill': color[1]}
    text_element = {'style':simplestyle.formatStyle(style), 'class': 'label', 'x':str(size[0]/2), 'y':str(size[1]/2)}
    svg_text = inkex.etree.SubElement(parent, inkex.addNS('text','svg'), text_element)
    svg_text.text = text

class tim_box_maker(inkex.Effect):
  def __init__(self):
      # Call the base class constructor.
      inkex.Effect.__init__(self)

      # Define options
      self.OptionParser.add_option('--page',action='store',type='string',dest='page',default='page_1')
      self.OptionParser.add_option('--unit',action='store',type='string',dest='unit',default='mm')

      self.OptionParser.add_option('--inner_height',action='store',type='float',dest='inner_height',default='0.0')
      self.OptionParser.add_option('--inner_width',action='store',type='float',dest='inner_width',default='0.0')
      self.OptionParser.add_option('--inner_depth',action='store',type='float',dest='inner_depth',default='0.0')

      self.OptionParser.add_option('--cut_percentage',action='store',type='int',dest='cut_percentage',default='50')
      self.OptionParser.add_option('--inner_compartment_overlap',action='store',type='float',dest='inner_compartment_overlap',default='20.0')

      self.OptionParser.add_option('--tab_mode',action='store',type='string',dest='tab_mode',default='number')
      self.OptionParser.add_option('--tab_size',action='store',type='float',dest='tab_size',default='0.0')
      self.OptionParser.add_option('--wrapper_size',action='store',type='float',dest='wrapper_size',default='0.5')
    
      self.OptionParser.add_option('--thickness',action='store',type='float',dest='thickness',default=4,help='Thickness of Material')
      self.OptionParser.add_option('--kerf',action='store',type='float',dest='kerf',default=0.2)
      self.OptionParser.add_option('--spaceing',action='store',type='float',dest='spaceing',default=1)

      self.OptionParser.add_option('--labels',action='store',type='inkbool',dest='labels',default=True)

  def effect(self):
    thickness=self.unittouu(str(self.options.thickness)+self.options.unit)
    kerf=self.unittouu(str(self.options.kerf)+self.options.unit)/2 #kerf is diameter in UI and radius in lib
    spaceing=self.unittouu(str(self.options.spaceing)+self.options.unit)

    inner_height=self.unittouu(str(self.options.inner_height)+self.options.unit)
    inner_width=self.unittouu(str(self.options.inner_width)+self.options.unit)
    inner_depth=self.unittouu(str(self.options.inner_depth)+self.options.unit)

    inner_compartment_overlap=self.unittouu(str(self.options.inner_compartment_overlap)+self.options.unit)
    wrapper_size=self.unittouu(str(self.options.wrapper_size)+self.options.unit)

    labels=self.options.labels

    bottom_height = (float(self.options.cut_percentage) / 100) * inner_height 
    top_height = inner_height - bottom_height
    insert_height = bottom_height + inner_compartment_overlap

    position = [0,0]
    ##Insert
    #Sides inner_depth x insert_height
    size = [inner_depth, insert_height]
    draw_SVG_String(size, ["#000000", "#ff0000"] , self.current_layer, kerf, position, 'Insert Left', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Insert Right', labels)
    position = [position[0] + size[0] + spaceing, 0]

    #Front/Back (inner_width+thickness*2) x insert_height
    size = [inner_width+thickness*2, insert_height]
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Insert Front', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Insert Back', labels)
    position = [position[0] + size[0] + spaceing, 0]

    ##Top + Bottom Plate
    #Plate (inner_width+thickness*4+wrapper_size*2) x (inner_depth+thickness*4+wrapper_size*2)
    size = [inner_width+thickness*4+wrapper_size*2, inner_depth+thickness*4+wrapper_size*2]
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Top Plate', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Bottom Plate', labels)
    position = [position[0] + size[0] + spaceing, 0]

    ##Bottom
    #Sides (inner_depth+thickness*2+wrapper_size*2) x bottom_height
    size = [inner_depth+thickness*2+wrapper_size*2, bottom_height]
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Bottom Left', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Bottom Right', labels)
    position = [position[0] + size[0] + spaceing, 0]

    #front/back (inner_width+thickness*4+wrapper_size*2) x bottom_height
    size = [inner_width+thickness*4+wrapper_size*2, bottom_height]
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Bottom Front', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Bottom Back', labels)
    position = [position[0] + size[0] + spaceing, 0]

    ##Top
    #Sides (inner_depth+thickness*2+wrapper_size*2) x top_height
    size = [inner_depth+thickness*2+wrapper_size*2, top_height]
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Top Left', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Top Right', labels)
    position = [position[0] + size[0] + spaceing, 0]

    #front/back (inner_width+thickness*4+wrapper_size*2) x top_height
    size = [inner_width+thickness*4+wrapper_size*2, top_height]
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Top Front', labels)
    position[1] = size[1] + spaceing
    draw_SVG_String(size, ["#000000", "#ff0000"], self.current_layer, kerf, position, 'Top Back', labels)
    position = [position[0] + size[0] + spaceing, 0]
    
effect = tim_box_maker()
effect.affect()