'''
Created on 12 kwi 2017

@author: Jarema Czajkowski
@license: Eclipse Public License version 1.0
@version: 2017e
@note: A utility to help you calculate properties of 3D geometric shapes and save in LDraw format.
'''
from copy import deepcopy
import argparse
import os
import sys
import re

import math

__appname__ = "LDShapeGenerator"

__version__ = "2017e"
__compilation__ = "Python 2.7.11 on win32"

__appdescription__ = "Tool for geometric shape manipulation and exporting as LDraw model"


# These values correspond to the side length of a given element for a given coordinate axis
STEP_DICT = {
 'cylinder':(24,0,0)
 ,'hexagonal':(24,0,0)
 ,'trapezoid':(40,0,0)
 ,'rectangular':(40,24,40)
 ,'pyramid':(40,24,40)
 ,'spheroid':(20,20,8)
 ,'tent':(20,20,8)
 ,'triangular':(8,)}

AVAILABLE_KINDS = {'trapezoid':['perpendicular','oblique']
                   ,'tent':['full','none','left','right']
                   ,'sphereoid':['full','none','left','right']}

PARTS = {'spheroid':'3024.dat'
         ,'tent':'3024.dat'
         ,'cylinder':'6222.dat'
         ,'rectangular':'3003.dat'
         ,'pyramid':'3003.dat'
         ,'triangular':'30503.dat'
         ,'hexagonal':'87620.dat'
         ,'trapezoid':'3684.dat'
         ,'trapezoid_perpendicular':'3684.dat'
         ,'trapezoid_oblique':'3685.dat'}

NAMES = {'6222.dat':'Brick 4 x 4 Round with Holes'
         ,'3024.dat':'Plate 1 x 1'
         ,'3005.dat':'Brick 1 x 1'
         ,'3003.dat':'Brick 2 x 2'
         ,'30503.dat':'Plate 4 x 4 without Corner'
         ,'87620.dat':'Brick 2 x 2 Facet'
         ,'3684.dat':'Slope Brick 75 2 x 2 x 3 with Hollow Studs'
         ,'3685.dat':'Slope Brick 75 2 x 2 x 3 Double Convex'}

PART_INLINE_TEMPLATE = "1 %(color)d %(x).1f %(y).1f %(z).1f 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 %(part)s"

MIRROR_LAYOUT__TEMPLATE = ['1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 {}'
                           ,'1 {} {} {} {} 0 0 -1 0 1 0 1 0 0 {}']

PERPENDICULAR_LAYOUT_TEMPLATE = ['1 {} {} {} {} 1 0 0 0 1 0 0 0 1 {}'
                                 ,'1 {} {} {} {} 0 0 1 0 1 0 -1 0 0 {}'
                                 ,'1 {} {} {} {} 0 0 -1 0 1 0 1 0 0 {}'
                                 ,'1 {} {} {} {} -1 0 0 0 1 0 0 0 -1 {}']

TEMPLATES = {'hexagonal':PERPENDICULAR_LAYOUT_TEMPLATE
             ,'trapezoid':MIRROR_LAYOUT__TEMPLATE}


def str_to_int(s):
    return int(re.sub('[^0-9]','',s))

def insideTest(rule,x,y,z,size):
    zadd = 1.64
    # rule 0: spheroid
    if rule == 0:
        v = math.pow((x+0.5)/size[1] ,2) + math.pow((y+0.5)/size[2] ,2) + math.pow((z+zadd)/size[0] ,2)
        return v < 1.0
    # rule 8: tent 
    elif rule == 8:
        v = math.pow((x+0.5)/size[1] ,2) + math.pow((y+0.5)/size[2] ,2)
        return v < math.pow(1.0 - math.sqrt( (z+zadd)/size[0]) ,2)
    return False
    
def print_shapes():
    for key in sorted(PARTS.keys()):
        if key.find('_') == -1: print key.capitalize()    

def rectangular(size, pt):
    xLength= size[0]
    yLength= size[1]
    zLength= size[2]
    
    x = pt[0] 
    y = pt[1] 
    z = pt[2]    
    
    count = 0
    result = []
    for nx in range(xLength):
        for ny in range(yLength):
            result.append([x ,y ,z])
            
            count += 1
            z += STEP[2]
            if count == yLength:
                x += STEP[0]
                count = 0
        z = pt[2]    
    
    zv = []
    for nz in range(1,zLength):       
        for pt in result:
            pt2 = deepcopy(pt)
            pt2[1] += STEP[1] *nz
            zv.append(pt2)
       
    result.extend(zv) 
    return result

 
'''
 @attention:  Based on Lego Spheroid Generator by Erik Olson
              This program generates 1/4 of a dome or other shape
 @see:  http://olson.pair.com/moc/spheroid/
'''     
def spheroid(rule ,size):
    steps = {}
    
    for z in range(size[0]):
        steps[z] = {}
        for y in range(size[2]):
            steps[z][y] = {}
            for x in range(size[1]):
                steps[z][y][x] = 0   
                if insideTest(rule ,x ,y ,z ,size): 
                    steps[z][y][x] = 1   
        
    for z in range(size[0]):
        for y in range(size[2]):
            for x in range(size[1]):
                if steps[z][y][x]:
                    # RIGHT TOP
                    if args.kind[0] in ['full','right']:
                        VERTICES.append([ x*STEP[0] ,-z*STEP[2] ,y*STEP[1] ])
                    # LEFT TOP
                    if args.kind[0] in ['full','left']:
                        VERTICES.append([ -x*STEP[0] ,-z*STEP[2] ,y*STEP[1] ])
                         
    for z in range(size[0]):
        for y in range(size[2]):
            for x in range(size[1]):
                if steps[z][y][x]:
                    # RIGHT BOTTOM
                    if args.kind[1] in ['full','right']:
                        VERTICES.append([ x*STEP[0] ,z*STEP[2] ,y*STEP[1] ])
                    # LEFT BOTTOM
                    if args.kind[1] in ['full','left']:
                        VERTICES.append([ -x*STEP[0] ,z*STEP[2] ,y*STEP[1] ])
                    
                    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__appdescription__)
    
    arggroup = parser.add_argument_group("required")
    arggroup.add_argument('-s'  ,'--shape' ,required=True
                        ,help='The chosen shape from support list.')
    arggroup.add_argument('-g'  ,'--geometry' ,required=True
                        ,help='Individual setting for chosen shape.')
    
    parser.add_argument('-v' ,'--version' ,action='version' 
                        ,version='%s %s (%s compilation)' % (__appname__ ,__version__ ,__compilation__))
    parser.add_argument('--shapelist' ,action='store_true'
                        ,help='Display supported geometric shapes and exit')
    parser.add_argument('--kindlist' ,action='store_true'
                        ,help='Display supported variation of given geometric shape and exit.')
    parser.add_argument('-c' ,'--color' ,default=27 ,type=int ,metavar='INTEGER'
                        ,help='Chosen color for parts of model.')
    parser.add_argument('-q'  ,'--quiet' ,action='store_false'
                        ,help='Give less output. Print less that more messages on standard output.')
    parser.add_argument('-o'  ,'--output' ,metavar='FILE'
                        ,help='The plain text file to write model.')
    
    arggroup = parser.add_argument_group("additional")
    arggroup.add_argument('--kind' ,nargs=2  
                        ,help='Selected variation of given geometric shape.')
    arggroup.add_argument('--calculation' 
                        ,help='Make mathematical operation.')
    
    if sys.argv.__len__() == 1:
        parser.print_help()
        sys.exit(-1)
    elif sys.argv.count('--shapelist') >0:
        print_shapes()
        sys.exit(0)    
    elif sys.argv.count('--kindlist') >0:
        for shape, kind in AVAILABLE_KINDS.items():
            print shape.upper()
            print "\t" , "\n\t".join(kind)
        sys.exit(0)    

    args = parser.parse_args()
    
    args.shape = args.shape.lower()
    args.geometry = args.geometry.lower()
        
    if not args.shape in PARTS:
        if args.quiet:
            print "Shape **%s** in not supported yet. For more details use --help argument." % args.shape
            print "Select now shape from list:"
            print_shapes()
        sys.exit(-1)
        
    if args.shape in ['spheroid','tent'] and not args.kind:
        args.kind = ['full','full']
    
    xyz = [20,24,20]
    whl = []   
    STEP = STEP_DICT[args.shape]
    VERTICES = []
    for val in args.geometry.split('x'):
        whl.append(str_to_int(val))

    try:
        collect_data = False
        rotation_axis= 1
    
        if args.shape == 'spheroid':
            spheroid(0 ,whl)
    
        elif args.shape == 'tent':
            spheroid(8 ,whl)
    
        if args.shape == 'trapezoid':
            coord = [[50.0 ,-72.0 ,-20.0] ,[70.0 ,-72.0 ,-20.0]]
            collect_data = True
            rotation_axis= 2
            
        elif args.shape == 'hexagonal':
            coord = [[-60.0 ,-24.0 ,-100.0] ,[-100.0 ,-24.0 ,-100.0] 
                     ,[-60.0 ,-24.0 ,-60.0] ,[-100.0 ,-24.0 ,-60.0]]
            collect_data = True
            rotation_axis= 1
            
        if collect_data:
            stop = whl[0]
            for ny in range(stop):
                ringcoord = deepcopy(coord)
                for pt in ringcoord:
                    pt[rotation_axis] +=STEP[0] *ny
                VERTICES.append(ringcoord)
    
        if args.shape in ['cylinder','triangular']:
            yLength= whl[0]
            x = xyz[0] 
            y = xyz[1] 
            z = xyz[2]
            for ny in range(yLength):
                VERTICES.append([x ,y ,z])   
                y += STEP[0]        
    
    
        if args.shape == 'pyramid':
            xyzLength = whl[0]
            if xyzLength % 2:
                xyzLength += 1
            whl = [xyzLength,xyzLength,1]
            
            origin = deepcopy(xyz)
            for m in range(xyzLength):
                origin[0] += STEP[0]
                origin[1] -= STEP[1]
                origin[2] += STEP[2]
                whl[1] -= 2
                whl[0] -= 2
                VERTICES.extend(rectangular(whl ,origin))
                
        elif args.shape == 'rectangular':    
            VERTICES.extend(rectangular(whl ,xyz))
    except Exception as error:
        if args.quiet:
            print error.__class__.__name__ ,':', error.message
        sys.exit(-1)
        
    try:
        if args.calculation:
            print  "{}pcs of {} /{}/" .format( VERTICES.__len__() ,NAMES[PARTS[args.shape]], PARTS[args.shape] )
    except Exception as error:
        if args.quiet:
            print error.__class__.__name__ ,':', error.message 
        
    try:
        if VERTICES:
            fpath = os.path.abspath(args.output)
            if os.path.isabs(fpath) and not os.path.isdir(fpath):
                header = [ "0 %s %s" % (args.shape .capitalize() ,args.geometry if args.shape == 'rectangular' else "")
                           ,"0 Name: %s" % os.path.normcase(os.path.basename(fpath))
                           ,"0 Author: %s" %__appname__
                          ]         
                with open(fpath,'w') as f:
                    f.write( "\n".join(header) )
                    if args.shape in TEMPLATES:
                        nv = VERTICES.__len__()-1
                        for n,coord in enumerate(VERTICES):
                            color =  args.color
                            part = PARTS[args.shape] 
                            template = deepcopy(TEMPLATES[args.shape])
                            if args.kind:
                                left = args.kind[0]
                                right= args.kind[1]
                                if args.shape == 'trapezoid':
                                    if n == 0 and left == 'oblique':
                                        coord[0][2] += 10
                                        coord[1][2] += 10
                                        part = PARTS["%s_%s" % (args.shape,left)]
                                        template = [PERPENDICULAR_LAYOUT_TEMPLATE[1]
                                                    ,PERPENDICULAR_LAYOUT_TEMPLATE[0]]
                                        
                                    if n == nv and right == 'oblique':
                                        coord[0][2] -= 10
                                        coord[1][2] -= 10
                                        part = PARTS["%s_%s" % (args.shape,right)]
                                        template = [PERPENDICULAR_LAYOUT_TEMPLATE[3]
                                                    ,PERPENDICULAR_LAYOUT_TEMPLATE[2]]
                                    
                            f.write( "\n0 STEP" )
                            for m,line in enumerate(template):
                                data = deepcopy(coord[m])
                                data.insert(0 ,color)
                                data.append(part)
                                f.write( "\n" + line.format(*data) )                
                    else:
                        prevY = 0
                        for n,pt in enumerate(VERTICES):
                            color =  args.color
                            data = {'color':color ,'part':PARTS[args.shape] , 'x':pt[0] , 'y':pt[1] , 'z':pt[2] }
                            if prevY <> pt[1]:
                                prevY = pt[1]
                                f.write( "\n0 STEP" )
                            f.write( "\n" + PART_INLINE_TEMPLATE % data )    
                    f.close()
                    
                if args.quiet:
                    dname = os.path.dirname(fpath)
                    fname = os.path.basename(fpath)
                    print "Saved {0} in {1}".format(fname ,dname)    
        elif args.quiet:
            print "Nothing to save."
    except Exception as error:
        if error.__class__ == IOError:
            error.message = fpath
        print error.__class__.__name__ ,':', error.message.capitalize()
        