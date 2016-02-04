import bpy
import bmesh
import mathutils
from bpy.props import *
from struct import *

SIGNATURE = 0xDEADC0DE


def get_rip_file(input_file):
    texture_files = []
    shader_files = []
    faces = []
    vertices = []
    vertex_attributes = []
    input_stream = open(input_file, "rb")
    mesh_name = input_file.split('/')[-1].split('.')[0]

    (signature, version) = unpack('2I', input_stream.read(8))
    assert (signature == SIGNATURE)
    if version != 4:
        print("Unsupported version: %i", version)
        raise NinjaRipError

    input_data = unpack('6I', input_stream.read(24))
    num_faces = input_data[0]
    num_vertices = input_data[1]
    vertex_size = input_data[2]
    num_texture_files = input_data[3]
    num_shader_files = input_data[4]
    num_vertex_attributes = input_data[5]

    for vertex_attribute_index in range(0, num_vertex_attributes):
        vertex_attributes.append(VertexAttribute(input_stream))

    for texture_file_index in range(0, num_texture_files):
        texture_files.append(get_cstring(input_stream))

    for shader_file_index in range(0, num_shader_files):
        shader_files.append(get_cstring(input_stream))

    for face_index in range(0, num_faces):
        input_data = unpack('3I', input_stream.read(12))
        faces.append((input_data[0], input_data[1], input_data[2]))

    for vertex_index in range(0, num_vertices):
        vertex = Vertex()
        for vertex_attribute in vertex_attributes:
            vertex.add_attribute(vertex_attribute, input_stream)
        vertices.append(vertex)

    mesh = bpy.data.meshes.new(mesh_name)
    ob = bpy.data.objects.new(mesh_name, mesh)
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    bm = bmesh.new()
    bm.from_mesh(mesh)

    for idx, vertex in enumerate(vertices):
        vert = bm.verts.new(vertex.attributes['POSITION'][0:3])
        # vert.normal = mathutils.Vector(vertex.attributes['NORMAL'])
        vert.index = idx
    bm.verts.ensure_lookup_table()

    for raw_face in faces:
        face = bm.faces.new((bm.verts[raw_face[0]],bm.verts[raw_face[1]],bm.verts[raw_face[2]]))
        uv_layer = bm.loops.layers.uv.verify()
        # bm.faces.layers.tex.verify()
        face.loops.index_update()
        for idx, loop in enumerate(face.loops):
            uv = loop[uv_layer].uv
            uvs = vertices[loop.vert.index].attributes['TEXCOORD']
            uv[0] = uvs[0]
            uv[1] = 1 - uvs[1]

    bm.to_mesh(mesh)
    ob.select = False

    return


def get_cstring(stream):
    result = bytearray()
    while True:
        byte = stream.read(1)
        if byte == b'\x00':
            return result
        result += byte
    return "FAIL"


def get_data_of_type(stream, data_type):
    if data_type == 0:
        return unpack("f", stream.read(4))[0]
    elif data_type == 1:
        return unpack("I", stream.read(4))[0]
    elif data_type == 2:
        return unpack("i", stream.read(4))[0]
    else:
        raise NinjaRipError


class NinjaRipError(Exception):
    pass


class VertexAttribute:
    def __init__(self, stream):
        self.vertex_attribute_types = []
        self.attribute_type = get_cstring(stream)
        input_data = unpack('4I', stream.read(16))
        self.attribute_index = input_data[0]
        self.offset = input_data[1]
        self.size = input_data[2]
        self.type_map_elements = input_data[3]

        for type_element_index in range(0, self.type_map_elements):
            input_data = unpack('I', stream.read(4))
            self.vertex_attribute_types.append(input_data[0])


class Vertex:
    def __init__(self):
        self.attributes = {}

    def add_attribute(self, attribute, stream):
        attributeName = attribute.attribute_type.decode(encoding="ascii")
        vector = []
        for type_element in attribute.vertex_attribute_types:
            vector.append(get_data_of_type(stream, type_element))
        if not attributeName in self.attributes:
            self.attributes[attributeName] = vector

# for i in range(200,240):
#     get_rip_file("/Users/ailish/bathroom-scene/Mesh_0"+str(i)+".rip")
get_rip_file("resources/Mesh_0785.rip")
