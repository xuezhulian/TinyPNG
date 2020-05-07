# /usr/local/bin/python3 <<'EOF' - "$@"

import os
import sys
import re
import json
import shutil
import zipfile
import tinify

# limited to 500 uploads per month.
tinify.key = 'hCNfnSl0ZZ1QvBgxv7F7YrW9Fby8K70H'
# generate after unzip
auto_generate_imageset = True

assets_dir = '/Users/yuencong/workplace/iPad/TutorResource/Resource/TTImages.xcassets'

def rename(dirpath):
    # Rename files under dirpath without recursion
    global auto_generate_imageset
    if not os.path.isdir(dirpath):
        return
    # Determine whether the file names without suffix are consistent
    files = os.listdir(dirpath)
    filename_record = None
    for file in files:
        filename = re.sub('(@\d{1}x)?\.png', '', file)
        if filename_record == None:
            filename_record = filename
        elif filename_record != filename:
            auto_generate_imageset = False
            return
        else:
            pass

    # Change file names to dir name with suffix
    os.chdir(dirpath)
    dirname = dirpath.strip().split('/')[-1]
    for filename in filter(lambda x: is_valid_png(x), files):
        result = re.compile('((@\d{1}x)?\.png)').findall(filename)
        if not result:
            continue
        (suffix, _) = result[0]
        os.rename(filename, dirname + suffix)


def unzip(filepath):
    if not filepath.endswith('.zip'):
        return
    # Remove suffix .zip
    unzip_dir = filepath[0:-4]
    if os.path.isdir(unzip_dir):
        shutil.rmtree(unzip_dir)
    try:
        with zipfile.ZipFile(filepath, 'r') as file:
            file.extractall(unzip_dir)
            file.close()
            # Remove __MACOSX dir if it exists
            macos_dir = os.path.join(unzip_dir, '__MACOSX')
            if os.path.isdir(macos_dir):
                shutil.rmtree(macos_dir)
    except:
        pass
    return unzip_dir


def compress_dir(dirpath):
    if not os.path.isdir(dirpath):
        return
    # Compress all files under dirpath
    for root, _, files in os.walk(dirpath):
        for filename in filter(lambda x: is_valid_png(os.path.join(root, x)), files):
            compress_file(os.path.join(root, filename))


def compress_file(filepath):
    source = tinify.from_file(filepath)
    source.to_file(filepath)


def generate_imageset(dirpath):
    if not os.path.isdir(dirpath):
        return
    files = os.listdir(dirpath)
    dirname = dirpath.strip().split('/')[-1]
    imageset_dir = dirpath + '.imageset'
    if os.path.isdir(imageset_dir):
        shutil.rmtree(imageset_dir)
    os.rename(dirpath, imageset_dir)
    # Generate Contents.json
    contents = {}
    images = []
    for index in range(1, 4):
        image = {}
        filename = '%s@%dx.png' % (dirname, index)
        if index == 1:
            filename = dirname + '.png'
        if filename in files:
            image['filename'] = filename
        image['idiom'] = 'universal'
        image['scale'] = '%dx' % index
        images.append(image)
    contents['images'] = images
    contents['info'] = {"version" : 1,"author" : "xcode"}
    try:
        with open(os.path.join(imageset_dir, 'Contents.json'), 'w') as file:
            file.write(json.dumps(contents, indent=2))
            file.close()
    except:
        pass
    if os.path.isdir(assets_dir):
        dest_dir = os.path.join(assets_dir, dirname + '.imageset')
        if os.path.isdir(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.move(imageset_dir, assets_dir)


def is_valid_png(filepath):
    try:
        with open(filepath, 'rb') as file:
            file.seek(-2, 2)
            buf = file.read()
            file.close()
            return buf == b'\x60\x82'
    except:
        return False


if __name__ == '__main__':
    for input in sys.argv:
        if input.endswith('.zip'):
            unzip_dir = unzip(input)
            rename(unzip_dir)
            compress_dir(unzip_dir)
            if auto_generate_imageset:
                generate_imageset(unzip_dir)
        elif os.path.isdir(input):
            compress_dir(input)
        elif os.path.isfile(input) and is_valid_png(input):
            compress_file(input)