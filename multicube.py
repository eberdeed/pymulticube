#!/usr/bin/python3
"""
**********************************************************
* MultiCube:  A class to create random cubes in an OpenGL
* sky box.  It uses numpy arrays and GLM for the transformations.  
* It will respond to keyboard and mouse inputs.
* Created by: Edward Charles Eberle <eberdeed@eberdeed.net>
* May 2020 San Diego, California USA
* ********************************************************
"""
import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from sfml import sf
from sfml.window import VideoMode
from numpy import array, zeros
from pymulticube.camera import Camera
from pymulticube.cubemaker import CubeMaker
from pymulticube.createimage import CreateImage
from glm import *
import sys
from math import fmod
from multiprocessing import Process
from random import randint
from random import random

class PosOrient:
    """
    A class to define the positon and orientation of a cube.
    The first two elements of the angles array are the 
    current angle values and the last two are the increments
    on the xaxis and yaxis rotations.
    """
    locon = vec3(0.)
    indices = zeros((6), 'i')
    angles = zeros((4), 'f')
    xaxis = vec3(0.)
    yaxis = vec3(0.)
    
    def repr(self):
        """
        Display the contents of the PosOrient class.
        """
        print("\n\tLocation: ", self.locon.x, ",", 
        self.locon.y, ",", self.locon.z, ".")
        print("\n\tImage Indices: ", end="")
        for y in self.indices:
            print(y, end=", ")
        print("\n\tAngles: ", self.angles[2], ",", self.angles[3])
        print("\n\tX Axis: ", self.xaxis.x, ",",
        self.xaxis.y, ",", self.xaxis.z)
        print("\n\tY Axis: ", self.yaxis.x, ",",
        self.yaxis.y, ",", self.yaxis.z, ".")


class MultiCube:
    """
    MultiCube:  A class to create random cubes in an OpenGL
    sky box.  It uses numpy arrays and GLM for the transformations.  
    It will respond to keyboard and mouse inputs.
    """
    Width = 800
    # Starting width for the display screen.
    Height = 600
    # Starting height for the display screen.
    width = Width
    # Current screen width.
    height = Height
    # Current screen height.
    cube = None
    # The cube vertex and texture array.
    skyboxverts = None
    # The sky box vertex array.
    clock = None
    # The SFML clock for timing.
    textureID1 = 0
    # The current texture buffer id.
    textureID = list()
    # The complete list of texture buffer ids.
    skyboxID = 0
    # The skybox texture buffer id.
    debug1 = False
    # The debug flag.
    firstMouse = True
    # The flag to signal the first time reading the mouse position.
    sndthrd = None
    # The sound thread.
    fullScreen = True
    # A full screen flag.
    modes = None
    # A video modes list.
    windowID = None
    # A window ID.
    image = None
    # An image creation class.
    timestart = 0
    # The start time of one eventLoop iteration.
    timeend = 0
    # The end time of one eventLoop iteration.
    mousePos1 = vec2()
    # The recorded mouse position.
    mousePos2 = vec2()
    # The previosly recorded mouse position.
    arraysize = 0
    # The size of the image list minus one to 
    # account for the first image being a background 
    # for the rest.
    distVals = list()
    # The list of cube location and orientation values.
    soundFile = "/usr/share/openglresources/sounds/celticfive.wav"
    # The Sound file.
    # The list of file location for cube images.
    boximages = ([
        "/usr/share/openglresources/images/planks.jpg",
        "/usr/share/openglresources/images/abstract.png",
        "/usr/share/openglresources/images/awesomeface.png",
        "/usr/share/openglresources/images/eucharist.png",
        "/usr/share/openglresources/images/grapes.png",
        "/usr/share/openglresources/images/lemon.png",
        "/usr/share/openglresources/images/mexican.png",
        "/usr/share/openglresources/images/palette.png",
        "/usr/share/openglresources/images/panda.png",
        "/usr/share/openglresources/images/paris.png",
        "/usr/share/openglresources/images/seahorse.png",
        "/usr/share/openglresources/images/sparkle.png",
        "/usr/share/openglresources/images/star.png",
        "/usr/share/openglresources/images/suites.png",
        "/usr/share/openglresources/images/sunflowers.png",
        "/usr/share/openglresources/images/sun.png",
        "/usr/share/openglresources/images/superman.png"
    ])
    # The list of file locations for sky box images.
    skyfiles = ([
        "/usr/share/openglresources/images/skybox/scene_right.tga",
        "/usr/share/openglresources/images/skybox/scene_left.tga",
        "/usr/share/openglresources/images/skybox/scene_up.tga",
        "/usr/share/openglresources/images/skybox/scene_down.tga",
        "/usr/share/openglresources/images/skybox/scene_front.tga",
        "/usr/share/openglresources/images/skybox/scene_back.tga"
    ])
    
    def __init__(self):
        """
        Initialize the GLUT windowing system and start the sound using the SFML library.
        """
        glutInit(sys.argv)
        self.arraysize = 2 * (len(self.boximages)  - 1)
        self.permLoc()
        self.camera = Camera(self.Width, self.Height, vec3(0.0, 0.0, 20.0), vec3(0.0, 0.0, 0.0))
        # create the main window
        self.modes = VideoMode.get_fullscreen_modes()
        if (self.debug1):
            print("Mode 0 dimensions: ", self.modes[0].width, ", ", self.modes[0].height)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_ALPHA)
        glutInitWindowSize(self.width, self.height) 
        glutInitWindowPosition(int((self.modes[0].width / 2) - (self.width / 2)), int((self.modes[0].height / 2) - (self.height / 2))) 
        self.windowID = glutCreateWindow("Python Glut OpenGL Demo")
        if (self.debug1):
            print("\n\tWindow width:  ", glutGet(GLUT_WINDOW_WIDTH), "  Window height:  ", 
        glutGet(GLUT_WINDOW_HEIGHT), ".")
        soundinfo = "sound thread"
        self.sndthrd = Process(target=self.soundMaker, args=(soundinfo,))
        self.sndthrd.start()
        self.initProg()
    
    def initProg(self):
        """
        Initialize OpenGL create the cube and sky cube and 
        initialize the positions and orientations for the cubes.
        """
        # enable Z-buffer read and write
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        cuby = CubeMaker()
        self.cube = cuby.createCube(True, False)
        self.skyboxverts = cuby.createCube(False, False)
        self.skyboxverts *= 2000.0
        if (self.debug1):
            print("\n\tType for sky box:  ", type(self.skyboxverts), ".")
            self.printCube(self.skyboxverts)
            print("\n\tType for cube:  ", type(self.cube), ".")
            self.printCube(self.cube)
        # Create a clock for timing events.
        self.clock = sf.Clock()
        self.image = CreateImage()
        self.textureID = self.image.doubleImage(self.boximages, 0)
        if (self.debug1):
            for x in range(len(self.textureID)):
                print("\n\tTexture ", x, " with ID ", self.textureID[x], 
                " from file ", self.boximages[x])
        self.skyboxID = self.image.createSkyBoxTex(self.skyfiles, len(self.textureID))
        glDepthRange(0.1, 200.0)
        
    def eventLoop(self):
        """
        The display and animation of the cubes is handled here.
        """
        self.timestart = self.clock.elapsed_time.seconds
        
        # clear the depth buffer
        glClearColor(0.0, 0.0, 0.0, 1.0);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        

        # this is useless here because we have only one window which is
        # always the active one, but don't forget it if you use multiple self.windows
        self.framebufferSize(self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.camera.setGluPerspective()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.camera.setGluViewMatrix()
        position = self.camera.getPosition()
        (pitch, yaw) = self.camera.getPitchYaw()
        if (self.debug1):
            print("\n\tPosition: ", position.x, ",", position.y, ",", position.z, "  Yaw: ", yaw,
            "  Front: ", self.camera.Front.x, ",", self.camera.Front.y, ",", self.camera.Front.z)
        # draw a skybox
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skyboxID)
        glEnable(GL_TEXTURE_CUBE_MAP)
        glBegin(GL_TRIANGLES)
        for z in range(36):
            glTexCoord3f(self.skyboxverts[z][0], self.skyboxverts[z][1], self.skyboxverts[z][2])
            glVertex3f(self.skyboxverts[z][0], self.skyboxverts[z][1], self.skyboxverts[z][2])
        glEnd()
        glDisable(GL_TEXTURE_CUBE_MAP)
        # draw a cube
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        for x in range(2):
            for y in range(0, len(self.boximages) - 1):
                # apply some transformations
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                glRotatef(yaw, 0.0, 1.0, 0.0)
                glRotatef(-pitch, 1.0, 0.0, 0.0)
                index = (x * (len(self.boximages) - 1))  + y
                glTranslate(self.distVals[index].locon.x - position.x, 
                self.distVals[index].locon.y - position.y,
                self.distVals[index].locon.z - position.z)
                glRotatef(self.distVals[index].angles[0], self.distVals[index].xaxis.x,
                self.distVals[index].xaxis.y, self.distVals[index].xaxis.z)
                glRotatef(self.distVals[index].angles[1], self.distVals[index].yaxis.x,
                self.distVals[index].yaxis.y, self.distVals[index].yaxis.z)
                for z in range(6):
                    self.textureID1 = self.textureID[self.distVals[index].indices[z]]
                    if (self.debug1):
                        print("\n\tTexture ", index, " with ID ", self.textureID1, ".")
                    glBindTexture(GL_TEXTURE_2D, self.textureID1)
                    glEnable(GL_TEXTURE_2D)
                    glBegin(GL_TRIANGLES)
                    for w in range(6):
                        if (self.debug1):
                            print("\n\tw", w, " z ", z, " y ", y, " x ", x)
                        glTexCoord2d(self.cube[(z * 6) + w][3], self.cube[(z * 6) + w][4])
                        glVertex3f(self.cube[(z * 6) + w][0], self.cube[(z * 6) + w][1], self.cube[(z * 6) + w][2])
                    glEnd()
                    self.distVals[index].angles[0] += self.distVals[index].angles[2]
                    self.distVals[index].angles[1] += self.distVals[index].angles[3]
                    self.distVals[index].angles[0] = fmod(self.distVals[index].angles[0], 360.0)
                    self.distVals[index].angles[1] = fmod(self.distVals[index].angles[1], 360.0)
                    glDisable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW);
        self.timeend = self.clock.elapsed_time.seconds
        glutSwapBuffers();
        
    def printCube(self, cube):
        """
        A debug method to print a cube.
        """
        shape = cube.shape
        print(shape)
        print("\nValues for a cube:", end="\n\t")
        for x in range(0, 36):
            for y in range(0, shape[1]):
                print(cube[x][y], end=", ")
            if (((x + 1) % 6) == 0):
                print(" of array type:  ", type(cube[x]), " of element type:  ", type(cube[x][y]), end="\n\t")
            else:
                print(" of array type:  ", type(cube[x]), " of element type:  ", type(cube[x][y]), end="\n\t")
        print("\n")

    #---------------------------------------------------------------------------------------------------------
    def keyDown(self, key, x, y):
        """
        Handle keyboard inputs.
        """
        mods = glutGetModifiers()
        keyval = ord(key)
        s = self.modes[0]
        # Use timing to create a cameraSpeed variable.
        delta = self.timeend - self.timestart
        cameraSpeed = 25.0 * delta
        if (self.debug1):
            print("\n\tdelta:  ", delta, " cameraSpeed:  ", cameraSpeed, ".")
        if (keyval == 0x001B):
            glutDestroyWindow(self.windowID);
            self.sndthrd.terminate()
        # Motion keys.
        # Forward motion.
        elif ((keyval == 0x77) or (keyval == 0x57)):
            self.camera.processKeyboard(Camera.Camera_Movement.index("FORWARD"), cameraSpeed)
        # Backwards motion.
        elif ((keyval == 0x73) or (keyval == 0x53)):
            self.camera.processKeyboard(Camera.Camera_Movement.index("BACKWARD"), cameraSpeed)
        # Move left.
        elif ((keyval == 0x61) or (keyval == 0x41)):
            self.camera.processKeyboard(Camera.Camera_Movement.index("LEFT"), cameraSpeed)
        # Move right.
        elif ((keyval == 0x44) or (keyval == 0x64)):
            self.camera.processKeyboard(Camera.Camera_Movement.index("RIGHT"), cameraSpeed)
        # Move up.
        elif ((keyval == 0x72) or (keyval == 0x52)):
            self.camera.processKeyboard(Camera.Camera_Movement.index("UP"), cameraSpeed)
        # Move down.
        elif ((keyval == 0x46) or (keyval == 0x66)):
            self.camera.processKeyboard(Camera.Camera_Movement.index("DOWN"), cameraSpeed)
        # Reset the self.camera.
        elif ((keyval == 0x7A) or (keyval == 0x5A)):
            self.camera.resetCamera()
        # Reverse the self.camera.
        elif ((keyval == 0x78) or (keyval == 0x58)):
            self.camera.reverseDirection()
        elif (keyval == 0x000D):
            if (mods == GLUT_ACTIVE_ALT):
                if (self.fullScreen):
                    glutFullScreen();
                    self.framebufferSize(s.width, s.height)
                else:
                    glutReshapeWindow(self.Width, self.Height);
                    glutPositionWindow(int((s.width / 2) - (self.Width / 2)), int((s.height / 2) - (self.Height / 2))); 
                    windowEvent(self.Width, self.Height);
            self.fullScreen = not self.fullScreen
    
    def funcKeyDown(self, key, x, y):
        """ 
        Handle non-ascii2 keys.
        """
        # Zoom keys.
        # Zoom in.
        if (key == GLUT_KEY_UP):
            self.camera.processMouseScroll(Camera.Camera_Movement.index("CLOSER"))
        # Zoom out.
        elif (key == GLUT_KEY_DOWN):
            self.camera.processMouseScroll(Camera.Camera_Movement.index("AWAY"))
        
        
    def mouseMove(self, x, y):
        """  
        Handle mouse motion.
        """
        if (self.firstMouse):
            self.mousePos2.x = x
            self.mousePos2.y = y
            self.firstMouse = False;

        self.mousePos1.x = x
        self.mousePos1.y = y

        if (self.debug1):
            print("\n\tIn mouseMove() Mouse X, Y:  ", self.mousePos1.x, ", ", self.mousePos1.y, 
            " Old Mouse: ", self.mousePos2.x, ", ", self.mousePos2.y, " differences ",
            self.mousePos1.x - self.mousePos2.x, ", ", self.mousePos1.y - self.mousePos2.y, ".")
 
        self.camera.processMouseMovement(self.mousePos1.x - self.mousePos2.x, self.mousePos1.y - self.mousePos2.y)
        self.mousePos2.x = x
        self.mousePos2.y = y
        
    # Whenever the window size changed (by OS or user resize) this callback function executes
    # ---------------------------------------------------------------------------------------------
    def framebufferSize(self, width, height):
        """
        Adjust the viewport due to window resizing.
        """
        # make sure the viewport matches the new window dimensions note that width and 
        # height will be significantly larger than specified on retina displays.
        glViewport(0, 0, width, height)
        self.camera.resizeView(width, height)
        if (self.debug1):
            print("\n\tWindow Dimensions: ", width, ", ", height, ".")
        self.width = width
        self.height = height

    def soundMaker(self, tinfo = ""):
        """
        Create the background music.
        """
        uargv = ""
        if (self.debug1):
            print("\n\tThe thread", tinfo, "is starting.")
        uargv = tinfo.upper()
        buffer = sf.SoundBuffer.from_file(self.soundFile)
        if (not buffer):
            print("\n\tUnable to load the sound", self.soundFile, ".")
        sound = sf.Sound(buffer)
        sound.loop = True
        while(True):
            sound.play()
            sf.sleep(sf.seconds(300))
        if (self.debug1):    
            print("\n\tThe thread", uargv, "is terminated.")
    
    def permLoc(self):
        """
        Calculate the locations and orientations.
        """
        loc = list()
        index = 1
        # Random angle for each instance, compute the MVP later
        loc.append([self.calcRand(), self.calcRand(), self.calcRand() - 15.0])
        for x in range(1, self.arraysize + 1):
            angles = zeros((4), 'f')
            picIndex = zeros((6), 'i')
            loc.append([self.calcRand(), self.calcRand(), self.calcRand() - 15.0])
            for y in range(x):
                # Check for collision and correct if necessary.
                point1 = vec3(loc[x - 1][0], loc[x - 1][1], loc[x - 1][2])
                point2 = vec3(loc[y][0], loc[y][1], loc[y][2])
                if (distance(point1, point2) < 1.50):
                    loc[x - 1] = [self.calcRand(), self.calcRand(), self.calcRand() - 15.0]
                    # Reset the loop so the system can check  
                    # if it is an acceptable location.
                    y = 0
            # Find the spin axis.
            xaxis = vec3(self.calcRand(), self.calcRand(), self.calcRand())
            normalize(xaxis)
            yaxis = vec3(self.calcRand(), self.calcRand(), self.calcRand())
            normalize(yaxis)
            for y in range(2, 4):
                angles[y] = random() * 2.0
            for y in range(6):
                picIndex[y] = index
                if (self.debug1):
                    print("\n\tIndex:  ", index)
                index += 1    
                if ((index % (len(self.boximages) - 1)) == 0):
                    index = 1
            # Create a new data item.
            if (self.debug1):
                print("\n\tSize of loc: ", len(loc), " value of x ", x, "")
            locItem = PosOrient()
            locItem.locon = vec3(loc[x - 1][0], loc[x - 1][1], loc[x - 1][2])
            locItem.angles = angles
            locItem.indices = picIndex
            locItem.xaxis = xaxis
            locItem.yaxis = yaxis
            locItem.dist = 0
            # Calculate six image indices.
            
            # Add the item to the collection.
            self.distVals.append(locItem)
        if (self.debug1):
            self.debugPrint()
    

    def calcRand(self):
        """
        Random number for x,y,z values for cube location.
        """
        MAXLOC = 10.0
        item = 1000.0
        while ((item < -MAXLOC) or (item > MAXLOC) or (item == 0)):
            dividend = float(randint(0, 100))
            divisor = float(randint(1, 100))
            scalar = dividend / (divisor + 1.0)
            sign = randint(0, 10)
            if (sign < 5):
                sign = -1.0
            else:
                sign = 1.0
            item = sign * scalar * (float(randint(0, MAXLOC)))
            while (abs(item) > MAXLOC):
                item /= 2.0
        return item

    def debugPrint(self):
        """
        Print the cube location and orientation data.
        """
        for x in self.distVals:
            x.repr()


# Remember the Maine.
def main():
    """ Start the program.
    """
    glutwin = MultiCube()
    glutDisplayFunc(glutwin.eventLoop)
    glutIdleFunc(glutwin.eventLoop)
    glutReshapeFunc(glutwin.framebufferSize)
    glutKeyboardFunc(glutwin.keyDown)
    glutSpecialFunc(glutwin.funcKeyDown)
    glutPassiveMotionFunc(glutwin.mouseMove)
    glutMainLoop()
    print("\n\tEnd Program.\n\n")
    glDeleteTextures(len(glutwin.textureID), glutwin.textureID)
    glutwin.sndthrd.terminate()
    return

# Run it all.
main()
    
