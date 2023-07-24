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
		comma-separated ticker symbol list (required)

	-s YYYYMMDD
		start date (inclusive) (required)

	-e YYYYMMDD
		end date (inclusive) (default: today)

The directory specified will be where output files are generated. If a target
file output alraedy exists, it will overwrite it in the case that the version
number is outdated, and take no action in the case that the version number is
the same.
*/
package main

import (
	"flag"
	"fmt"
	"os"
	"strings"
	"time"
	// "github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
)

func main() {
	//------------------------------------------------------------------------
	// Ensure Alpaca environment variables are set
	//------------------------------------------------------------------------

	alpacaEnvVars := []string{"APCA_API_KEY_ID", "APCA_API_SECRET_KEY"}

	// check if each environment variable is set
	for _, envVar := range alpacaEnvVars {
		if os.Getenv(envVar) == "" {
			fmt.Println("[ ERROR ] The environment variable", envVar, "is not set")
			return
		}
	}

	//------------------------------------------------------------------------
	// Parse flags
	//------------------------------------------------------------------------

	// define and parse flags
	startFlag := flag.String("s", "", "Start date (inclusive) (format: YYYYMMDD) (required)")
	endFlag := flag.String("e", "", "End date (inclusive) (format: YYYYMMDD) (default: today)")
	tickersFlag := flag.String("t", "", "Comma-separated list of ticker symbols (format: SYMBOL1,SYMBOL2) (required)")
	flag.Parse()

	// require start flag to be specified
	if *startFlag == "" {
		fmt.Println("[ ERROR ] Start date flag (-s) is missing")
		return
	}

	// require ticker symbol list to be specified
	if *tickersFlag == "" {
		fmt.Println("[ ERROR ] Ticker symbol list flag (-t) is missing")
		return
	}

	// get the start and end dates as time.Time objects
	start, err := time.Parse("20060102", *startFlag)
	if err != nil {
		fmt.Println("[ ERROR ] Error while parsing start date:", err)
		return
	}
	end, err := time.Parse("20060102", *endFlag)
	if err != nil {
		fmt.Println("[ ERROR ] Error while parsing end date:", err)
		return
	}

	// get the ticker symbols as a slice
	tickers := strings.Split(*tickersFlag, ",")

	// print parsed flags
	fmt.Println("Start date:", start)
	fmt.Println("End date:", end)
	fmt.Println("Tickers:", tickers)
}

// // Get Facebook bars
// func bars() {
// 	bars, err := marketdata.GetBars("META", marketdata.GetBarsRequest{
// 		TimeFrame: marketdata.OneDay,
// 		Start:     time.Date(2022, 6, 1, 0, 0, 0, 0, time.UTC),
// 		End:       time.Date(2022, 6, 22, 0, 0, 0, 0, time.UTC),
// 		AsOf:      "2022-06-10", // Leaving it empty yields the same results
// 	})
// 	if err != nil {
// 		panic(err)
// 	}
// 	fmt.Println("META bars:")
// 	for _, bar := range bars {
// 		fmt.Printf("%+v\n", bar)
// 	}
// }
