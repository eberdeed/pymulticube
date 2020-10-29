"""
****************************************************************
* Camera:  A class to contain the functions of an OpenGL camera.
* Adapted from a class proposed on www.learnopengl.com.
* Edward C. Eberle <eberdeed@eberdeed.net>
* May 2020 San Diego, California USA
****************************************************************
"""
from math import asin, sin, cos, fmod
from glm import *
from numpy import array, zeros
from OpenGL.GLU import gluPerspective, gluLookAt
import os, sys
class Camera:
    """ 
    Camera:  A camera class that processes input and calculates the 
    corresponding Euler Angles, Vectors and Matrices for moving the 
    camera about a 3-dimensional landscape. For use in OpenGL.  This 
    class relies heavily on GLM the OpenGL Math Library.
    """
    
    """ 
    Defines several possible options for camera movement. Used as 
    abstraction to stay away from window-system specific input methods.
    To access this from the calling class use: 
    "Camera.Camera_Movement.index("FORWARD")," etc.
    """
    Camera_Movement = ([
        "FORWARD",
        "BACKWARD",
        "LEFT",
        "RIGHT",
        "CLOSER",
        "AWAY",
        "UP",
        "DOWN"
    ])
    """
    Constants
    The Default camera values.
    """
    YAW    = -90.0
    PITCH  =  0.0
    SPEED       =  0.1
    SENSITIVITY =  1.0
    ZOOM        =  45.0
    WORLDUP     =  vec3(0.0, 1.0, 0.0)
    """
    Variables
    Camera Attributes
    """
    Position = None
    Front = None
    Up = None
    Focus = None
    Right = None
    WorldUp = None
    """
    Persistent camera attributes.
    """
    position = None
    focus = None
    front = None
    """
    Euler Angles: Large is current and small is persistent.
    """
    Yaw = 0.
    yaw = 0.
    Pitch = 0.
    pitch = 0.
    """
    Camera options
    Adjust this to account for timing of the keyboard.
    """
    MovementSpeed = 0.
    """
    Adjust this to account for the mouse movement.
    """
    MouseSensitivity = 0.
    """
    Zoom for a more detailed view of an object.
    """
    Zoom = 0.
    """
    Viewport dimensions.
    """
    Width = 0
    Height = 0
    width = 0
    height = 0
    """
    Perspective matrix.
    """
    projection = identity(mat4)
    """
    The debug flag. Setting this to True will give debug data on the console.
    """
    debug1 = False
    # Functions 
    def __init__(self, width, height, position = vec3(0.0, 0.0, 2.0), focus = vec3(0.0, 0.0, 0.0)): 
        """ 
        Constructor with vectors to define viewer position and focus.
        width : the width of the viewport.
        height : the height of the viewport.
        position : the position of the camera.
        focus :  the position of the object looked at.
        """
        print("\n\tCreating Camera.")
        self.Width = self.width = width
        self.Height = self.height = height
        self.position = self.Position = position
        self.focus = self.Focus = focus
        self.MovementSpeed = self.SPEED
        self.MouseSensitivity = self.SENSITIVITY
        self.Zoom = self.ZOOM
        self.WorldUp = self.WORLDUP
        self.getEulerAngles()
        self.yaw = self.Yaw
        self.pitch = self.Pitch
        self.front = self.Front
        if (self.debug1):
            print("\n\t Constructor : Vectors : Yaw:  ",
            self.Yaw, "  Pitch:  ", self.Pitch,
            " Position:  ", self.Position.x, ", ",
            self.Position.y, ", ", self.Position.z,
            " Focus:  ", self.Focus.x, ", ",
            self.Focus.y, ", ", self.Focus.z,
            " Front:  ", self.Front.x, ", ",
            self.Front.y, ", ", self.Front.z)
            
    def setCamera(self, width, height, posX, posY, posZ, upX, upY, upZ, yaw, pitch):
        """ 
        Set the camera values to define viewer postion and Euler angles for direction.
        width : the width of the viewport.
        height : the height of the viewport.
        posX, posY, posZ : the (x, y, z) position of the camera.
        upX, upY, upZ : the (x, y, z) up direction of camera up.
        yaw : yaw based on (x > 0, 0, 0) as zero radians (right <-> left).
        pitch : pitch based on (x, 0, z) as zero radians (up <-> down).
        """
        self.Width = self.width = width
        self.Height = self.height = height
        self.MovementSpeed = self.SPEED
        self.MouseSensitivity = self.SENSITIVITY
        self.Zoom = self.ZOOM
        self.position = self.Position = vec3(posX, posY, posZ)
        self.WorldUp = vec3(upX, upY, upZ)
        self.yaw = self.Yaw = yaw
        self.pitch = self.Pitch = pitch
        self.getFront()
        self.focus = self.Focus
        self.front = self.Front
        
    def setGluViewMatrix(self):
        """ 
        Sets the LookAt Matrix using GLU.
        """
        tmpVec = self.Position + self.Front
        self.Focus = tmpVec
        if (self.debug1):
            print("\n\t getGluViewMatrix() Vectors : Yaw:  ",
            self.Yaw, "  Pitch:  ", self.Pitch,
            " Position:  ", self.Position.x, ", ",
            self.Position.y, ", ", self.Position.z,
            " Focus:  ", self.Focus.x, ", ",
            self.Focus.y, ", ", self.Focus.z,
            " Front:  ", self.Front.x, ", ",
            self.Front.y, ", ", self.Front.z)
        gluLookAt(
            self.Position.x, self.Position.y, self.Position.z, 
            tmpVec.x, tmpVec.y, tmpVec.z, 
            self.Up.x, self.Up.y, self.Up.z
        )
        
    def setGluPerspective(self):
        """  
        Sets the current perspective matrix using GLU.
        """
        gluPerspective(self.Zoom, self.Width / self.Height, 0.1, 10000.0)        
    def getViewMatrix(self):
        """ 
        Returns the LookAt Matrix using GLM.
        """
        tmpVec = self.Position + self.Front
        if (self.debug1):
            print("\n\t getViewMatrix() Vectors : Yaw:  ",
            self.Yaw, "  Pitch:  ", self.Pitch,
            " Position:  ", self.Position.x, ", ",
            self.Position.y, ", ", self.Position.z,
            " Focus:  ", self.Focus.x, ", ",
            self.Focus.y, ", ", self.Focus.z,
            " Front:  ", self.Front.x, ", ",
            self.Front.y, ", ", self.Front.z)
        tmpMat = lookAt(self.Position, tmpVec, self.Up)
        return self.mat4tonumpy(tmpMat)
    def getPerspective(self):
        """  
        Returns the current perspective matrix using GLM.
        """
        tmpMat = perspective(self.Zoom, self.Width / self.Height, 0.1, 10000.0)        
        return self.mat4tonumpy(tmpMat)

    def getPitchYaw(self):
        """
        Return the pitch and yaw as a tuple.
        """
        self.getEulerAngles()
        return (self.Pitch, self.Yaw)
        
    def resizeView(self, width, height):
        """ 
        Allows the viewport to be resized.
        """
        self.Width = width
        self.Height = height
        
    def resetCamera(self):
        """ 
        Return the camera to its original settings.
        """
        self.MovementSpeed = self.SPEED
        self.MouseSensitivity = self.SENSITIVITY
        self.Up = self.WorldUp = self.WORLDUP
        self.Zoom = self.ZOOM
        self.Position = self.position
        self.Focus = self.focus
        self.Front = self.front
        self.Yaw = self.yaw
        self.Pitch = self.pitch
        
    def getPosition(self):
        """ 
        Get the camera position.
        """
        return self.Position

    def setPosition(self, position):
        """ 
        Set the camera position.
        """
        self.Position = position
        
    def reverseDirection(self):
        """ 
        Rotate the camera 180 degrees
        on the XZ plane.
        """
        if (self.debug1):
            print("\n\treverseDirection()  Yaw:  ", self.Yaw)
        self.Yaw += 180
        self.Yaw = fmod(self.Yaw, 360.0)
        if(isnan(self.Yaw)):
            self.Yaw = 0.
        if (self.debug1):
            print("\n\t reverseDirection() Vectors : Yaw:  ", 
           self.Yaw, "  Pitch:  ", self.Pitch,
           " Position:  ", self.Position.x, ", ", 
           self.Position.y, ", ", self.Position.z,
           " Focus:  ", self.Focus.x, ", ", 
           self.Focus.y, ", ", self.Focus.z,
           " Front:  ", self.Front.x, ", ", 
           self.Front.y, ", ", self.Front.z)
        self.getFront()
        
    def processKeyboard(self, direction, deltaTime):
        """ 
        Processes input received from any keyboard-like input system. 
        Accepts input parameter in the form of camera defined index,
        such as Camera.Camera_Movement.index("RIGHT") or 
        Camera.Camera_Movement.index("UP")  (to abstract it from windowing 
        systems). This is adjustable using the SPEED variable.
        """
        velocity = abs(self.MovementSpeed * deltaTime)
        if (direction == self.Camera_Movement.index("FORWARD")):
            self.Position += self.Front * velocity
        elif (direction == self.Camera_Movement.index("BACKWARD")):
            self.Position -= self.Front * velocity
        elif (direction == self.Camera_Movement.index("LEFT")):
            self.Position -= self.Right * velocity
        elif (direction == self.Camera_Movement.index("RIGHT")):
            self.Position += self.Right * velocity
        elif (direction == self.Camera_Movement.index("UP")):
            self.Position += self.Up * velocity
        elif (direction == self.Camera_Movement.index("DOWN")):
            self.Position -= self.Up * velocity
        elif (direction == self.Camera_Movement.index("CLOSER")):
            self.Zoom -= 1.0
        elif (direction == self.Camera_Movement.index("AWAY")):
            self.Zoom += 1.0
        if (self.debug1):
            print("\n\tprocessKeyboard() : self.Position:  ", self.Position.x, ", ", 
            self.Position.y, ", ", self.Position.z, " Zoom:  ",
            self.Zoom, "  Right:  ", self.Right.x, ", ",
            self.Right.y, ", ", self.Right.z) 
        self.Focus = self.Position + self.Front

    
    def processMouseMovement(self, xoffset, yoffset):
        """ 
        Processes input received from a mouse input system. 
        It expects the offset value in both the x and y direction.
        This is adjustable using the SENSITIVITY variable.
        """
        xoffset *= self.MouseSensitivity
        yoffset *= self.MouseSensitivity
        if (self.debug1):
            print("\n\tMouse Offset Before x, y:  ", xoffset, 
            ", ", yoffset, " Yaw:  ", self.Yaw, 
            " Pitch:  ", self.Pitch)
        self.Yaw   += xoffset
        self.Pitch -= yoffset
        self.Yaw = fmod(self.Yaw, 180.0)
        self.Pitch  = fmod(self.Pitch, 90.0)
        if (self.debug1):
            print("\n\tMouse Offset After x, y:  ", xoffset, 
            ", ", yoffset, " Yaw:  ", self.Yaw, 
            " Pitch:  ", self.Pitch)
        #Update Front, Right and Up Vectors using the updated Euler angles
        self.getFront()
        
    def processMouseScroll(self, inout):
        """ 
        Process input received from a mouse scroll-wheel event. 
        This method only requires input on the wheel-axis
        """
        if (inout == self.Camera_Movement.index("AWAY")):
            self.Zoom += 1.0
        if (inout == self.Camera_Movement.index("CLOSER")):
            self.Zoom -= 1.0
        if(self.Zoom <= 1.0):
            self.Zoom = 1.0
        if(self.Zoom >= 90.0):
            self.Zoom = 90.0
        
    def getEulerAngles(self):
        """ 
        Calculates the Euler angles from the front vector.
        """
        # Calculate the new Front vector
        self.Front = normalize(self.Focus - self.Position)
        self.Pitch = degrees(asin(self.Front.y))
        # Also re-calculate the Right and Up vector
        self.Right = normalize(self.crossProduct(self.Front, self.WorldUp))  # Normalize the vectors.
        self.Up    = normalize(self.crossProduct(self.Right, self.Front))
        xzVec = normalize(self.crossProduct(self.WORLDUP, self.Right))
        if (xzVec.x < 0.0):
            self.Yaw = degrees(acos(xzVec.z)) - 180.0
        else:
            self.Yaw = -(degrees(acos(xzVec.z)) - 180.0)
        if (self.debug1):
            print("\n\t getEulerAngles() Vectors : Yaw:  ",
            self.Yaw, "  Pitch:  ", self.Pitch,
            " Position:  ", self.Position.x, ", ",
            self.Position.y, ", ", self.Position.z,
            " Focus:  ", self.Focus.x, ", ",
            self.Focus.y, ", ", self.Focus.z,
            " Front:  ", self.Front.x, ", ",
            self.Front.y, ", ", self.Front.z)
        
    def getFront(self):
        """ 
        Calculate the front vector from the Euler angles.
        """
        tmpVec = vec3()
        tmpVec.x = sin(radians(self.Yaw)) * cos(radians(self.Pitch))
        tmpVec.y = sin(radians(self.Pitch))
        tmpVec.z = -cos(radians(self.Yaw)) * cos(radians(self.Pitch))
        self.Front = normalize(tmpVec)
        self.Focus = self.Position + self.Front
        # Also re-calculate the Right and Up vector
        self.Right = normalize(self.crossProduct(self.Front, self.WorldUp))  # Normalize the vectors.
        self.Up    = normalize(self.crossProduct(self.Right, self.Front))
        if (self.debug1):
            print("\n\tgetFront() Vectors : Yaw:  ",
            self.Yaw, "  Pitch:  ", self.Pitch,
            " Position:  ", self.Position.x, ", ",
            self.Position.y, ", ", self.Position.z,
            " Focus:  ", self.Focus.x, ", ",
            self.Focus.y, ", ", self.Focus.z,
            " Front:  ", self.Front.x, ", ",
            self.Front.y, ", ", self.Front.z,
            " Up:  ", self.Up.x, ", ",
            self.Up.y, ", ", self.Up.z,
            " Right ", self.Right.x, ", ",
            self.Right.y, ", ", self.Right.z)

    def mat4tonumpy(self, value):
        """ 
        Convert a GLM mat4 to a numpy float array.
        """
        arrayval = zeros((4, 4), 'f')
        count = 0
        for x in range(4):
            for y in range(4):
                arrayval[x][y] = value[x][y]
        return arrayval
        
    def printMat4(self, printMat):
        print("\tPrinting a 4x4 matrix.")
        for x in range(0, 4):
            print("\tVector values for row ", x, end = " : ") 
            for y in range(0, 4):
                print(printMat[y][x], end=", ")
            print()
        print("\n")
    
    def crossProduct(self, a, b):
        result =  vec3(0.0)
        result.x = a.y * b.z - a.z * b.y
        result.y = a.z * b.x - a.x * b.z
        result.z = a.x * b.y - a.y * b.x
        return result
