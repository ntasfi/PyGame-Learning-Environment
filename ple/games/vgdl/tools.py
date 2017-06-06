'''
Video game description language -- utility functions.

@author: Tom Schaul
'''

from math import sqrt
import pygame


def logToFile(string):
    f = open("log.txt", "a")
    f.write(string +"\n")
    f.close()
    pass

def vectNorm(v):
    return sqrt(float(v[0])**2+v[1]**2)

def unitVector(v):
    l = vectNorm(v)
    if l > 0:
        return (v[0]/l, v[1]/l)
    else:
        return (1, 0)
    
def oncePerStep(sprite, game, name):
    """ Utility for guaranteeing that an event gets triggered only once per time-step on each sprite. """
    name = "_"+name
    if hasattr(sprite, name):
        # bounce only once per timestep, even if there are multiple collisions
        if sprite.__dict__[name] == game.time:
            return False
    sprite.__dict__[name] = game.time
    return True
    
def triPoints(rect, orientation):
    """ Returns the pointlist for a triangle 
    in the middle of the provided rect, pointing in the orientation (given as angle from upwards,
    or orientation vector) """    
    p1 = (rect.center[0]+orientation[0]*rect.size[0]/3.,
          rect.center[1]+orientation[1]*rect.size[1]/3.)
    p2 = (rect.center[0]-orientation[0]*rect.size[0]/4.,
          rect.center[1]-orientation[1]*rect.size[1]/4.)
    orthdir = (orientation[1], -orientation[0])
    p2a = (p2[0]-orthdir[0]*rect.size[0]/6.,
           p2[1]-orthdir[1]*rect.size[1]/6.)
    p2b = (p2[0]+orthdir[0]*rect.size[0]/6.,
           p2[1]+orthdir[1]*rect.size[1]/6.)    
    return [(p[0], p[1]) for p in [p1, p2a, p2b]]

def roundedPoints(rect):    
    from ontology import BASEDIRS
    size = rect.size[0]
    assert rect.size[1]==size, "Assumes square shape."
    size = size*0.92
    res = []
    for d0, d1 in BASEDIRS:
        res += [(d0*size/32*15-(d1)*7*size/16, d1*size/32*15+(d0)*7*size/16),
                (d0*size/2-(d1)*3*size/8, d1*size/2+(d0)*3*size/8),
                (d0*size/2+(d1)*3*size/8, d1*size/2-(d0)*3*size/8),
                (d0*size/32*15+(d1)*7*size/16, d1*size/32*15-(d0)*7*size/16),
                ]    
    return [(p[0]+rect.center[0], p[1]+rect.center[1]) for p in res]

def squarePoints(center, size):
    return [(center[0]+size/2, center[1]+size/2),
            (center[0]+size/2, center[1]-size/2),
            (center[0]-size/2, center[1]-size/2),
            (center[0]-size/2, center[1]+size/2)]
    

class Node(object):
    """ Lightweight indented tree structure, with automatic insertion at the right spot. """
    
    parent = None
    def __init__(self, content, indent, parent=None):
        self.children = []
        self.content = content
        self.indent = indent
        if parent:
            parent.insert(self)
        else:
            self.parent = None
    
    def insert(self, node):
        if self.indent < node.indent:
            if len(self.children) > 0:
                assert self.children[0].indent == node.indent, 'children indentations must match'
            self.children.append(node)
            node.parent = self
        else:
            assert self.parent, 'Root node too indented?'
            self.parent.insert(node)

    def __repr__(self):
        if len(self.children) == 0:
            return self.content
        else:
            return self.content+str(self.children)
                        
    def getRoot(self):
        if self.parent: return self.parent.getRoot()
        else:           return self


def indentTreeParser(s, tabsize=8):
    """ Produce an unordered tree from an indented string. """
    # insensitive to tabs, parentheses, commas
    s = s.expandtabs(tabsize)
    s.replace('(', ' ')
    s.replace(')', ' ')
    s.replace(',', ' ')
    lines = s.split("\n")            
                     
    last = Node("",-1)
    for l in lines:
        # remove comments starting with "#"
        if '#' in l:
            l = l.split('#')[0]
        # handle whitespace and indentation
        content = l.strip()
        if len(content) > 0:
            indent = len(l)-len(l.lstrip())
            last = Node(content, indent, last)
    return last.getRoot()

def listRotate(l, n):
    return l[n:] + l[:n]
    
    
def makeGifVideo(env, actions, initstate=None, prefix='seq_', duration=0.1,
                 outdir='../gifs/', tmpdir='../temp/'):
    """ Generate an animated gif from a sequence of actions. """
    from external_libs.images2gif import writeGif
    import Image
    env.visualize = True
    env.reset()
    if initstate is not None:
        env.setState(initstate)
    env._counter = 1
    res_images = []
    astring = ''.join([str(a) for a in actions if a is not None])
    
    def cb(*_):
        fn = tmpdir + "tmp%05d.png" % env._counter
        pygame.image.save(env._game.screen, fn)
        res_images.append(Image.open(fn))
        env._counter += 1
        
    env.rollOut(actions, callback=cb)
    writeGif(outdir + prefix + '%s.gif' % astring, res_images, duration=duration, dither=0)
 
    
