package main

import (
	"fmt"
	"strings"
)

func main() {
	tickers := []string{"AAPL", "TSLA"}
	body := fmt.Sprintf("Retrieve sentiment analysis for %s", strings.Join(tickers, ", "))
	fmt.Println(body)
}