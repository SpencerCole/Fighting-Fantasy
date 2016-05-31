import sys
import random
from dialog import Dialog

class BaseStory(object):

  def __init__(self):
    self.title = ''
    self.intro = ''
    self.base_page = Page()
    self.pages = {}
    self.character = {
                      'points': 0
                     }
    self.dice_specifics = []
    self.dice_roll = 0
    self.d = Dialog(dialog="dialog")
      
  def do_action(self, action):
    if 'PointTo' in action:
      self.character['points'] = action['PointTo']
    if 'RollDice' in action:
      self._RollDice(action['RollDice'][0], action['RollDice'][1])
    if 'Quit' in action:
      #import pdb; pdb.set_trace
      # Go to a graceful page (save and close, etc...)
      sys.exit(0)
      
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
    self.d.msgbox(self.intro,
                  height=0,
                  width=0)
    self.Open(page)                  
    
  def Open(self, page_num, old_choice=0, old_actions={}):
    
    opened_page = self.pages[page_num]
    choice = None 
    # Do Action old action
    if old_actions and (old_choice in old_actions):
      for action in old_actions[old_choice]:
        self.do_action({action.keys()[0]: action.values()[0]})
    
     # Show Page Text
    if opened_page.text:
      self.d.msgbox(opened_page.text,
                    height=0,
                    width=0)
    
    # Display Choices
    if opened_page.options:
      choices = []
      for key, value in opened_page.options.iteritems():
        choices.append(("{0}".format(key), "{0}".format(value.keys()[0])))
      code, choice = self.d.menu(" ",
                               choices=choices,
                               no_cancel=True,
                               ok_label="Choose",
                               width=0,
                               menu_height=4)
    
      if code == self.d.DIALOG_ESC:
        sys.exit(0)    
    
    if choice:
    # I dont think I could have made this more confusing.
      self.Open(opened_page.options[int(choice)].values()[0],
                int(choice),
                opened_page.actions)
   
    
   
class Page(object):
  #images? text art?
  def __init__(self, text='', options={}, actions={}):
    self.actions = actions
    self.text = text
    self.options = options

