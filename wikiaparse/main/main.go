package main

import (
  "encoding/json"
  "flag"
  "fmt"
  "io/ioutil"

  wp "../"
)

var input = flag.String("input", "cocktails_pages_current.xml", "Path to cocktail wikia dump")
var output = flag.String("output", "cocktails.json", "Name of output json file.")

func main() {
  flag.Parse()
  w, err := wp.ReadWikiXML(*input)
  if err != nil {
    fmt.Printf("Error reading xml %v: %v\n", *input, err)
    return
  }
  fmt.Printf("%v wiki pages\n", len(w))
  rb, err := wp.ParseWiki(w)
  if err != nil {
    fmt.Printf("Failed to parse wiki: %v\n", err)
    return
  }
  fmt.Printf("%v recipes\n", len(rb))
  j, err := json.MarshalIndent(rb, "", "  ")
  if err != nil {
    fmt.Printf("Failed to marshall: %v\n", err)
    return
  }
  ioutil.WriteFile(*output, j, 0)
}
