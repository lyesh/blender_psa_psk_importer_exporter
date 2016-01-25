import bpy
# import mathutils
import math
import types
from mathutils import Vector
from math import *
from bpy.props import *
from string import *
from struct import *
from math import *
from bpy.props import *

SIGNATURE = 0xDEADC0DE

def get_rip_file(input_file):

    texture_files = []
    shader_files = []
    faces = []
    vertices = []
    vertex_attribute_types = []
    input_stream = open(input_file, "rb")
    mesh_name = input_file.split('/')[-1].split('.')[0]

    mesh = bpy.data.meshes.new(mesh_name)
    (signature,version) = unpack('2I', input_stream.read(8))
    assert(signature == SIGNATURE)
    if version != 4:
        print("Unsupported version: %i", version)
        assert(False)

    input_data = unpack('6I', input_stream.read(24))
    num_faces = input_data[0]
    num_vertices = input_data[1]
    vertex_size = input_data[2]
    num_texture_files = input_data[3]
    num_shader_files = input_data[4]
    num_vertex_attributes = input_data[5]

    for vertex_attribute_index in range(0, num_vertex_attributes):
        attribute_type = get_cstring(input_stream)
        input_data = unpack('4I', input_stream.read(16))
        attribute_index = input_data[0]
        offset = input_data[1]
        size = input_data[2]
        type_map_elements = input_data[3]
        for type_element_index in range(0,type_map_elements):
            input_data = unpack('I',input_stream.read(4))
            vertex_attribute_types.append(input_data[0])

        if attribute_type == b'POSITION':
            pass


    for texture_file_index in range(0, num_texture_files):
        texture_files.append(get_cstring(input_stream))

    for shader_file_index in range(0, num_shader_files):
        shader_files.append(get_cstring(input_stream))

    for face_index in range(0, num_faces):
        input_data = unpack('3I',input_stream.read(12))
        faces.append((input_data[0],input_data[1],input_data[2]))

    for vertex_index in range(0, num_vertices):
        input_data = unpack('3f',input_stream.read(12))
        vertices.append(Vector((input_data[0],input_data[1],input_data[2])))
        for vertex_attribute_index in range(3, len(vertex_attribute_types)):
            get_data_of_type(input_stream,vertex_attribute_types[vertex_attribute_index])

    return



def get_cstring(stream):
    result = bytearray()
    while True:
        byte = stream.read(1)
        if byte == b'\x00':
            return result
        result += byte
    return "FAIL"

def get_data_of_type(stream,type):
    if type == 0:
        return unpack("f",stream.read(4))
    elif type == 1:
        return unpack("I",stream.read(4))
    elif type == 2:
        return unpack("i",stream.read(4))
    else:
        raise(NinjaRipError)

class NinjaRipError(Exception):
    pass

get_rip_file("/Users/ailish/Mesh_0778.rip")