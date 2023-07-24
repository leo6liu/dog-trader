/*
DataGeneration creates files with stock bar data and technical indicators.

Output file names will be in the format: SYMBOL/SYMBOL_YYYYMMDD_vXXX.csv
(vXXX indicates the output file version number). File versions are used to 
track column content, data format, and indicator calculation metholodogy 
changes. Version change information is tracked in the README file.

Current output file version: v000

Usage:

	generation [flags] [directory]

The flags are:

	-t SYMBOL1,SYMBOL2
		comma-separated ticker symbol list

	-s YYYYMMDD
		start date (inclusive)

	-e YYYYMMDD
		end date (inclusive)

The directory specified will be where output files are generated. If a target 
file output alraedy exists, it will overwrite it in the case that the version 
number is outdated, and take no action in the case that the version number is 
the same.
*/
package main

import (
	"fmt"
	"time"

	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
)

func main() {
	bars()
}

// Get Facebook bars
func bars() {
	bars, err := marketdata.GetBars("META", marketdata.GetBarsRequest{
		TimeFrame: marketdata.OneDay,
		Start:     time.Date(2022, 6, 1, 0, 0, 0, 0, time.UTC),
		End:       time.Date(2022, 6, 22, 0, 0, 0, 0, time.UTC),
		AsOf:      "2022-06-10", // Leaving it empty yields the same results
	})
	if err != nil {
		panic(err)
	}
	fmt.Println("META bars:")
	for _, bar := range bars {
		fmt.Printf("%+v\n", bar)
	}
}
