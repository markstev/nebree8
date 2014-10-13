package wikiaparse

import (
  "encoding/xml"
  "fmt"
  "io/ioutil"
  "strconv"
  "regexp"
  "strings"
)


type WikiPage struct {
  Title string `xml:"title"`
  Text string  `xml:"revision>text"`
}

type Wiki struct {
  Pages []*WikiPage `xml:"page"`
}

const (
  _ = iota
  OZ Unit = 1
  PART Unit = 2
  DROP Unit = 3
)


func ReadWikiXML(filename string) (map[string]string, error) {
  m := make(map[string]string)
  bytes, err := ioutil.ReadFile(filename)
  if err != nil { return nil, err }
  var wiki Wiki
  xml.Unmarshal(bytes, &wiki)
  noTitle := 0
  for _, page := range wiki.Pages {
    if len(page.Title) > 0 {
      if _, ok := m[page.Title]; ok {
        panic(fmt.Sprintf("Duplicate title %v", page.Title))
      }
      m[page.Title] = page.Text
    } else {
      noTitle++
    }
  }
  if noTitle > 0 {
    fmt.Printf("Warning: %v pages with no title", noTitle)
  }
  return m, err
}

type Unit int32

type Ingredient struct {
  Quantity float32
  Units Unit
  Name string
}

type Recipe struct {
  Name string
  Ingredients []Ingredient
  Notes string
  WikiSource string
}

var ingredientRegexp = regexp.MustCompile(`[*] ((\d+)\s*(oz)\s*[^\s])?(.*)$`)

func ParseIngredients(s string) ([]Ingredient, error) {
  if !strings.Contains(s, "ingredients") && !strings.Contains(s, "Ingredients") {
    return nil, nil
  }
  ignore := true
  seen_ingredient := false
  for _, line := range strings.Split(s, "\n") {
    if strings.Contains(line, "ingredients") || strings.Contains(line, "Ingredients") {
      ignore = false
      continue
    }
    if ignore { continue }
    if strings.HasPrefix(line, "* ") {
      seen_ingredient = true
      m := ingredientRegexp.FindStringSubmatch(line)
      if m == nil || len(m) != 4 { panic(fmt.Sprintf("m is weird, got %v for %v", m, line)) }
      var i Ingredient
      quantity := m[2]
      units := m[3]
      name := m[4]
      if len(quantity) > 0 {
        parsed, err := strconv.ParseFloat(quantity, 32)
        if err != nil { panic(err) }
        i.Quantity = float32(parsed)
      }
      if units == "oz" {
        i.Units = OZ
      } else if units == "drop" {
        i.Units = DROP
      } else if units == "part" {
        i.Units = PART
      } else {
        panic(fmt.Sprintf("Unexpected unit %v check regexp", units))
      }
      i.Name = name
    } else if seen_ingredient {
      break
    }
  }
  return []Ingredient{}, nil
}

func ParsePage(title, text string) (*Recipe, error) {
  i, err := ParseIngredients(text)
  if err != nil { return nil, err }
  if i == nil { return nil, nil }
  return &Recipe{
    Name: title,
    Ingredients: i,
    WikiSource: text,
  }, nil
}

func ParseWiki(w map[string]string) ([]*Recipe, error) {
  var rb []*Recipe
  for title, text := range w {
    r, err := ParsePage(title, text)
    if err != nil { return nil, err }
    if len(r.Ingredients) > 0 {
      rb = append(rb, r)
    }
  }
  return rb, nil
}
