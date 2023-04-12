package main

import (
	"fmt"

	"github.com/robfig/cron/v3"
)

func main() {
	//-------------------------------------------------------------------------
	// configure and start scheduler
	//-------------------------------------------------------------------------

	c := cron.New()
  // execute trade sequence every minute from 09:00-16:00 EST, M-F
	c.AddFunc("TZ=America/New_York * 9-16 * * 1-5", func() { fmt.Println("This should print every minute.") })
	c.Start()

	//-------------------------------------------------------------------------
	// block forever (keeps service running)
	//-------------------------------------------------------------------------

	select {}
}
