import random
import sys

from io_bank import Outputs

INGREDIENTS = {
  "tequila" : [1, 0, 0, 0],
  "rye" : [1, 0, 0, 0],
  "bourbon" : [1, 0, 0, 0],
  "gin" : [1, 0, 0, 0],
  "vodka" : [1, 0, 0, 0],
  "rum" : [1, 0, 0, 0],
  "triple sec" : [0.5, 0.5, 0, 0],
  "coffee liqueur" : [0.5, 0.5, 0, 0],
  "lime juice" : [0, 0, 1, 0],
  "lemon juice" : [0, 0, 1, 0],
  "simple syrup" : [0, 1, 0, 0],
  "agave syrup" : [0, 1, 0, 0],
  "grenadine" : [0, 1, 0, 0],
  "Angostura bitters" : [0, 0, 0, 1],
}


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
  "tequila",
  "rye",
  "bourbon",
  "gin",
  "vodka",
  "rum",
  "triple sec",
  "coffee liqueur",
  "lime juice",
  "lemon juice",
  "simple syrup",
  "agave syrup",
  "grenadine",
  "Angostura bitters"
)

def CreateRandomDrink(target_weight):
  """Returns a dict from ingredient to (volume, location)"""
  total_weight = [0, 0, 0, 0]
  ingredient_to_weight = {}
  while total_weight != target_weight:
    ingredient_location = random.randrange(len(INGREDIENTS_ORDERED))
    ingredient = INGREDIENTS_ORDERED[ingredient_location]
    min_gap = 1000
    for target, (x, y) in zip(target_weight,
                              zip(INGREDIENTS[ingredient], total_weight)):
      if x > 0:
        gap = (target - y) * 1.0 / x
        min_gap = min(gap, min_gap)
    if min_gap > 0:
      if min_gap > 1 and random.random() < 0.3:
        min_gap /= 2.0
      ingredient_to_weight[ingredient] = (min_gap, ingredient_location)
      total_weight = [x + y * min_gap for x, y in zip(total_weight, INGREDIENTS[ingredient])]
  return ingredient_to_weight


def CreateDrink(list_of_ingredients):
  ingredient_to_weight = {}
  for ingredient in list_of_ingredients:
    try:
      ingredient_to_weight[ingredient] = (1.0, INGREDIENTS_ORDERED.index(ingredient))
    except:
      print "ERROR: %s is missing" % ingredient
  return ingredient_to_weight


def CreateTestDrink():
  return CreateDrink(["agave syrup", "lemon juice", "grenadine"])


def main(args):
  target_weight = [4, 1, 0, 1]  # Spiritous
  print CreateRandomDrink(target_weight)
  target_weight = [2, 1, 1, 0]  # Sour
  print CreateRandomDrink(target_weight)
  print CreateTestDrink()


if __name__ == "__main__":
  main(sys.argv)
