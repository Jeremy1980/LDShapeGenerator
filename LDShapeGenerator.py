'''
Created on 12 kwi 2017

@author: Jarema Czajkowski
@license: GNU General Public License version 3
@version: 2017c
@note: A utility to help you calculate properties of 3D geometric shapes and save in LDraw format.
'''
from copy import deepcopy
import argparse
import os
import sys

__appname__ = "LDShapeGenerator"

__version__ = "2017c"
__compilation__ = "Python 2.7.11 on win32"

__appdescription__ = "Tool for geometric shape manipulation and exporting as LDraw model"

AVAILABLE_SHAPES = ['cylinder','rectangular','triangular']

PARTS = {'cylinder':'6222.dat','rectangular':'3003.dat','triangular':'30503.dat'}
PART_INLINE_TEMPLATE = "1 %(color)d %(x).1f %(y).1f %(z).1f 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 %(part)s"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__appdescription__)
    
    parser.add_argument('-v' ,'--version' ,action='version' 
                        ,version='%s %s (%s compilation)' % (__appname__ ,__version__ ,__compilation__))
    parser.add_argument('-l' ,'--shapelist' ,action='store_true'
                        ,help='Display supported geometric shapes')
    parser.add_argument('-s'  ,'--shape'
                        ,required=True
                        ,help='The chosen shape from support list.')
    parser.add_argument('-g'  ,'--geometry'
                        ,required=True
                        ,help='Individual setting for chosen shape.')
    parser.add_argument('-c' ,'--color' ,default=27 ,type=int ,metavar='INTEGER'
                        ,help='Chosen color for parts of model.')
    parser.add_argument('-q'  ,'--quiet' ,action='store_false'
                        ,help='Give less output. Do not print messages on standard output.')
    parser.add_argument('-o'  ,'--output' ,metavar='FILE'
                        ,help='The plain text file to write model.')
    
    if sys.argv.__len__() == 1:
        parser.print_help()
        sys.exit(-1)
    if sys.argv.count('--shapelist') >0 or sys.argv.count('-l') >0:
        print "\n".join(AVAILABLE_SHAPES)
        sys.exit(0)    

    args  = parser.parse_args()
        
    if not args.shape in AVAILABLE_SHAPES:
        if args.quiet:
            print "Shape **%s** in not supported yet. Select shape from list:\n%s" % (args.shape ,"\n".join(AVAILABLE_SHAPES))
        sys.exit(-1)


    vertices = []
    whl = args.geometry.split('x')   
    
    xyz = (20,24,20)
    x = xyz[0] 
    y = xyz[1] 
    z = xyz[2]

    if args.shape == 'cylinder':
        step = (24,0,0)
    elif args.shape == 'rectangular':
        step = (40,24,40)
    elif args.shape == 'triangular':
        step = (8,0,0)

    if args.shape in ['cylinder','triangular']:
        yLength= int(whl[0])
        for ny in range(yLength):
            vertices.append([x ,y ,z])   
            y += step[0]
    
    if args.shape == 'rectangular':    
        xLength= int(whl[0])
        yLength= int(whl[1])
        zLength= int(whl[2])
        
        count= 0
        for nx in range(xLength):
            for ny in range(yLength):
                vertices.append([x ,y ,z])
                
                count += 1
                z += step[2]
                    
                if count == yLength:
                    x += step[0]
                    count = 0
            
            z = xyz[2]    
        
        zv = []
        for nz in range(1,zLength):       
            for pt in vertices:
                pt2 = deepcopy(pt)
                pt2[1] += step[1] *nz
                zv.append(pt2)
            
        vertices.extend(zv)
        
    if vertices:
        fpath = os.path.abspath(args.output)
        if os.path.isabs(fpath) and not os.path.isdir(fpath):
            header = [ "0 %s" % args.shape .capitalize()
                       ,"0 Name: %s" % args.shape .capitalize()
                       ,"0 Author: %s" %__appname__
                      ]         
            with open(fpath,'w') as f:
                f.write( "\n".join(header) )
                for pt in vertices:
                    data = {'color':args.color , 'part':PARTS[args.shape] , 'x':pt[0] , 'y':pt[1] , 'z':pt[2] }
                    f.write( "\n" + PART_INLINE_TEMPLATE % data )    
                f.close()
                
            if args.quiet:
                dname = os.path.dirname(fpath)
                fname = os.path.basename(fpath)
                print "Saved {0} in {1}".format(fname ,dname)    
    elif args.quiet:
        print "Nothing to save."
        