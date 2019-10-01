# Copy the documentation files to a folder, allowing for some processing.
from __future__ import print_function
import os
import sys
import shutil
import re

def process_markdown(infile, outfile):
    """Remove the title of a markdown file, and add Jekyll front matter"""
    preamble_lines = []
    images = set()
    extracted_title = False
    with open(infile, 'r', encoding='utf8') as input_file, open(outfile, 'w') as output_file:
        print(f"Opened {infile}...")
        for line in input_file:
            if not extracted_title:
                if line.startswith("# "):
                    # once we have the title, write the YAML block, then regurgitate the preceding bit of the file.
                    title = line.strip("# \n")
                    output_file.write("---\n")
                    output_file.write("layout: page\n")
                    output_file.write(f"title: {title}\n")
                    output_file.write("nav: false\n")
                    output_file.write("---\n")
                    output_file.writelines(preamble_lines)
                    extracted_title = True
                    print(f"Added header for '{title}' ({infile})")
                else:
                    preamble_lines.append(line)
            else:
                output_file.write(line) # copy over the file
            m = re.search(r"images/([^.]*\.(jpeg|jpg|JPG|JPEG|png|PNG))", line)
            if m:
                images.add(m.group(1))
    return images


    

if __name__ == "__main__":
    here = os.path.dirname(os.path.realpath(__file__))
    docs_dir = os.path.abspath(os.path.join(here, "docs"))
    parts_dir = os.path.abspath(os.path.join(docs_dir, "parts"))

    output_dir = os.path.abspath(os.path.join(here, "builds/docs"))

    # Delete the output directory if it exists
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    # Create the output directory and the folder structure
    os.mkdir(output_dir)
    os.mkdir(os.path.join(output_dir, "parts"))

    for f in os.listdir(parts_dir):
        if os.path.isdir(os.path.join(parts_dir, f)):
            os.mkdir(os.path.join(output_dir, "parts", f))
    os.mkdir(os.path.join(output_dir, "images"))

    images = set()
    # This should be recursive or something - but for now, I just enumerate the parts directory
    for input_dir in ['.', 'parts'] + [os.path.join('parts', d) for d in os.listdir(parts_dir) if os.path.isdir(os.path.join(parts_dir, d))]:
        input_dir_abs = os.path.join(docs_dir, input_dir)
        for f in os.listdir(os.path.join(docs_dir, input_dir)):
            if f.endswith(".md"):
                f_images = process_markdown(os.path.join(input_dir_abs, f), os.path.join(output_dir, input_dir, f))
                images.update(f_images)

    # copy over only the images that are actually used
    for f in images:
        shutil.copyfile(os.path.join(docs_dir, "images", f), os.path.join(output_dir, "images", f))
                