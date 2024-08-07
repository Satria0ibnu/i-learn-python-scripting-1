import os
import json
import shutil #allow to copy and overwrite operation
from subprocess import PIPE, run #allow to run terminal command for go code
import sys #get acces to command line arguments


GAME_DIR_PATTERN = "game"
GAME_CODE_EKSTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]



def find_all_game_paths(source):
    game_paths = []
    
    for root, dirs, files in os.walk(source):           #recursively walk at the current source path
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():   #if in the directory that currently walk in has "game"
                path = os.path.join(source, directory)       #assign the absolute path to currently walk in dir to variable
                game_paths.append(path)
        break
    
    return game_paths

def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:              
        _, dir_name = os.path.split(path)               #get the last directory from paths(absolute path) and assign to variable
        new_dir_name = dir_name.replace(to_strip, "")   #replace the string that need to remove with empty string and assign it
        new_names.append(new_dir_name)          

    return new_names



def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def copy_and_overwrite(source, destination):
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source,destination)

def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames" : game_dirs,
        "numberOfGames" : len(game_dirs)
    }
    
    with open(path, "w") as f:      # "w" for write, "r" for read
        json.dump(data, f)          # dumps is for string dump, dump is for file dump

def compile_game_code(path):
    code_file_name = None

    for root, dirs, files in os.walk(path):           #recursively walk at the current source path
        for file in files:
            if file.endswith(GAME_CODE_EKSTENSION):   
                code_file_name = file       #assign the file name to variable
                break

        break

    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

def run_command(command, path):
    cwd = os.getcwd()               #save the current directory
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result: ",  result)

    os.chdir(cwd)                   #back to the directory that we saved earlier



def main(source, target):
    cwd = os.getcwd()               #assign absolute current working directory to variable
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)

    game_paths = find_all_game_paths(source_path)               #return with all game absolute paths in array
    new_game_dirs = get_name_from_paths(game_paths,"_game")     #return with only game name directory without "_game"

    create_dir(target_path)

    #zip is to combine for example:
    # [1, 2 ,3]
    # ["a" , "b", "c"]
    # zip of that = [[1, "a"], [2, "b"], [3, "c"]]
    for src, dest in zip(game_paths, new_game_dirs):    #basically assign the array to variable but fancy
        dest_path = os.path.join(target_path, dest)     #try to get the absolute path for new game dirs / same like new_game_dirs but its absolute path
        copy_and_overwrite(src, dest_path) 
        compile_game_code(dest_path)             
    
    json_path = os.path.join(target_path, "data.json")
    make_json_metadata_file(json_path, new_game_dirs)



if __name__ == "__main__":          #code below only runs when this file is run directly
    args = sys.argv                 #get coommand line argument in array form

    if len(args) == 1:              #if no argument is given
        raise Exception("You should give an argument to the command.")
    
    if len(args) != 3:              #if argument not 3
        raise Exception("You must pass a source and target directory - only .")
    
    source, target = args[1:]       #assign second and third argument to variable

    main(source, target)
    

