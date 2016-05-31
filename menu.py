import glob, imp
from os.path import join, basename, splitext
from os import system

# For python dialog
import locale
from dialog import Dialog

def importPluginModulesIn(directory):
    modules = {}
    for path in glob.glob(join(directory, '[!_]*.py')):
        name, ext = splitext(basename(path))
        modules[name] = imp.load_source(name, path)
    return modules

def getPlugins():
    return importPluginModulesIn('stories')
    
def getStories():
    plugins = getPlugins()
    choices = []
    for i, plugin in enumerate(plugins):
        choices.append(("{0}".format(i + 1), "{0}".format(plugin)))
    return choices, plugins

def main():

    locale.setlocale(locale.LC_ALL, '')
    d = Dialog(dialog="dialog")
    
    #d.msgbox("Really lly Long Text Really Long Text Really Long Text ",
    #         height=20,
    #         width=100)
    
    stories, plugins = getStories()
    code, tags = d.menu("Select a Story",
                        choices= stories,
                        no_cancel=True,
                        ok_label="Start Story",
                        width=0,
                        menu_height=5)
    
    if code == d.DIALOG_ESC:
      exit()    
    
    for story in stories:
      if story[0] == tags:
        story_name = story[1]
        break
    
    #if save file is found then ask if they would like to continue or start a new game.
    
    new_story = plugins[story_name].Story()
    #import pdb; pdb.set_trace()
    # set to page one if new or a different page if continuing.
    new_story._StartStory(1)

if __name__ == "__main__":
    main()
