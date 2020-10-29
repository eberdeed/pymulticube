"""
**********************************************************
* CreateImage: Using PIL the Python Imaging Library, this class 
* loads an image into memory, converts it to a 32 bit format with alpha, 
* and then passes it to a numpy byte array, then the image is be turned 
* into an OpenGL buffer object. It provides for a single image, a double 
* image (the first image is then combined with the rest of the list of 
* images, a vector of images, or a sky box containing six images. 
* Designed for OpenGL. The program requires that the user
* keep track of the OpenGL buffer object handle, and a start
* index for this value is required for each function.
* Created by: Edward Charles Eberle <eberdeed@eberdeed.net>
* May 2020 San Diego, California USA
* ********************************************************
"""
from PIL import Image
import sys, os
from OpenGL.GL import *
from numpy import zeros, array

class CreateImage:
    """ 
    CreateImage : Using PIL the Python Imaging Library, this class 
    loads an image into memory, converts it to a 32 bit format with alpha, 
    and then passes it to a numpy byte array, then the image is be turned 
    into an OpenGL buffer object. It provides for a single image, a double 
    image, a vector of images, or a sky box containing six images. 
    """
    width = 0
    # Image width.
    height = 0
    # Image height.
    size = 0
    # Overall image size.
    pixels = None
    # Image data.
    debug1 = False
    # Debug flag.
    
    def __init__(self):
        """ 
        Initialization flags the creation of the class.
        """
        print("\n\tCreating CreateImage.")
        return
    
    def doubleImage(self, imagearray, startindex = 0):
        """
        Create a series of double images using a passed list of filenames.  
        The first image (imagearray[0]) is used as the background for the 
        rest of the list.  The return value is a list of OpenGL buffer 
        object handles for the double images created.  The startindex 
        value is the start of the numbering for the OpenGL buffer object handles.
        """
        textureID = list()
        # The list of OpenGL texture buffer object handles.
        if (self.debug1):
            print("\n\tIn doubleImage().\n")
        for x in range(len(imagearray)):
            textureID.append(startindex + x)
        if (self.debug1):
            print("\n\tType of textureID ", type(textureID), " with size ", 
            len(textureID), "\n")
        # The PIL Image loads a standard picture.
        tmpImage1 = Image.open(imagearray[0])
        if (not tmpImage1):
            print("\n\tImage file ", imagearray[0], " failed to load in createimage.")
        else:
            print("\n\tImage file ", imagearray[0], " successfully loaded.")
        self.size = 0
        # Convert the image to four 8 bit fields RGBA.
        txtImage1 = tmpImage1.convert("RGBA")
        for x in range(len(imagearray) - 1):
            self.pixels = None
            # The PIL Image loads a standard picture.
            tmpImage2 = Image.open(imagearray[x])
            if (not tmpImage2):
                print("\n\tImage file ", imagearray[x], " failed to load in createimage.")
            else:
                print("\n\tImage file ", imagearray[x], " successfully loaded.")
            self.size = 0
            # Convert image to four 8 bit fields RGBA.
            txtImage2 = tmpImage2.convert("RGBA")
            tmpImage2 = txtImage2.rotate(180)
            # Combine the two images using the alpha_composite method.
            finalImage = Image.alpha_composite(txtImage1, tmpImage2)
            if (self.debug1):
                # View the result.
                finalImage.save("blendImage.png")
            (self.width, self.height) = finalImage.size
            # Load the image into a byte array.
            tmpdata = list(finalImage.getdata())
            self.pixels = array(tmpdata, "byte")
            # Bind the texture ID and load texture data 
            glBindTexture(GL_TEXTURE_2D, textureID[x])
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)
            glGenerateMipmap(GL_TEXTURE_2D)    
            #  Parameters
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glBindTexture(GL_TEXTURE_2D, 0)
            if (self.debug1):
                print("\n\tDouble Image texture ID", textureID)
        return textureID

    """
    Accessor functions for the given image's dimensions and data.
    """

    def getWidth(self):
        """
        Image width in pixels.
        """
        return self.width

    def getHeight(self):
        """
        Image height in pixels.
        """
        return self.height

    def getSize(self):
        """
        The overall size of the image in bytes.
        """
        return self.size

    def getData(self):
        """
        The void* blob containing the picture data.
        """
        return self.pixels
    
    def textureObject(self, imagefile, index = 0):
        """
        Provide a filename and an OpenGL buffer handle,
        and receive an OpenGL buffer object tied to 
        that handle.
        """
        self.pixels = None
        # Image data.
        self.pixels = self.getData(imagefile)
        # Bind the texture ID and load the texture data. 
        textureID = index
        glBindTexture(GL_TEXTURE_2D, textureID)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)
        glGenerateMipmap(GL_TEXTURE_2D)    
        #  Parameters
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        return textureID
        
    def createSkyBoxTex(self, filenames, index = 0):
        """
        Provide a list of six filenames and a buffer 
        handle number and return an OpenGL sky box object
        tied to that number.
        Loads a cubemap texture from 6 individual texture faces.
        The order of the faces should be:
        +X (right)
        -X (left)
        +Y (top)
        -Y (bottom)
        +Z (front) 
        -Z (back)
        """
        if (self.debug1):
            print("\n\tIn createSkyBoxTex().\n")
        textureID = index
        glBindTexture(GL_TEXTURE_CUBE_MAP, textureID)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
         # Six images, one texture ID.
        for i in range(6):
            txtImage = Image.open(filenames[i])
            if (not txtImage):
                print("\n\tImage load failure for image ", filenames[i],
                "Only a partial load is present.")
                continue
            else:
                print("\n\tLoaded sky box image: ", filenames[i], ".")
            # Align the ceiling and the floor.
            if (i == 2):
                tmpImage = txtImage.rotate(90)
                txtImage = tmpImage
            if (i == 3):
                tmpImage = txtImage.rotate(-90)
                txtImage = tmpImage
            tmpImage = txtImage.transpose(Image.FLIP_LEFT_RIGHT)
            txtImage = tmpImage.convert("RGBA")
            tmpImage = txtImage.resize((512,512))
            tmpdata = list(tmpImage.getdata())
            self.pixels = array(tmpdata, "byte")
            (self.width, self.height) = tmpImage.size
            if (self.debug1):
                print("\n\tImage size: ", self.width, ",", self.height, "\n")
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)
        glGenerateMipmap(GL_TEXTURE_CUBE_MAP)    
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        return textureID

        
    def create2DTexArray(self, filenames, index = 0):
        """
        Create an array of images for an OpenGL Texture2DArray object
        using a provided file name list and a buffer handle.
        """
        textureID = index
        count = 0
        glBindTexture(GL_TEXTURE_2D_ARRAY, textureID)
        self.pixels = self.getData(filename[0])
        # The overall data store.
        pixel_data = zeros((size * len(filenames)), "byte")
        for x in range(size):
            pixel_data[count] = pixels[x]
            count += 1
        for i in range(1, len(filenames)):
            self.pixels = self.getData(filenames[i])
            for x in range(size):
                pixel_data[count] = pixels[x]
                count += 1
        if (self.debug1):
            print("\n\n\tPixels loaded:  ", count, 
            "  Pixels calculated:  ", len(filenames) * size, "\n\n")
        glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA, self.width, self.height, len(filenames), 0, GL_RGBA, GL_UNSIGNED_BYTE, pixel_data)
        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_R, GL_REPEAT)
        glBindTexture(GL_TEXTURE_2D_ARRAY, 0)
        return textureID

    def getData(self, filename):
        """
        The PIL Image class loads standard picture
        and it is returned as a numpy byte array.
        """
        txtImage = Image.open(filename)
        if (not txtImage):
            print("\n\tImage file ", filename, " failed to load in createimage.")
        else:
            print("\n\tImage file ", filename, " successfully loaded.")
        self.size = 0
        # Convert the image to four 8 bit fields RGBA.
        tmpImage = txtImage.convert("RGBA")
        # The image size in pixels.
        (self.width, self.height) = tmpImage.size
        # The overall image size in bytes.
        self.size = self.width * self.height * 4
        # Load the image into a numpy byte array.
        tmpdata = list(tmpImage.getdata())
        return array(tmpdata, "byte")
        
        
