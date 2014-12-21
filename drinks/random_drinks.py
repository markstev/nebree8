import random

from config.ingredients import INGREDIENTS_ORDERED
from drinks.recipe import Recipe, Ingredient, Oz


INGREDIENTS = {
  "agave syrup" : [0, 1, 0, 0],
  "angostura bitters" : [0, 0, 0, 1],
  "bourbon" : [1, 0, 0, 0],
  "coffee liqueur" : [0.5, 0.5, 0, 0],
  "coffee liqueur" : [0.5, 0.5, 0, 0],
  "creme de cacao" : [0.5, 0.5, 0, 0],
  "frangelico" : [0.5, 0.5, 0, 0],
  "gin" : [1, 0, 0, 0],
  "grenadine" : [0, 1, 0, 0],
  "kahlua" : [0.5, 0.5, 0, 0],
  "lemon juice" : [0, 0.5, 1, 0],
  "lime juice" : [0, 0, 1, 0],
  "lime juice" : [0, 0, 1, 0],
  "peppermint schnapps" : [1, 0, 0, 0],
  "pimms" : [0.5, 0.5, 0, 0],
  "rum" : [1, 0, 0, 0],
  "rye" : [1, 0, 0, 0],
  "simple syrup" : [0, 1, 0, 0],
  "stoli" : [1, 0, 0, 0],
  "tequila" : [1, 0, 0, 0],
  "triple sec" : [0.5, 0.5, 0, 0],
  "vodka" : [1, 0, 0, 0],
}


def RandomDrink(target_weight, drink_name = 'Random drink'):
  """Returns a Recipe."""
  FILTERED_INGREDIENTS = {}
  for i in INGREDIENTS_ORDERED:
    if i not in INGREDIENTS:
      print "No random config for", i
    else:
      FILTERED_INGREDIENTS[i] = INGREDIENTS[i]
  recipe = None
  total_weight = None
  attempts = 0
  while total_weight != target_weight:
    if not recipe or attempts > 100:
      recipe = Recipe(name = drink_name, ingredients=[])
      total_weight = [0, 0, 0, 0]
      attempts = 0
    ingredient = random.choice(FILTERED_INGREDIENTS.keys())
    min_gap = 1000
    for target, (x, y) in zip(target_weight,
                              zip(INGREDIENTS[ingredient], total_weight)):
      if x > 0:
        gap = (target - y) * 1.0 / x
        min_gap = min(gap, min_gap)
    if min_gap > 0:
      if min_gap > 1 and random.random() < 0.3:
        min_gap /= 2.0
      recipe.ingredients.append(Ingredient(Oz(min_gap), ingredient))
      total_weight = [x + y * min_gap for x, y in zip(total_weight, INGREDIENTS[ingredient])]
    attempts += 1
  return recipe


def RandomSourDrink():
    return RandomDrink([2, 1, 1, 0], 'Random Sour Drink')


def RandomSpirituousDrink():
    return RandomDrink([3, .7, 0, 1], 'Random Spirituous Drink')


if __name__ == "__main__":
    print RandomSourDrink()
    print RandomSpirituousDrink()
