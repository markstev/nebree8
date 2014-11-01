
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
        name = 'Margarita (with Triple Sec)',
        ingredients = [
            Ingredient(Oz(1.5), 'Tequila'),
            Ingredient(Oz(0.75), 'Lime'),
            Ingredient(Oz(0.5), 'Triple Sec')]),
    Recipe(
        name = 'Margarita (with Agave)',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Tequila'),
            Ingredient(Parts(1), 'Lime'),
            Ingredient(Parts(1), 'Agave')]),
    Recipe(
        name = 'Old Fashioned',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(4), 'Bourbon'),
            Ingredient(Parts(1), 'Simple'),
            Ingredient(Parts(1), 'Angostura')]),
    Recipe(
        name = 'Daquiri',
        total_oz = 2.75, #topped off with soda
        ingredients = [
            Ingredient(Parts(2), 'Rum'),
            Ingredient(Parts(1), 'Lime'),
            Ingredient(Parts(1), 'Simple')]),
    Recipe(
        name = 'Gin Gimlet', #top with tonic to be a G&T
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(1), 'Lime'),]),
    Recipe(
        name = 'Whiskey Sour',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Rye'),
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Simple')]),
    Recipe(
        name = 'Pimms Cup',
        total_oz = 4,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(3), 'Pimms'),
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Simple')]),
    Recipe(
        name = 'Kamikaze',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Vodka'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Triple Sec')]),
    Recipe(
        name = 'Lemon Drop',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Vodka'),
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Simple')]),
    Recipe(
        name = 'Long Island Ice Tea',
        total_oz = 5, #topped with splash of cola
        ingredients = [
            Ingredient(Parts(1), 'Vodka'),
            Ingredient(Parts(1), 'Gin'),
            Ingredient(Parts(1), 'Tequila'),
            Ingredient(Parts(1), 'Rum'),
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Lime'),
            Ingredient(Parts(1), 'Simple'),
            Ingredient(Parts(1), 'Triple Sec')]),
    Recipe(
        name = 'Tom Collins',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Gin'),
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Simple')]),
    Recipe(
        name = 'Virgin Lemonade',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Simple')]),
    Recipe(
        name = 'Other Virgin Thing',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Grenadine'),
            Ingredient(Parts(1), 'Lemon'),
            Ingredient(Parts(1), 'Lime')]),
]


if __name__ == "__main__":
    for r in db:
        print r
