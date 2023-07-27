/*
DataGeneration creates files with stock bar data and technical indicators.

This program uses relative file paths. It is intended to be run from the
directory: dog-trader/data/generation

Output file names will be in the format: ../tickers/SYMBOL/SYMBOL_YYYYMMDD_vXXX.csv
(vXXX indicates the output file version number). File versions are used to
track column content, data format, and indicator calculation metholodogy
changes. Version change information is tracked in the README file.

Output files will contain data from 9:00 AM to 4:00PM EST.

Current output file version: v000

Usage:

	generation [flags]

The flags are:

	-t SYMBOL1,SYMBOL2
		comma-separated ticker symbol list (required)

	-s YYYYMMDD
		start date (inclusive) (required)

	-e YYYYMMDD
		end date (inclusive) (default: today)
*/
package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/alpacahq/alpaca-trade-api-go/v3/marketdata"
)

// define constants
const OUTPUT_VERSION string = "v000"
const EMA12_SMOOTHING float64 = 2
const EMA26_SMOOTHING float64 = 2
const MACDS_SMOOTHING float64 = 2
const RSI_PERIOD int = 14

func main() {
	//-------------------------------------------------------------------------
	// Ensure Alpaca environment variables are set
	//-------------------------------------------------------------------------

	checkAlpacaEnvVars()

	//-------------------------------------------------------------------------
	// Parse flags for start, end, and tickers
	//-------------------------------------------------------------------------

	start, end, tickers := parseFlags()

	// print parsed flags
	fmt.Println("[ INFO ] Start date:", start)
	fmt.Println("[ INFO ] End date:", end)
	fmt.Println("[ INFO ] Tickers:", tickers)

	//-------------------------------------------------------------------------
	// data generation loop
	//-------------------------------------------------------------------------

	holidays := getHolidays("../../properties/market-holidays.json")

	newYork, _ := time.LoadLocation("America/New_York")

	fmt.Println("[ INFO ] --------------------------------------------------")
	fmt.Println("[ INFO ] Stating data generation loop...")

	for current := start; !current.After(end); current = current.AddDate(0, 0, 1) {
		// skip weekends and holidays (including early closes)
		if isWeekend(current) || isHoliday(current, holidays) {
			continue
		}

		startTime := time.Date(current.Year(), current.Month(), current.Day(), 8, 0, 0, 0, newYork) // 8:00 AM
		endTime := time.Date(current.Year(), current.Month(), current.Day(), 16, 0, 0, 0, newYork)  // 4:00 PM

		for _, symbol := range tickers {
			// define output directory and filename
			outputDirectory := fmt.Sprintf("../tickers/%s", symbol)
			outputFilename := fmt.Sprintf("%s_%d%02d%02d_%s.csv", symbol, current.Year(), current.Month(), current.Day(), OUTPUT_VERSION)

			fmt.Println("[ INFO ] Generating file:", outputFilename)

			// get minute bars for day and ticker from Alpaca
			bars, err := marketdata.GetBars(symbol, marketdata.GetBarsRequest{
				TimeFrame: marketdata.OneMin,
				Start:     startTime,
				End:       endTime,
			})
			panicOnNil(err)

			// fill in bars that do not exist
			for i := 0; i < len(bars); i++ {
				if i == 0 {
					// if first minute is not 8:00 AM, then exit
					if !bars[i].Timestamp.Equal(startTime) {
						fmt.Println("[ ERROR ] First minute bar is not 8:00 AM")
						os.Exit(1)
					}

					// skip 8:00 AM minute
					continue
				}

				// check for non-sequantial minute bars
				if !bars[i].Timestamp.Equal(bars[i-1].Timestamp.Add(time.Minute)) {
					bars = insertBar(bars, i, marketdata.Bar{
						Timestamp:  bars[i-1].Timestamp.Add(time.Minute),
						Open:       bars[i-1].Close,
						High:       bars[i-1].Close,
						Low:        bars[i-1].Close,
						Close:      bars[i-1].Close,
						Volume:     0,
						TradeCount: 0,
						VWAP:       0,
					})
				}
			}

			// create output file and writer
			err = os.MkdirAll(outputDirectory, 0755)
			panicOnNil(err)
			file, err := os.Create(fmt.Sprintf("%s/%s", outputDirectory, outputFilename))
			panicOnNil(err)
			writer := csv.NewWriter(file)
			defer writer.Flush()

			// write header
			header := []string{
				"time",
				"open",
				"high",
				"low",
				"close",
				"volume",
				"VWAP",
				"5SMA",
				"8SMA",
				"13SMA",
				"12EMA",
				"26EMA",
				"MACD",
				"MACDS",
				"RSI",
			}
			writer.Write(header)

			// create and write rows
			var last12EMA float64
			var last26EMA float64
			var macdLine []float64
			var lastMACDS float64
			var cumPV float64 = 0       // cumulative price-volume for calculating VWAP
			var cumVol float64 = 0      // cumulative volume for calculating VWAP
			var lastAvgGain float64 = 0 // for RSI
			var lastAvgLoss float64 = 0 // for RSI
			for i, bar := range bars {
				// update VWAP
				cumPV = cumPV + ((bar.High+bar.Low+bar.Close)/3)*float64(bar.Volume)
				cumVol = cumVol + float64(bar.Volume)

				// skip bars prior to 8:30 AM
				if bar.Timestamp.Before(time.Date(current.Year(), current.Month(), current.Day(), 8, 30, 0, 0, newYork)) {
					continue
				}

				// initialize EMAs, MACD, and RSI at 8:30 AM
				if bar.Timestamp.Equal(time.Date(current.Year(), current.Month(), current.Day(), 8, 30, 0, 0, newYork)) {
					last12EMA = calcBarCloseSMA(bars[i-11 : i+1])
					last26EMA = calcBarCloseSMA(bars[i-25 : i+1])
					macdLine = append(macdLine, last12EMA-last26EMA)

					// calculate average gain for RSI
					lastAvgGain = calcFirstAvgGainLoss(bars[i-RSI_PERIOD:i+1], true)
					lastAvgLoss = calcFirstAvgGainLoss(bars[i-RSI_PERIOD:i+1], false)

					continue
				}

				// calculate avg. gain/loss
				lastAvgGain = calcAvgGainLoss(RSI_PERIOD, lastAvgGain, bars[i-1].Close, bar.Close, true)
				lastAvgLoss = calcAvgGainLoss(RSI_PERIOD, lastAvgLoss, bars[i-1].Close, bar.Close, false)

				// calcualte EMAs and MACD from 8:31 AM - 8:37 AM (inclusive)
				if bar.Timestamp.After(time.Date(current.Year(), current.Month(), current.Day(), 8, 30, 0, 0, newYork)) &&
					bar.Timestamp.Before(time.Date(current.Year(), current.Month(), current.Day(), 8, 38, 0, 0, newYork)) {
					last12EMA = calcEMA(bar.Close, last12EMA, 12, EMA12_SMOOTHING)
					last26EMA = calcEMA(bar.Close, last26EMA, 26, EMA26_SMOOTHING)
					macdLine = append(macdLine, last12EMA-last26EMA)
					continue
				}

				// initialize MACDS at 8:38 (uses 9-period MACD)
				if bar.Timestamp.Equal(time.Date(current.Year(), current.Month(), current.Day(), 8, 38, 0, 0, newYork)) {
					last12EMA = calcEMA(bar.Close, last12EMA, 12, EMA12_SMOOTHING)
					last26EMA = calcEMA(bar.Close, last26EMA, 26, EMA26_SMOOTHING)
					macdLine = append(macdLine, last12EMA-last26EMA)
					lastMACDS = calcSMA(macdLine[len(macdLine)-9:])
					continue
				}

				// calcualte EMAs and MACDS from 8:39 AM - 8:59 AM (inclusive)
				if bar.Timestamp.After(time.Date(current.Year(), current.Month(), current.Day(), 8, 38, 0, 0, newYork)) &&
					bar.Timestamp.Before(time.Date(current.Year(), current.Month(), current.Day(), 9, 0, 0, 0, newYork)) {
					last12EMA = calcEMA(bar.Close, last12EMA, 12, EMA12_SMOOTHING)
					last26EMA = calcEMA(bar.Close, last26EMA, 26, EMA26_SMOOTHING)
					lastMACDS = calcEMA(last12EMA-last26EMA, lastMACDS, 9, MACDS_SMOOTHING)
					continue
				}

				// reset VWAP at 9:30
				if bar.Timestamp.Equal(time.Date(current.Year(), current.Month(), current.Day(), 9, 30, 0, 0, newYork)) {
					cumPV = ((bar.High + bar.Low + bar.Close) / 3) * float64(bar.Volume)
					cumVol = float64(bar.Volume)
				}

				// get time
				time := fmt.Sprintf("%02d:%02d", bar.Timestamp.In(newYork).Hour(), bar.Timestamp.In(newYork).Minute())

				// get OHLC
				open := fmt.Sprintf("%.3f", bar.Open)
				high := fmt.Sprintf("%.3f", bar.High)
				low := fmt.Sprintf("%.3f", bar.Low)
				close := fmt.Sprintf("%.3f", bar.Close)

				// get volume
				volume := fmt.Sprintf("%d", bar.Volume)

				// calculate VWAP
				vwap := fmt.Sprintf("%.3f", cumPV/cumVol)

				// calculate SMAs
				sma5 := fmt.Sprintf("%.3f", calcBarCloseSMA(bars[i-4:i+1]))
				sma8 := fmt.Sprintf("%.3f", calcBarCloseSMA(bars[i-7:i+1]))
				sma13 := fmt.Sprintf("%.3f", calcBarCloseSMA(bars[i-12:i+1]))

				// calculate EMAs
				last12EMA = calcEMA(bar.Close, last12EMA, 12, 2)
				ema12 := fmt.Sprintf("%.3f", last12EMA)
				last26EMA = calcEMA(bar.Close, last26EMA, 26, 2)
				ema26 := fmt.Sprintf("%.3f", last26EMA)

				// calculate MACD
				macd := fmt.Sprintf("%.3f", last12EMA-last26EMA)

				// calculate MACDS
				lastMACDS = calcEMA(last12EMA-last26EMA, lastMACDS, 9, MACDS_SMOOTHING)
				macds := fmt.Sprintf("%.3f", lastMACDS)

				// calculate RSI
				rs := lastAvgGain / lastAvgLoss
				rsi := fmt.Sprintf("%.3f", 100-100/(1+rs))

				// write row
				writer.Write([]string{time, open, high, low, close, volume, vwap, sma5, sma8, sma13, ema12, ema26, macd, macds, rsi})
			}
		}
	}
}

//----------------------------------------------------------------------------
// helper functions
//----------------------------------------------------------------------------

func panicOnNil(value interface{}) {
	if value != nil {
		panic(value)
	}
}

/*
Checks if all Alpaca environment variables are set, exiting with status 1 if
not.
*/
func checkAlpacaEnvVars() {
	alpacaEnvVars := []string{"APCA_API_KEY_ID", "APCA_API_SECRET_KEY"}

	for _, envVar := range alpacaEnvVars {
		if os.Getenv(envVar) == "" {
			fmt.Println("[ ERROR ] The environment variable", envVar, "is not set")
			os.Exit(1)
		}
	}
}

/*
Parses the command line arguments for start and end dates and the ticker
symbol list, exiting with status 1 if there is a missing required flag or an
error is encountered while parsing.
*/
func parseFlags() (start, end time.Time, tickers []string) {
	// define and parse flags
	startFlag := flag.String("s", "", "Start date (inclusive) (format: YYYYMMDD) (required)")
	endFlag := flag.String("e", "", "End date (inclusive) (format: YYYYMMDD) (default: today)")
	tickersFlag := flag.String("t", "", "Comma-separated list of ticker symbols (format: SYMBOL1,SYMBOL2) (required)")
	flag.Parse()

	// require start flag to be specified
	if *startFlag == "" {
		fmt.Println("[ ERROR ] Start date flag (-s) is missing")
		os.Exit(1)
	}

	// require ticker symbol list to be specified
	if *tickersFlag == "" {
		fmt.Println("[ ERROR ] Ticker symbol list flag (-t) is missing")
		os.Exit(1)
	}

	// get the start and end dates as time.Time objects
	start, err := time.Parse("20060102", *startFlag)
	if err != nil {
		fmt.Println("[ ERROR ] Error while parsing start date:", err)
		os.Exit(1)
	}
	end, err = time.Parse("20060102", *endFlag)
	if err != nil {
		fmt.Println("[ ERROR ] Error while parsing end date:", err)
		os.Exit(1)
	}

	// get the ticker symbols as a slice
	tickers = strings.Split(*tickersFlag, ",")

	return
}

func getHolidays(filepath string) (holidays map[string][]struct {
	Month      int
	Day        int
	EarlyClose bool
}) {
	// Open the JSON file.
	file, err := os.Open(filepath)
	if err != nil {
		fmt.Println("[ ERROR ] Error opening ../../properties/market-holidays.json:", err)
		os.Exit(1)
	}

	// Read the JSON data from the file.
	data, err := io.ReadAll(file)
	if err != nil {
		fmt.Println("[ ERROR ] Error reading file:", err)
		os.Exit(1)
	}

	// Unmarshal the JSON data into a map.
	err = json.Unmarshal(data, &holidays)
	if err != nil {
		fmt.Println("[ ERROR ] Error unmarshalling JSON:", err)
		os.Exit(1)
	}

	return holidays
}

func isHoliday(date time.Time, holidays map[string][]struct {
	Month      int
	Day        int
	EarlyClose bool
}) bool {
	// Check if the date is a holiday.
	isHoliday := false
	for _, holiday := range holidays[strconv.Itoa(date.Year())] {
		if holiday.Month == int(date.Month()) && holiday.Day == date.Day() {
			isHoliday = true
			break
		}
	}

	return isHoliday
}

func isWeekend(date time.Time) bool {
	return date.Weekday() == 0 || date.Weekday() == 6
}

func insertBar(bars []marketdata.Bar, index int, bar marketdata.Bar) []marketdata.Bar {
	// Create a new array.
	newArray := make([]marketdata.Bar, len(bars)+1)

	// Copy the elements from the old array to the new array.
	for i := 0; i < index; i++ {
		newArray[i] = bars[i]
	}

	// Insert the new element into the new array.
	newArray[index] = bar

	// Copy the remaining elements from the old array to the new array.
	for i := index + 1; i < len(bars)+1; i++ {
		newArray[i] = bars[i-1]
	}

	// Return the new array.
	return newArray
}

func calcBarCloseSMA(bars []marketdata.Bar) float64 {
	// Extract an array of just close values.
	closeValues := []float64{}
	for _, bar := range bars {
		closeValues = append(closeValues, bar.Close)
	}

	return calcSMA(closeValues)
}

func calcSMA(values []float64) float64 {
	sum := 0.0
	for _, value := range values {
		sum += value
	}

	return sum / float64(len(values))
}

func calcEMA(price, lastEMA float64, period int, smoothing float64) float64 {
	multiplier := smoothing / float64(period+1)
	return price*multiplier + lastEMA*(1-multiplier)
}

/*
gainOrLoss bool: true -> calculate avg. gain, false -> calculate avg. loss
*/
func calcFirstAvgGainLoss(bars []marketdata.Bar, gainOrLoss bool) float64 {
	var gainLossSum float64 = 0

	// sum gain or loss
	for i, bar := range bars {
		// skip first bar
		if i == 0 {
			continue
		}

		if gainOrLoss {
			// calculate gain
			gainLossSum += math.Max(bar.Close-bars[i-1].Close, 0)
		} else {
			// sum loss
			gainLossSum += math.Max(bars[i-1].Close-bar.Close, 0)
		}
	}

	return gainLossSum / float64(len(bars)-1)
}

/*
gainOrLoss bool: true -> calculate avg. gain, false -> calculate avg. loss
*/
func calcAvgGainLoss(period int, prevGainLoss float64, last, current float64, gainOrLoss bool) float64 {
	var gainLoss float64
	if gainOrLoss {
		// calculate gain
		gainLoss = math.Max(current-last, 0)
	} else {
		// calculate loss
		gainLoss = math.Max(last-current, 0)
	}

	return (prevGainLoss*float64(period-1) + gainLoss) / float64(period)
}
