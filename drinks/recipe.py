
class Recipe(object):
    def __init__(self, name, ingredients, total_oz = None):
        self.name = name
        self.total_oz = total_oz
        self.ingredients = ingredients
        has_parts = any(isinstance(i.qty, Parts) for i in ingredients)
        if has_parts:
            if total_oz is None:
                raise Exception("Set total_oz for drink %s" % name)
            total_parts = sum(getattr(i.qty, 'parts', 0) for i in ingredients)
            for i in self.ingredients:
                i.qty.total_oz = total_oz
                i.qty.total_parts = total_parts

    def __str__(self):
        return "%s\n  %s\n\n" % (self.name, "\n  ".join(map(str, self.ingredients)))

class Ingredient(object):
    def __init__(self, qty, name):
        assert issubclass(qty.__class__, Unit)
        self.qty = qty
        self.name = name
    def __str__(self):
        return "% 6s %s" % (self.qty, self.name)

class Unit(object):
    def __str__(self):
        return "%.2f oz" % self.oz


class Oz(Unit):
    def __init__(self, oz):
        self.oz = oz


class Parts(Unit):
    def __init__(self, parts):
        self.parts = parts
        self.total_oz = None
        self.total_parts = None
    @property
    def oz(self):
      return self.total_oz * (self.parts * 1./self.total_parts)


class Drops(Unit):
    def __init__(self, drops):
        self.drops = drops
    @property
    def oz(self):
        return 0
    def __str__(self):
        return "%i drops" % self.drops

