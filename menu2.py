import os
import curses
import glob, imp
from os.path import join, basename, splitext
from os import system

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
    choices = {}
    for i, plugin in enumerate(plugins):
        choices[i + 1] = "{0}".format(plugin)
    return choices, plugins

def addWord(text, word):
    # ~ adds tab
    if "~" in word:
      new_word = "    " + word.strip("~")
    else:
      new_word = word
    text += "{0} ".format(new_word)
    return text

def formatLongString(text, padding):
    height, width = screen.getmaxyx()
    
    line_width = float(width - (padding * 2))
    split_text = text.split()
    
    current_line = ""
    line_text = []
    for word in split_text:
      # ^ adds return carriage
      if len(current_line) + len(word) > line_width or "^" in word:
        line_text.append(current_line)
        current_line = ""
        current_line = addWord(current_line, word.strip("^"))
      else:
        current_line = addWord(current_line, word)
      if word == split_text[-1]:
        line_text.append(current_line)
    return line_text

def show_header(text):
    height, width = screen.getmaxyx()
    screen.addstr(0, ((width - len(text))/2), text)

def display_page(pos_x, pos_y, main_text, choices, plugins, padding):
  height, width = screen.getmaxyx()
  formatted_text = formatLongString(main_text, padding)
  
  display_height = height - 3
  text_length = len(formatted_text)
  top_scroll_line = pos_y - 1
  scroll_buffer = display_height / 2
  pos = 1
  curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
  highlighted = curses.color_pair(1)
  normal = curses.A_NORMAL
  
  done = False
  while not done:
    screen.clear()
    screen.border(0)
    show_header("Welcome")
    bottom_scroll_line = top_scroll_line + display_height
    text_to_display = formatted_text[top_scroll_line:bottom_scroll_line]
    choice_num = 1
    for num in range(0, display_height):
      if num <= len(text_to_display) - 1:
        screen.addstr(pos_y + num, pos_x + padding, text_to_display[num])
      else:
        if num >= len(text_to_display) + (scroll_buffer/2):
          if choice_num < len(choices) + 1:
            if pos == choice_num:
              screen.addstr(pos_y + num, pos_x + padding, 
                            "- {1}".format(choice_num, 
                                           choices[choice_num]), highlighted)
            else:
              screen.addstr(pos_y + num, pos_x + padding, 
                            "- {1}".format(choice_num,
                                           choices[choice_num]), normal)      
            choice_num +=1

    choice_num = 1
    
    x = screen.getch()

    if x == ord('\n'):
      if top_scroll_line + display_height >= text_length + scroll_buffer:
        done = True
        return choices[pos]
      
    elif x == 258:
      if top_scroll_line + display_height >= text_length + scroll_buffer:
        if pos < len(choices):
          pos += 1
        else:
          pos = 1
      
      elif top_scroll_line + display_height < text_length + scroll_buffer:
        if top_scroll_line + display_height + (display_height//3) <= text_length + scroll_buffer:
          top_scroll_line += (display_height//3)
        else:
          top_scroll_line = text_length + scroll_buffer - display_height
          
    elif x == 259:
      if bottom_scroll_line >= text_length + scroll_buffer:
        if pos > 1:
          pos += -1
        else:
          pos = len(choices)      
      
      elif top_scroll_line > pos_y:
        if top_scroll_line - (display_height//3) >= pos_y:
          top_scroll_line -= (display_height//3)
        else:
          top_scroll_line = pos_y

    screen.refresh()
      
  return choice_page

def main():
  intro_text = "^ ^Please select a story to play:"
  
  choices, plugins = getStories()
  choice = display_page(1, 1, intro_text, choices, plugins, 6)
  
  new_story = plugins[choice].Story()
  new_story._StartStory(1)

if __name__ == "__main__":
  try:
    os.system('setterm -cursor off')
    screen = curses.initscr()
    screen.keypad(1)
    curses.noecho()
    screen.border(0)
    curses.start_color()
    main()
  finally:
    # on exit
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
    os.system('setterm -cursor on')
