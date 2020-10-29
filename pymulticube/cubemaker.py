#!/usr/bin/python3
"""
**********************************************************
* CubeMaker:  A class to create a cube.  It uses numpy arrays
* and GLM for the transformations.  It will produce texture
* coordinates and/or normals for the cube.
* Created by: Edward Charles Eberle <eberdeed@eberdeed.net>
* May 2020 San Diego, California USA
* ********************************************************
"""
import sys, os
from glm import *
from numpy import array, zeros

class CubeMaker:
    """
    CubeMaker:  A class to create a cube.  It uses numpy arrays
    and GLM for the transformations.  It will produce texture
    coordinates and/or normals for the cube.
    """
    def __init__(self):
        """
        Echo the creation of the class.
        """
        print("\n\tCreating CubeMaker.")
        return
    # The vertices of one side of the cube.
    vertices = array(([
        [0.5, -0.5, 0.5],
        [-0.5, -0.5, 0.5],
        [0.5, 0.5, 0.5],
        [-0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.5],
        [0.5, 0.5, 0.5]    
    ]), 'f')
    # The normals for the cube.
    normals = array(([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [-1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, 0.0, -1.0]
    ]), 'f')
    # The adjustment for the vector element to ignore
    # for the texture coordinate.
    adjust = array(([
        2, 0, 1
    ]), 'i')
    # The texture coordinate array flag.
    textures = False
    # The normal vector array flag.
    normal = False
    # The cube array.
    cube = None
    # A debug flag.
    debug1 = False
    
    def createCube(self, textures, normal):
        """ 
        The entry method:  textures will signal the
        creation of texture coordinates if true, 
        similarly, normal signals the creation of 
        normals.
        """
        columns = 0
        self.textures = textures
        self.normal = normal
        if (self.debug1):
            print("\n\tTextures ", textures, "  Normals  ", normal, "\n")
        if ((not textures) and (not normal)):
            self.cube = zeros((36, 3), 'f')
            columns = 3
            if (self.debug1):
                print("\n\n\tNo normals or textures.\n\n")
        elif (not normal):
            self.cube = zeros((36, 5), 'f')
            columns = 5
            if (self.debug1):
                print("\n\n\tNo normals.\n\n")
        elif (not textures):
            self.cube = zeros((36, 6), 'f')
            columns = 6
            if (self.debug1):
                print("\n\n\tNo textures.\n\n")
        else:
            self.cube = zeros((36, 8), 'f')
            columns = 8
            if (self.debug1):
                print("\n\tNormals and textures.\n")
        self.rotateMatrix()
        if (self.debug1):
            print("\n\tCube size:  ", len(self.cube) * len(self.cube[0]), " compare to size:  ", 36 * columns, "\n")
            self.printCube()
        
        return self.cube
        
    def printCube(self):
        """
        A debug method to display the data.
        """
        if ((self.textures) and (self.normal)):
            print("\n    float self.cube[288] \n")
        elif (self.normal):
            print("\n    float self.cube[216] \n")
        elif (self.textures):
            print("\n    float self.cube[180] \n")
        else:
            print("\n    float self.cube[108] \n")
        for x in range(0, 36):
            if ((x != 0) and((x % 6) == 0)):
                print("\n")
            print("        ")
            if ((self.textures) and (self.normal)):
                for y in range(0, 8):
                    print(self.cube[x][y], end=", ")
            elif (self.normal):
                for y in range(0, 6):
                    print(self.cube[x][y], end=", ")
            elif (self.textures):
                for y in range(0, 5):
                    print(self.cube[x][y], end=", ")
            else:
                for y in range(0, 3):
                    print(self.cube[x][y], end=", ")
            print("\n")
        print("    \n\n")
        print("\n\n\tResultant Cube:  \n\n")
        print("\n\n\t****************************************\n\n")
        
    def createFrustum(self, right, left, bottom, top, near, far):
        """
        A convenience method to create a frustum matrix.
        """
        frustumBase = mat4x4(1.0) 
        frustumRow = vec4(0) 
        frustumRow = vec4(near /(right - left), 0.0, (right + left) / (right - left), 0.0)
        frustumBase[0] = frustumRow
        frustumRow = vec4(0.0, (2.0 * near) / (top - bottom), (top + bottom) / (top - bottom), 0.0)
        frustumBase[1] = frustumRow
        frustumRow = vec4(0.0, 0.0, (near + far)/(near - far), (2.0 * near * far) / (near - far))
        frustumBase[2] = frustumRow
        frustumRow = vec4(0.0, 0.0, -1.0, 0.0)
        frustumBase[3] = frustumRow
        return frustumBase

    def rotateMatrix(self):
        """ 
        Rotate the side of the matrix to create the other five sides.
        """
        data = zeros((6, 3))
        result = zeros((6, 3))
        tmpvec = vec4(0)
        matRow = zeros(3)
        pi180 = acos(-1)
        pi90 = acos(-1) / 2.0
        for x in range(0, 6):
            for y in range(0, 3):
                data[x][y] = self.vertices[x][y]
            result[x] = data[x]
        self.createSide(result, 0, 0)
        transform = identity(mat4)
        transform = rotate(transform, pi180, vec3(1.0, 0.0, 0.0))
        for x in range(0, 6):
            tmpvec = transform * vec4(data[x][0], data[x][1], data[x][2], 1.0)
            result[x] = vec3(tmpvec.x, tmpvec.y, tmpvec.z)
        self.createSide(result, 3, 6)
        transform = identity(mat4)
        transform = rotate(transform, pi90, vec3(0.0, 1.0, 0.0))
        for x in range(0, 6):
            tmpvec = transform * vec4(data[x][0], data[x][1], data[x][2], 1.0)
            result[x] = vec3(tmpvec.x, tmpvec.y, tmpvec.z)
        self.createSide(result, 1, 12)
        transform = identity(mat4)
        tmptrans = identity(mat4)
        transform = rotate(transform, -pi90, vec3(0.0, 1.0, 0.0))
        tmptrans = rotate(tmptrans, -pi90, vec3(1.0, 0.0, 0.0))
        for x in range(0, 6):
            tmpvec = tmptrans * transform * vec4(data[x][0], data[x][1], data[x][2], 1.0)
            result[x] = vec3(tmpvec.x, tmpvec.y, tmpvec.z)
        self.createSide(result, 4, 18)
        transform = identity(mat4)
        transform = rotate(transform, pi90, vec3(1.0, 0.0, 0.0))
        for x in range(0, 6):
            tmpvec = transform * vec4(data[x][0], data[x][1], data[x][2], 1.0)
            result[x] = vec3(tmpvec.x, tmpvec.y, tmpvec.z)
        self.createSide(result, 2, 24)
        transform = identity(mat4)
        transform = rotate(transform, -pi90, vec3(1.0, 0.0, 0.0))
        for x in range(0, 6):
            tmpvec = transform * vec4(data[x][0], data[x][1], data[x][2], 1.0)
            result[x] = vec3(tmpvec.x, tmpvec.y, tmpvec.z)
        self.createSide(result, 5, 30)

    def debug(self, items, x, face, texCoords):
        """
        A debug method to show the data as it is created.
        """
        if ((normal) and (textures)):
            print("\n", items[x][0], ", ", items[x][1], ", ", 
            items[x][2], ", ", normals[face].x, ", ", 
            normals[face].y, ", ", normals[face].z, ", ",
            texCoords[x][0], ", ", texCoords[x][1], ",")
        elif (normal):
            print("\n", items[x][0], ", ", items[x][1], ", ", 
            items[x][2], ", ", normals[face].x, ", ", 
            normals[face].y, ", ", normals[face].z, ", ")
        elif (textures):
            print("\n", items[x][0], ", ", items[x][1], ", " ,
            items[x][2], ", ", texCoords[x][0], ", ", 
            texCoords[x][1], ",")
        else:
            print("\n", items[x][0], ", ", items[x][1], ", ", 
            items[x][2], ", ")

    def createSide(self, items, face, offset):
        """
        Create an individual side after the transformation of the original.
        """
        texCoords = zeros((6, 2), 'f')
        count = 0
        for x in range(0, 6):
            tmpvec = items[x]
            tmptex = vec2(0)
            count = 0
            index = face
            if (index > 2):
                index -= 3
            if (self.textures):
                for y in range(0, 3):
                    if (y != self.adjust[index]): # Omit the element of the face.
                        if (tmpvec[y] > 0):
                            tmptex[count] = 1.0
                            count += 1
                        else:
                            tmptex[count] = 0.0
                            count += 1
                texCoords[x] = tmptex
        for x in range(0, 6):
            self.cube[offset + x][0] = items[x][0]
            self.cube[offset + x][1] = items[x][1]
            self.cube[offset + x][2] = items[x][2]
            if ((self.normal) and (self.textures)):
                self.cube[offset + x][3] = self.normals[face][0]
                self.cube[offset + x][4] = self.normals[face][1]
                self.cube[offset + x][5] = self.normals[face][2]
                self.cube[offset + x][6] = texCoords[x][0]
                self.cube[offset + x][7] = texCoords[x][1]
            elif (self.textures):
                self.cube[offset + x][3] = texCoords[x][0]
                self.cube[offset + x][4] = texCoords[x][1]
            elif (self.normal):
                self.cube[offset + x][3] = self.normals[face][0]
                self.cube[offset + x][4] = self.normals[face][1]
                self.cube[offset + x][5] = self.normals[face][2]

    
    def printVec3(self, printVec):
        """
        Print a 3 element vector.
        """
        vecVal = vec3(printVec)
        print("\n", vecVal.x, ", ", vecVal.y, ", ", vecVal.z)

        
    def printMat4(self, printMat):
        """
        Print a 4x4 matrix.
        """
        print("\n\tPrinting a 4x4 matrix.\n")
        printVec = vec4(0)
        for x in range(0, 4):
            printVec = printMat[x]
            print("\n\tVector values for row ", x, 
            printVec.x, ", ", printVec.y, ", ", printVec.z 
            , ", ", printVec.w)
        print("\n\n\n")


 # Remember the Maine.
def main():
    """ Start the program.
    """
    cuby = CubeMaker()
    cuby.createCube(False, False)
    frust = cuby.createFrustum(1.0, -1.0, -1.0, 1.0, 0.1, 1000)
    cuby.printMat4(frust)
    return

# Run it all.
#main()
