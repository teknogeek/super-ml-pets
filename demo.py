from sb3_contrib import MaskablePPO
from sapai_gym import SuperAutoPetsEnv
from sb3_contrib.common.maskable.utils import get_action_masks
from sapai import *
from sapai.shop import *
from smp.utils import opponent_generator
from demo_actions import SuperAutoPetsActionPrinter


interface = SuperAutoPetsActionPrinter()
action_dict = interface.get_action_dict()

# custom object relevant for supporting using model trained using a different python version than the one used now
custom_objects = {
    "learning_rate": 0.0,
    "lr_schedule": lambda _: 0.0,  # @TODO: Is this needed? Probably not for MaskablePPO
    "clip_range": lambda _: 0.0,
}

print("INITIALIZATION [self.run]: Loading Model")
# model = MaskablePPO.load("models/model_sap_gym_sb3_280822_finetuned_641057_steps.zip", custom_objects=custom_objects)
model = MaskablePPO.load("models/rl_model.zip", custom_objects=custom_objects)

print("INITIALIZATION [self.run]: Create SuperAutoPetsEnv Object")
env = SuperAutoPetsEnv(opponent_generator, valid_actions_only=True)
obs = env.reset()

def get_action_name(k: int) -> str:
    """
    translated action name from integer
    """
    name_val = list(SuperAutoPetsEnv.ACTION_BASE_NUM.items())
    assert k >= 0
    for (start_name, _), (end_name, end_val) in zip(name_val[:-1], name_val[1:]):
        if k < end_val:
            return start_name
    else:  # @TODO: this can't possibly be the correct placement, or?
        return end_name

def play(dry_run=True):
  # print(f"CV SYSTEM [self.run]: The detected Pets and Food in the Shop is : {shop}")
  # print("GAME ENGINE [self.run]: Set Environment Shop = detected Pets and Food")

  action_masks = get_action_masks(env)
  obs = env._encode_state()
  print("GAME ENGINE [self.run]: Get the best action to make for the given state from the loaded model")
  action, _states = model.predict(obs, action_masks=action_masks, deterministic=True)
  s = env._avail_actions()

  # converting to an integer to avoid causing unhashable a TypeError
  action = int(action)
  action_name = get_action_name(action)

  print(f"GAME ENGINE [self.run]: Current Team and Shop \n{s[action][0]}")
  print(f"GAME ENGINE [self.run]: Best Action = {action} {action_name}")
  print(f"GAME ENGINE [self.run]: Instruction given by the model = {s[action][1:]}")

  if env._is_valid_action(action):
    print("GAME ENGINE [self.run]: Action is valid")

    if action_name == 'buy_food':
      num_pets = 0
      num_food = 0
      for shop_slot in env.player.shop:
        if shop_slot.slot_type == "pet":
          num_pets += 1
        if shop_slot.slot_type == "food":
          num_food += 1
      print(f"GAME ENGINE [self.run]: Calls {action_name} with parameters {s[action][1:]}, {num_pets - num_food % 2}")
      if dry_run: return
      action_dict[action_name](s[action][1:], num_pets - num_food % 2)
    elif action_name == 'buy_team_food':  # same behaviour as for buy_food for single animal
      num_pets = 0
      num_food = 0
      for shop_slot in env.player.shop:
        if shop_slot.slot_type == "pet":
          num_pets += 1
        if shop_slot.slot_type == "food":
          num_food += 1
      print(f"GAME ENGINE [self.run]: Calls {action_name} with parameters {s[action][1:]}, {num_pets - num_food % 2}")
      if dry_run: return
      action_dict[action_name](s[action][1:], num_pets - num_food % 2)
    else:
      if action_name == 'roll':
        print(f"GAME ENGINE [self.run]: Calls {action_name} with no parameters")
        if dry_run: return
        action_dict[action_name]()
      else:
        print(f"GAME ENGINE [self.run]: Calls {action_name} with parameters {s[action][1:]}")
        if dry_run: return
        action_dict[action_name](s[action][1:])

    if dry_run: return

    print("GAME ENGINE [self.run]: Implements the action in the Environment\n\n\n")
    obs, reward, done, info = env.step(action)


def init(shop=None, team=None, health=None, turn=None, wins=None, gold=None):
  if shop is not None: env.player.shop = Shop(shop)
  if team is not None: env.player.team = Team(team)
  if health is not None: env.player.lives = health
  if turn is not None: env.player.turn = turn
  if wins is not None: env.player.wins = wins
  if gold is not None: env.player.gold = gold


# do_run(['mouse', 'mouse', 'mouse', 'apple'], health=5, dry_run=False)
# do_run(['mouse', 'mouse', 'apple'], dry_run=False)

# print(env.player)