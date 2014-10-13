
class Recipe(object):
    def __init__(self, name, ingredients, total_oz = None):
        self.name = name
        self.total_oz = total_oz
        self.ingredients = ingredients
        has_parts = any(isinstance(i.qty, Parts) for i in ingredients)
        if has_parts:
            if total_oz is None:
                raise Exception("Set total_oz for drink %s" % name)
            total_parts = sum(i.qty.q for i in ingredients)
            print "total_parts", total_parts
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
        return "??"

class Oz(Unit):
    def __init__(self, q):
        self.q = q
    def __str__(self):
        return "%.2f oz" % self.q


class Parts(Unit):
    def __init__(self, q):
        self.q = q
        self.total_oz = None
        self.total_parts = None
    def __str__(self):
        return "%.2f oz" % (self.total_oz * (self.q * 1./self.total_parts))


db = [
    Recipe(
        name = 'Margarita',
        ingredients = [
            Ingredient(Oz(1.5), 'Tequila'),
            Ingredient(Oz(0.75), 'Lime Juice'),
            Ingredient(Oz(0.5), 'Triple Sec')]),
    Recipe(
        name = 'Margarita',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Tequila'),
            Ingredient(Parts(3), 'Lime Juice'),
            Ingredient(Parts(2), 'Triple Sec')]),
]

for r in db:
    print r
