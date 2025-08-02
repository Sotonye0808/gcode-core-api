# Python SVG to G-Code Converter
A fast svg to gcode compiler forked from [pjpscriv/py-svg2gcode](https://github.com/pjpscriv/py-svg2gcode), who originally forked it from  [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode).

This library takes an svg file `location/my_file.svg` and outputs the gcode conversion, optionally to a folder in the same directory `location/gcode_output/my_file.gcode`.

The file `config.py` contains the configurations for the conversion (printer bed size etc).

## Installation
Copy the folder, copy files one by one or clone the entire repo.
```
git clone https://github.com/Sotonye0808/Experiments.git
```

## Usage
### As a Python module
To import it into your existing python project:
```python

from py_svg2gcode import SVGConverter
... 
    converter = SVGConverter(debugging=True | False, toDefDir=True | False)
```
### As a Python Command
From the root directory, run
```
python svg2gcode.py
```

### With Bash Script (Recommended) [From previous developer. I, Sotonye, have not tested or attempted this]
You can also use the `RUNME` script to convert files.

This method is useful for debugging as it gives you extra information.
```
./RUNME my_svg_file.svg
```

## Details
The compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code.

## Changes made by this Developer, [Sotonye Dagogo](https://github.com/Sotonye0808)
The svg2gcode.py and other files were modified with OOP principles to enable calling of the methods in other python scripts as opposed to just command-line usage.
