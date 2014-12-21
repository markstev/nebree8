import csv

class DrinkRack(object):
  def __init__(self, csv_filename):
    # Read positions and drinks file.
    # Read drink alias file
    self.drinks_to_positions = {}
    with open(csv_filename, "r") as csv_file:
      reader = csv.reader(csv_file)
      for row in reader:
        self.drinks_to_positions[row[0]] = row[1]
    self.drinks_aliases = {}

  def IngredientToPosition(self, ingredient):
    """Returns a tuple of (ingredient, position). May alias ingredient."""
    if ingredient not in self.drinks_to_positions:
      for alias in self.drink_aliases.get(ingredient, ingredient) 
        if alias in self.drinks_to_positions:
          ingredient = alias
    if ingredient not in self.drinks_to_positions:
      return None
    return (ingredient, self.drinks_to_positions[ingredient])
