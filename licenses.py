
import json
import os
import re
import sys
import getopt

# python3 /Users/Stahl/Programmierung/Anwendungen/Python/license-reader/licenses.py --in /Users/Stahl/Programmierung/Projekte/ReactNative/webweaver --out /Users/Stahl/Programmierung/Projekte/ReactNative/webweaver/src/utils/licenses.json

def main(argv):
    inpath = os.getcwd()
    outpath = os.path.join(inpath, 'licenses.json')
    opts, args = getopt.getopt(argv, 'h', ["in=", "out=", "help"])
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: licenses.py --in /somedir/ --out /someother/license.json')
            sys.exit()        
        elif opt in ("-i", "--in"):
            inpath = arg
        elif opt in ("-o", "--out"):
            outpath = arg

    readLicenses(inpath, outpath)

def getLicenseFile(files):
    names = ['license', 'licence']
    for file in files:
        for name in names:
            if name in file.lower():
                return file
    return None        
    

def readPackageJson(path):
    jsonpath = os.path.join(path, 'package.json')
    with open(jsonpath) as file:
        try: 
            package = json.load(file)
        except ValueError:  
            print('Decoding JSON has failed: ' + path)
            return None
        if 'name' not in package:
            return None
        info = {
            'path': path,
            'name': package['name']
        }
        if 'version' in package:
            info['version'] = package['version']
        if 'license' in package:
            info['license'] = package['license']
        if 'author' in package:
            if isinstance(package["author"], str):
                author = package["author"]
                email = re.findall('<(.*?)>', author)
                url = re.findall('\((.*?)\)', author)
                if len(email) > 0:
                    info["authorEmail"] = email[0]
                    author = author.partition(' <')[0]
                if len(url) > 0:
                    info["authorUrl"] = url[0]
                    author = author.partition(' (')[0]                    
                info["authorName"] = author
            elif isinstance(package["author"], dict):
                if "name" in package["author"]:
                    info["authorName"] = package["author"]["name"]
                if "email" in package["author"]:
                    info["authorEmail"] = package["author"]["email"]
                if "url" in package["author"]:
                    info["authorUrl"] = package["author"]["url"]
        repoUrl = ''
        dir = ''
        if 'repository' in package:
            if isinstance(package['repository'], str):
                repoUrl = package['repository']
            else:
                if 'url' in package['repository']:
                    repoUrl = package['repository']['url']
                if 'directory' in package['repository']:
                    dir = '/' + package['repository']['directory']
        repoUrl = repoUrl.replace('git+ssh://git@', 'git://')
        repoUrl = repoUrl.replace('git+https://github.com', 'https://github.com')
        repoUrl = repoUrl.replace('git://github.com', 'https://github.com')
        repoUrl = repoUrl.replace('git@github.com:', 'https://github.com/')
        repoUrl = re.sub('\.git$', '', repoUrl)
        if 'http' not in repoUrl:
            repoUrl = 'https://github.com/' + repoUrl
        info['repository'] = repoUrl
        parts = repoUrl.rsplit('/', 2)
        user = parts[1]
        info['user'] = user
        info['avatar'] = "http://github.com/" + user + ".png"
        if 'url' not in info:
            info['url'] = "http://github.com/" + user
        return info


def readLicenses(path, output):
    packages = []

    rootjson = os.path.join(path, 'package.json')
    with open(rootjson) as file:
        dependencies = list(json.load(file)['dependencies'].keys())

    current = os.path.join(path, 'node_modules')
    if os.path.isdir(current):
        for root, dirs, files in os.walk(current):
            if 'package.json' in files:
                #print(root)
                package = readPackageJson(root)
                if package is not None:
                    if package['name'] in dependencies:
                        licenseFile = getLicenseFile(files)
                        if licenseFile == None:
                            pass
                            #print('no license file in ' + root)
                        else:
                            with open(os.path.join(root, licenseFile), 'r') as file:
                                text = file.read()
                                package['licenseText'] = text
                        packages.append(package)

    packages = sorted(packages, key=lambda k: k['user'].lower())

    with open(output, 'w') as file:
        json.dump(packages, file)


if __name__ == "__main__":
   main(sys.argv[1:])
   