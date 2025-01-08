'''OpenGL extension SGIS.texture_select

This module customises the behaviour of the 
OpenGL.raw.GL.SGIS.texture_select to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension introduces several new texture internal formats.  The
	purpose of these new formats is to reorganize the components of a
	texture into groups of components.  The currently selected group
	effectively becomes the internal format.
	
	Also, two new texture parameters are introduced that control the
	selection of these groups of components.
	
	For example, assume a texture internal format of DUAL_LUMINANCE4_SGIS is
	specified.  Now there are two groups of components, where each group has
	a format of LUMINANCE4.  One of the two LUMINANCE groups is always
	selected.  components can be selected and then interpreted as a LUMINANCE
	texture.
	
	The purpose of this extension is allow better utilization of texture
	memory by subdividing the internal representation of a texel into 1, 2,
	or 4 smaller texels.  Additionally, this may improve performance of
	texture downloads.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIS/texture_select.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.SGIS.texture_select import *
from OpenGL.raw.GL.SGIS.texture_select import _EXTENSION_NAME

def glInitTextureSelectSGIS():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION