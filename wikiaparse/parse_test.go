package wikiaparse

import "testing"

func IngredientsEqual(t *testing.T, actual, expected []Ingredient) {
  if len(actual) != len(expected) {
    t.Errorf("number of ingredients not equal.\nActual: %v\nExpected: %v", actual, expected)
    return
  }
  for i := range actual {
    if actual[i] != expected[i] {
      t.Errorf("Ingredients %v and %v do not match.", i, actual[i], expected[i])
    }
  }
}

func TestParseMargarita(t *testing.T) {
  expected := []Ingredient{
    {Quantity: 2, Units: OZ, Name: "tequila"},
    {Quantity: 1, Units: OZ, Name: "cointreau"},
    {Quantity: 1, Units: OZ, Name: "lime juice"},
  }
  parsed, err := ParseIngredients(
  `== Description ==
[[Image:450px-Margarita.jpg|150px|right|Classic Margarita]]
The '''margarita''' is the best known of all [[:Category:Tequila recipes|tequila-based cocktails]]. There are three main ingredients in a margarita: Tequila, Triple Sec ([[Orange liqueur]], and lime juice. 

* Source: [http://en.wikibooks.org/wiki/Bartending/Cocktails/Margarita Margarita] from the Wikibooks Bartending Guide—original source of recipe, licensed under the GNU Free Documentation License

==Ingredients==
* 2 oz [[tequila]]
* 1 oz orange-flavored liqueur ([[Cointreau]] or [[Triple sec]])
* 1 oz fresh [[lime juice]]
* [[salt]]

== Directions ==
# Rub the [[Rimming|rim]] of a cocktail glass with a lime wedge.
# Dip in salt.
# [[Shake]] all ingredients with ice.
# [[Strain]] into a cocktail glass.
# [[Garnish]] with a [[lime wedge]] or slice.

== Alternate Recipe ==
The traditional recipe above is best (three parts Tequila, two parts Triple Sec and one part lime juice) but if you don't have lime juice but you do have [[Bar mix|sweet and sour mix]] you can try this one out instead.  One oz. Tequila, 0.5 to 1 oz Triple Sec, 2 oz. sweet and sour.

__NOTOC__
__NOEDITSECTION__
[[Category:Cointreau recipes]]
[[Category:Triple sec recipes]]
[[Category:Lime juice recipes]]
[[Category:Tequila recipes]]
[[Category:Shaken Drinks]]`)
  if err != nil { t.Errorf("Parse error: %v\n", err) }
  IngredientsEqual(t, parsed, expected)
}
