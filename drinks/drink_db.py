import argparse
import pycurl
import re
import sys
import urllib
import cStringIO
 

class DrinkDatabase(object):
  def __init__(self):
    pass

  def _InitialSearch(self, drink_name):
    curl = pycurl.Curl()
    curl.setopt(curl.URL, "www.cocktaildb.com")
    curl.setopt(curl.FOLLOWLOCATION, 1)
    curl.setopt(curl.CONNECTTIMEOUT, 5)
    curl.setopt(curl.TIMEOUT, 8)
    form_data = {
        "simpleSearch": drink_name,
        "_action_submit_name": "Search recipes database",
        "__formID__": "recipes_name_search",
        }
    # url_opts = "&".join(["%s=%s" % (k, urllib.quote(v))
    #                      for k, v in form_data.iteritems()])
    url_opts = urllib.urlencode(form_data)
    curl.setopt(curl.POSTFIELDS, url_opts)
    curl.setopt(curl.POST, 1)
    curl.setopt(curl.COOKIEJAR, "cookie.txt")
    buf = cStringIO.StringIO()
    curl.setopt(curl.WRITEFUNCTION, buf.write)
    try:
      curl.perform()
    except pycurl.error, error:
      print error
    return buf.getvalue()

  def _ParseFirstPage(self, first_page_html):
    recipes = re.findall(
        "recipe_detail\?id=\d+\" title=\"click here for the recipe\">[\w ]+</a>",
        first_page_html)
    recipe_name_and_url = []
    for recipe in recipes:
      m = re.match("(recipe_detail\?id=\d+)\" .+recipe\">([\w ]+)</a>", recipe)
      recipe_name_and_url.append((m.group(2), m.group(1)))
    return recipe_name_and_url

  def _GetSecondPage(self, url_suffix):
    curl = pycurl.Curl()
    curl.setopt(curl.URL, "www.cocktaildb.com/%s" % url_suffix)
    curl.setopt(curl.FOLLOWLOCATION, 1)
    curl.setopt(curl.CONNECTTIMEOUT, 5)
    curl.setopt(curl.TIMEOUT, 8)
    buf = cStringIO.StringIO()
    curl.setopt(curl.WRITEFUNCTION, buf.write)
    try:
      curl.perform()
    except pycurl.error, error:
      print error
    return buf.getvalue()

  def _ParseSecondPage(self, second_page_html):
    ingredients_html = re.findall("\"recipeMeasure\">.*<a href=\"ingr_detail\?id=.*\">.*</a>",
                                  second_page_html)
    ingredients = []
    for ingredient in ingredients_html:
      ingredient = ingredient.lower()
      m = re.match("\"recipemeasure\">([^<]*)<a href=\"ingr_detail\?id=.*\">([^<]*)</a>", ingredient)
      if m and m.group(1) and m.group(2):
        ingredients.append((m.group(2), self.ParseVolume(m.group(1))))
      else:
        print "Could not parse: %s" % ingredient
    return ingredients

  def SearchForIngredients(self, drink_name):
    """Returns a list of ingredients, or an empty list for not found"""
    #TODO(Mark): alternates
    #TODO(Mark): directions
    recipe_urls = self._ParseFirstPage(self._InitialSearch(drink_name))
    for name, url in recipe_urls:
      if name.lower() == drink_name.lower():
        page = self._GetSecondPage(url)
        return self._ParseSecondPage(page)

  def ParseVolume(self, volume):
    volume = (volume
        .replace("ounce", "oz")
        .replace("ounces", "oz")
        .replace("tbsp", "tsp")
        .replace("dashes", "dash")
        .replace("wedges", "wedge")
        .replace(" of", "")
        .replace("float", ""))
    volume = volume.strip().rstrip()
    if " oz" in volume:
      units = "oz"
      volume = volume.replace(" oz", "")
    elif " tsp" in volume:
      units = "tsp"
      volume = volume.replace(" tsp", "")
    elif " dash" in volume:
      units = "dash"
      volume = volume.replace(" dash", "")
    elif " wedge" in volume:
      units = "wedge"
      volume = volume.replace(" wedge", "")
    else:
      units = "units"
    total = 0.0
    for portion in volume.split(" "):
      try:
        if "/" in portion:
          num, skip, denom = portion.partition("/")
          total += float(num) / float(denom)
        else:
          total += float(portion)
      except ValueError, e:
        print volume
        print portion
        raise e
    return (units, total)


def main(args):
  drink_db = DrinkDatabase()
  print drink_db.ParseVolume("1 oz")
  print drink_db.ParseVolume("1/4 oz")
  print drink_db.ParseVolume("2 1/2 oz")
  parser = argparse.ArgumentParser(description='Drink to look up')
  parser.add_argument('--drink', type=str, nargs="?", default="margarita",
                      help='Name of a drink')
  args = parser.parse_args()
  ingredients = drink_db.SearchForIngredients(args.drink)
  for ingredient in ingredients:
    print "Ingredient: %s; Volume: %f %s" % (ingredient[0], ingredient[1][1], ingredient[1][0])


if __name__ == "__main__":
  main(sys.argv)
