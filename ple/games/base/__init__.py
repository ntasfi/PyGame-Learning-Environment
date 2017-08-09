from .pygamewrapper import PyGameWrapper
try:
    from .doomwrapper import DoomWrapper
except:
    print("couldn't import doomish")
