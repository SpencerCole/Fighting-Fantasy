
import curses
import glob, imp
import os
import random
import sys

from os.path import join, basename, splitext
from os import system   
    
    
class BaseStory(object):

  def __init__(self):
    self.title = ''
    self.intro = ''
    self.base_page = Page()
    self.pages = {}
    self.character = {'points': 0}
    self.dice_specifics = []
    self.dice_roll = 0
    
    self.screen = curses.initscr()
    self.screen.keypad(1)
    self.screen.border(0)
    curses.noecho()
    curses.start_color()
    self.height, self.width = self.screen.getmaxyx()
    self.display_height = self.height - 3
      
  def do_action(self, action):
    if 'PointTo' in action:
      self.character['points'] = action['PointTo']
    if 'RollDice' in action:
      self._RollDice(action['RollDice'][0], action['RollDice'][1])
      
  def _CharPointTo(self, num):
    self.character['points'] = num
  
  def _RollDice(self, dice_num, dice_faces):
    dice_rolls = []
    total_rolls = 0
    
    for dice in range(1, dice_num):
      dice_rolls.append(random.randint(1, dice_faces))
    for roll in dice_rolls:
      total_rolls = total_rolls + roll
      
    self.dice_roll = total_rolls
    self.dice_specifics = dice_rolls
  
  def _StartStory(self, page):
    self.show_intro(self.intro)
    self.Open(page)                  
    
  def Open(self, page_num, old_choice=0, old_actions={}):
    if page_num == -1:
      sys.exit()
    
    # Do Action old action
    if old_actions and (old_choice in old_actions):
      for action in old_actions[old_choice]:
        self.do_action({action.keys()[0]: action.values()[0]})  
 
    opened_page = self.pages[page_num]

    # Display Text and Choices
    if opened_page.options and opened_page.text:
      page, choice = self.display_page(1, 1, opened_page.text, opened_page.options, 6)  
    
    self.Open(page, choice, opened_page.actions)
  
  def addWord(self, text, word, line_width=0):
    # ~ adds tab
    word = word.replace("#", " ")
    
    if "~" in word:
      new_word = "    " + word.strip("~")
    elif "$" in word:
      
      padding = (line_width - len(word) - 1)//2
      new_word = " " * padding + "{0}".format(word.strip("$")) + " " * padding
    else:
      new_word = word
    text += "{0} ".format(new_word)
    return text

  def formatLongString(self, text, padding):      
      line_width = self.width - (padding * 2)
      split_text = text.split()
      
      current_line = ""
      line_text = []
      for word in split_text:
        # ^ adds return carriage
        if len(current_line) + len(word) > line_width or "^" in word or "$" in word:
          if "^" in word and "$" in word:
            line_text.append(current_line)
            current_line = ""
          line_text.append(current_line)
          current_line = ""
          current_line = self.addWord(current_line, word.strip("^"), line_width)
        else:
          current_line = self.addWord(current_line, word)
        
        if word == split_text[-1]:
          line_text.append(current_line)
      
      return line_text

  def show_header(self, text):
    self.screen.addstr(0, ((self.width - len(text))/2), text)

  def show_intro(self, text):
    self.screen.clear()
    self.screen.border(0)
    self.screen.addstr(self.display_height//3, ((self.width - len(text))/2), text)
    self.screen.getch()

  def display_page(self, pos_x, pos_y, main_text, choices, padding):
    formatted_text = self.formatLongString(main_text, padding)

    text_length = len(formatted_text)
    top_scroll_line = pos_y - 1
    scroll_buffer = self.display_height / 2
    pos = 1
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlighted = curses.color_pair(1)
    normal = curses.A_NORMAL
    
    done = False
    while not done:
      self.screen.clear()
      self.screen.border(0)
      bottom_scroll_line = top_scroll_line + self.display_height
      text_to_display = formatted_text[top_scroll_line:bottom_scroll_line]
      
      choice_num = 1
      for num in range(0, self.display_height):
        if num <= len(text_to_display) - 1:
          self.screen.addstr(pos_y + num, pos_x + padding, text_to_display[num])
        else:
          if num >= len(text_to_display) + (scroll_buffer/2):
            if choice_num < len(choices) + 1:
              if pos == choice_num and top_scroll_line + self.display_height >= text_length + scroll_buffer:
                self.screen.addstr(pos_y + num, pos_x + padding, 
                              "- {1}".format(choice_num, 
                                             choices[choice_num].keys()[0]), highlighted)
              else:
                self.screen.addstr(pos_y + num, pos_x + padding, 
                              "- {1}".format(choice_num,
                                             choices[choice_num].keys()[0]), normal)      
              choice_num +=1
      choice_num = 1      
   
      percent = "{:.0%}".format((bottom_scroll_line - scroll_buffer)/ float(text_length))  
      self.screen.addstr(self.display_height + 1, self.width - (len(percent) + 1), percent)
      
      x = self.screen.getch()

      if x == ord('\n'):
        if top_scroll_line + self.display_height >= text_length + scroll_buffer:
          done = True
          return choices[pos].values()[0], pos
        
      elif x == 258: #down arrow
        if top_scroll_line + self.display_height < text_length + scroll_buffer:
          if (top_scroll_line + self.display_height + 
              (self.display_height//4) <= text_length + scroll_buffer):
            top_scroll_line += (self.display_height//4)
          else:
            top_scroll_line = text_length + scroll_buffer - self.display_height
        elif pos < len(choices):
          pos += 1
            
      elif x == 259: #up arrow
 
        if top_scroll_line > pos_y - 1 and pos == 1:
          if top_scroll_line - (self.display_height//4) >= pos_y:
            top_scroll_line -= (self.display_height//4)
          else:
            top_scroll_line = pos_y - 1
        elif pos > 1:
          pos += -1

      self.screen.refresh()

   
class Page(object):
    
    
  def __init__(self, text='', options={}, actions={}):
    self.actions = actions
    self.text = text
    self.options = options
