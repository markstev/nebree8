#!/usr/bin/env python
from recipe import Recipe, Ingredient, Oz, Parts, Drops

db = [
    Recipe(
        name = 'Margarita',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Tequila'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Agave Syrup')]),
    Recipe(
        name = 'Old Fashioned',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(4), 'Bourbon'),
            Ingredient(Parts(1), 'Simple Syrup'),
            Ingredient(Drops(1), 'Angostura Bitters')]),
    Recipe(
        name = 'Daquiri',
        total_oz = 2.75, #topped off with soda
        ingredients = [
            Ingredient(Parts(2), 'Rum'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Gin Gimlet', #top with tonic to be a G&T
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(1), 'Lime Juice'),]),
    Recipe(
        name = 'Whiskey Sour',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Rye'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Pimms Cup',
        total_oz = 4,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(3), 'Pimms'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
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
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Long Island Ice Tea',
        total_oz = 5, #topped with splash of cola
        ingredients = [
            Ingredient(Parts(1), 'Vodka'),
            Ingredient(Parts(1), 'Gin'),
            Ingredient(Parts(1), 'Tequila'),
            Ingredient(Parts(1), 'Rum'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Simple Syrup'),
            Ingredient(Parts(1), 'Triple Sec')]),
    Recipe(
        name = 'Tom Collins',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Gin'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Virgin Lemonade',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Grenadine Punch',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Grenadine'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Lime Juice')]),
]


if __name__ == "__main__":
    for r in db:
        print r
