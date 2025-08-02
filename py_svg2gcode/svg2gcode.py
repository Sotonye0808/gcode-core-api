#!/usr/bin/env python

# External Imports
import os
import sys
import xml.etree.ElementTree as ET

# Local Imports
#sys.path.insert(0, "./local_lib")  # (Import from lib folder)
import py_svg2gcode.local_lib.shapes as shapes_pkg
from py_svg2gcode.local_lib.shapes import point_generator
from .config import *

class SVGConverter:
    """
    Args:
        debugging: to determine whether to apply testing methods or not

        toDefDir: short for 'to default directory?'. Set to False if you don't want initial functionality of program of saving output gcode file in a directory '/gcode_output' in the same directory as original svg file
    """
    def __init__(self, debugging=True, toDefDir=True):
        self.DEBUGGING = debugging
        self.toDefDir = toDefDir
        self.SVG = set(["rect", "circle", "ellipse", "line", "polyline", "polygon", "path"])
        self.log = ""

    def debug_log(self, message):
        if self.DEBUGGING:
            print(message)
        return message + "\n"

    def generate_gcode(self, filename):
        """
        The main method that converts svg files into gcode files.

        Args:
            filename: The full path to the SVG file to be converted. 'path/to/file.svg'      

        Returns:
            gcode: The gcode equivalent of the SVG file inputed.  
        """
        self.log = ""
        
        # Check File Validity
        if not os.path.isfile(filename):
            raise ValueError('File "' + filename + '" not found.')

        if not filename.endswith(".svg"):
            raise ValueError('File "' + filename + '" is not an SVG file.')

        # Define the Output
        self.log += self.debug_log("Input File: " + filename)

        # Process SVG
        gcode = self._process_svg(filename)
        
        # Save to default directory if toDefDir is True
        if self.toDefDir:
            file = filename.split("/")[-1]
            dirlist = filename.split("/")[:-1]
            dir_string = "/".join(dirlist) + "/" if dirlist else ""

            # Make Output File
            outdir = dir_string + "gcode_output/"
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            outfile = outdir + file.split(".svg")[0] + ".gcode"
            
            # Write the Result
            with open(outfile, "w+") as ofile:
                ofile.write(gcode)
        
        return gcode

    def _process_svg(self, filename):
        """Internal method to process SVG file and generate G-code"""
        # Get the SVG Input File
        tree = ET.parse(filename)
        root = tree.getroot()

        # Get dimensions and scaling
        width, height, scale = self._get_dimensions(root)
        
        # Generate G-code
        gcode = preamble + "\n"
        
        # Process SVG elements
        for elem in root.iter():
            gcode += self._process_element(elem, scale)
            
        gcode += postamble + "\n"
        return gcode

    def _get_dimensions(self, root):
        """Extract and calculate dimensions from SVG root"""
        width = root.get("width")
        height = root.get("height")
        if width is None or height is None:
            viewbox = root.get("viewBox")
            if viewbox:
                _, _, width, height = viewbox.split()

        if width is None or height is None:
            raise ValueError("Unable to get width or height for the svg")

        # Clean up dimensions
        width = float(str(width).replace("pt", "").replace("px", ""))
        height = float(str(height).replace("pt", "").replace("px", ""))

        # Calculate scaling
        scale_x = bed_max_x / width
        scale_y = bed_max_y / height
        scale = min(scale_x, scale_y)
        if scale > 1:
            scale = 1

        return width, height, scale

    def _process_element(self, elem, scale):
        """Process individual SVG elements"""
        gcode = ""
        try:
            tag_suffix = elem.tag.split("}")[-1]
        except:
            return ""

        if tag_suffix in self.SVG:
            shape_class = getattr(shapes_pkg, tag_suffix)
            shape_obj = shape_class(elem)
            d = shape_obj.d_path()
            m = shape_obj.transformation_matrix()

            if d:
                gcode += shape_preamble + "\n"
                points = point_generator(d, m, smoothness)
                new_shape = True

                for x, y in points:
                    x = scale * x
                    y = bed_max_y - scale * y

                    if 0 <= x <= bed_max_x and 0 <= y <= bed_max_y:
                        if new_shape:
                            gcode += f"G0 X{x:.1f} Y{y:.1f}\nM03\n"
                            new_shape = False
                        else:
                            gcode += f"G0 X{x:.1f} Y{y:.1f}\n"

                gcode += shape_postamble + "\n"

        return gcode

def test(filename):
    """Simple test function to call to check that this
    module has been loaded properly"""
    circle_gcode = "G28\nG1 Z5.0\nG4 P200\nG1 X10.0 Y100.0\nG1 X10.0 Y101.8\nG1 X10.6 Y107.0\nG1 X11.8 Y112.1\nG1 X13.7 Y117.0\nG1 X16.2 Y121.5\nG1 X19.3 Y125.7\nG1 X22.9 Y129.5\nG1 X27.0 Y132.8\nG1 X31.5 Y135.5\nG1 X36.4 Y137.7\nG1 X41.4 Y139.1\nG1 X46.5 Y139.9\nG1 X51.7 Y140.0\nG1 X56.9 Y139.4\nG1 X62.0 Y138.2\nG1 X66.9 Y136.3\nG1 X71.5 Y133.7\nG1 X75.8 Y130.6\nG1 X79.6 Y127.0\nG1 X82.8 Y122.9\nG1 X85.5 Y118.5\nG1 X87.6 Y113.8\nG1 X89.1 Y108.8\nG1 X89.9 Y103.6\nG1 X90.0 Y98.2\nG1 X89.4 Y93.0\nG1 X88.2 Y87.9\nG1 X86.3 Y83.0\nG1 X83.8 Y78.5\nG1 X80.7 Y74.3\nG1 X77.1 Y70.5\nG1 X73.0 Y67.2\nG1 X68.5 Y64.5\nG1 X63.6 Y62.3\nG1 X58.6 Y60.9\nG1 X53.5 Y60.1\nG1 X48.3 Y60.0\nG1 X43.1 Y60.6\nG1 X38.0 Y61.8\nG1 X33.1 Y63.7\nG1 X28.5 Y66.3\nG1 X24.2 Y69.4\nG1 X20.4 Y73.0\nG1 X17.2 Y77.1\nG1 X14.5 Y81.5\nG1 X12.4 Y86.2\nG1 X10.9 Y91.2\nG1 X10.1 Y96.4\nG1 X10.0 Y100.0\nG4 P200\nG4 P200\nG1 X110.0 Y100.0\nG1 X110.0 Y101.8\nG1 X110.6 Y107.0\nG1 X111.8 Y112.1\nG1 X113.7 Y117.0\nG1 X116.2 Y121.5\nG1 X119.3 Y125.7\nG1 X122.9 Y129.5\nG1 X127.0 Y132.8\nG1 X131.5 Y135.5\nG1 X136.4 Y137.7\nG1 X141.4 Y139.1\nG1 X146.5 Y139.9\nG1 X151.7 Y140.0\nG1 X156.9 Y139.4\nG1 X162.0 Y138.2\nG1 X166.9 Y136.3\nG1 X171.5 Y133.7\nG1 X175.8 Y130.6\nG1 X179.6 Y127.0\nG1 X182.8 Y122.9\nG1 X185.5 Y118.5\nG1 X187.6 Y113.8\nG1 X189.1 Y108.8\nG1 X189.9 Y103.6\nG1 X190.0 Y98.2\nG1 X189.4 Y93.0\nG1 X188.2 Y87.9\nG1 X186.3 Y83.0\nG1 X183.8 Y78.5\nG1 X180.7 Y74.3\nG1 X177.1 Y70.5\nG1 X173.0 Y67.2\nG1 X168.5 Y64.5\nG1 X163.6 Y62.3\nG1 X158.6 Y60.9\nG1 X153.5 Y60.1\nG1 X148.3 Y60.0\nG1 X143.1 Y60.6\nG1 X138.0 Y61.8\nG1 X133.1 Y63.7\nG1 X128.5 Y66.3\nG1 X124.2 Y69.4\nG1 X120.4 Y73.0\nG1 X117.2 Y77.1\nG1 X114.5 Y81.5\nG1 X112.4 Y86.2\nG1 X110.9 Y91.2\nG1 X110.1 Y96.4\nG1 X110.0 Y100.0\nG4 P200\nG28\n"
    print(circle_gcode[:90], "...")
    return circle_gcode


if __name__ == "__main__":
    """If this file is called by itself in the command line
    then this will execute."""
    # file = raw_input("Please supply a filename: ")
    # Python3:
    # file = input("Please supply a filename: ")
    # Take in an argument:

    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = input("Please supply a filename: ")

    converter = SVGConverter()
    converter.generate_gcode(file)
