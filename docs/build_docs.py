# Copy the documentation files to a folder, allowing for some processing.
from __future__ import print_function
import os
import sys
import shutil
import re

def process_markdown(infile, outfile):
    """Remove the title of a markdown file, and add Jekyll front matter"""
    preamble_lines = []
    extracted_title = False
    with open(infile, 'r') as input, open(outfile, 'w') as output:
        for line in input:
            if not extracted_title:
                if line.startswith("# ")
                    # once we have the title, write the YAML block, then regurgitate the preceding bit of the file.
                    title = line[2:]
                    output.write("---")
                    output.write("layout: page")
                    output.write(f"title: {title}")
                    output.write("nav: false")
                    output.write("---")
                    output.writelines(preamble_lines)
                else:
                    preamble_lines.append(line)
            else:
                output.write(line) # copy over the file


    

if __name__ == "__main__":
    output_dir = ../builds/docs

    # Delete the output directory if it exists
    if os.path.isdir(output_dir):
        shutil.rmtree(itempath)
    # Create the output directory and the folder structure
    os.mkdir(output_dir)
    os.mkdir(os.path.join(output_dir, "parts"))
    for f in os.listdir("parts"):
        if os.path.isdir(os.path.join("parts",f)):
            os.mkdir(os.path.join(output_dir, "parts", f))
    os.mkdir(os.path.join(output_dir, "images"))

    for indir in ['.', 'parts'] + [os.path.join('parts',d) for d in os.listdir("parts") if os.path.isdir(os.path.join("parts", d))]:
        for f in os.listdir(indir):
            if f.endswith(".md"):
                process_markdown(os.path.join(indir, f), os.path.join(output_dir, indir, f))
                