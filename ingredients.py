#!/usr/bin/env python

import random
import sys

INGREDIENTS = {
  #"stoli" : [1, 0, 0, 0],
  "Angostura bitters" : [0, 0, 0, 1],
  #"water one" : [0, 1, 0, 0],
  "water two" : [0, 0, 1, 0],
  #"peppermint schnapps" : [1, 0, 0, 0],
  "creme de cacao" : [0.5, 0.5, 0, 0],
  "water end" : [0, 0, 1, 0],
  "water almost end" : [0, 1, 0, 0],
  "red" : [1, 0, 0, 0],
  "blue" : [0.5, 0.5, 0, 0],
  "yellow" : [0, 0, 1, 0],
  "pink" : [0, 1, 0, 0],
# "tequila" : [1, 0, 0, 0],
# "rye" : [1, 0, 0, 0],
# "bourbon" : [1, 0, 0, 0],
# "gin" : [1, 0, 0, 0],
# "vodka" : [1, 0, 0, 0],
# "rum" : [1, 0, 0, 0],
# "triple sec" : [0.5, 0.5, 0, 0],
# "coffee liqueur" : [0.5, 0.5, 0, 0],
# "lime juice" : [0, 0, 1, 0],
# "lemon juice" : [0, 0, 1, 0],
# "simple syrup" : [0, 1, 0, 0],
# "agave syrup" : [0, 1, 0, 0],
# "grenadine" : [0, 1, 0, 0],
# "Angostura bitters" : [0, 0, 0, 1],
# "mezcal" : [1, 0, 0, 0],
}


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
  "water end",
  "water almost end",
  "red",
  "blue",
  "yellow",
  "pink",
  "junk",
  "junk",
  "junk",
  "water two",
  "creme de cacao",
  "peppermint schnapps",
  "water one",
  "Angostura bitters",
  "stoli",
# "tequila",
# "rye",
# "bourbon",
# "gin",
# "vodka",
# "rum",
# "triple sec",
# "coffee liqueur",
# "lime juice",
# "lemon juice",
# "simple syrup",
# "agave syrup",
# "grenadine",
# "Angostura bitters",
# "mezcal"
)

def CreateRandomDrink(target_weight):
  """Returns a dict from ingredient to (volume, location)"""
  total_weight = [0, 0, 0, 0]
  ingredient_to_weight = {}
  attempts = 0
  while total_weight != target_weight:
    if attempts > 100:
      ingredient_to_weight = {}
      total_weight = [0, 0, 0, 0]
      attempts = 0
    ingredient = random.choice(INGREDIENTS.keys())
    ingredient_location = INGREDIENTS_ORDERED.index(ingredient)
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
    attempts += 1
  return ingredient_to_weight


def CreateDrinkWithWeights(list_of_ingredients):
  ingredient_to_weight = {}
  for ingredient, weight in list_of_ingredients:
    try:
      ingredient_to_weight[ingredient] = (weight,
          INGREDIENTS_ORDERED.index(ingredient))
    except:
      print "ERROR: %s is missing" % ingredient
  return ingredient_to_weight


def CreateDrink(list_of_ingredients):
  ingredient_weight_pairs = []
  for ingredient in list_of_ingredients:
    ingredient_weight_pairs.append((ingredient, 1.0))
  return CreateDrinkWithWeights(ingredient_weight_pairs)


def CreateTestDrink(n=3):
  #return CreateDrink(["agave syrup", "lemon juice", "grenadine"])
  #return CreateDrink(["mezcal", "tequila", "lemon juice"][:n])
  return CreateDrink(["mezcal", "agave syrup"][:n])

def CreateNamedDrink(name):
  name = name.lower()
  if name == "margarita":
    return CreateDrinkWithWeights([("tequila", 2.0), ("lime juice", 1.0), ("agave syrup", 1.0)])
  if name == "whiskey sour":
    return CreateDrinkWithWeights([("rye", 2.0), ("simple syrup", 1.0), ("lemon juice", 1.0)])
  if name == "gin gimlet":
    return CreateDrinkWithWeights([("gin", 2.0), ("lime juice", 0.5)])
  if name == "old fashioned":
    return CreateDrinkWithWeights([("bourbon", 4.0), ("simple syrup", 1.0), ("Angostura bitters", 1.0)])
  if name == "daquiri":
    return CreateDrinkWithWeights([("rum", 2.0), ("simple syrup", 1.0), ("lime juice", 1.0)])

def CreateTestDrink(n=4):
  #return CreateDrink(["agave syrup", "lemon juice", "grenadine"])
  return CreateDrink(["Angostura bitters", "mezcal", "lemon juice", "grenadine"][:n])


def PrimeRun():
  return {
    ingredient: (.1, i) for i, ingredient in enumerate(INGREDIENTS_ORDERED)}

def main(args):
  target_weight = [4, 1, 0, 1]  # Spiritous
  print CreateRandomDrink(target_weight)
  target_weight = [2, 1, 1, 0]  # Sour
  print CreateRandomDrink(target_weight)
  print CreateTestDrink()


if __name__ == "__main__":
  main(sys.argv)
