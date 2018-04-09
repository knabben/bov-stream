// Copyright © 2018 Amim Knabben <amim.knabben@gmail.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package cmd

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/spf13/cobra"
	"github.com/tidwall/gjson"
)

var (
	tickers   string
	startDate string
	endDate   string

	streamCmd = &cobra.Command{
		Use:   "stream",
		Short: "BVSP Price stream",
		Long:  ``,
		Run: func(cmd *cobra.Command, args []string) {
			startStream()
		},
	}
)

func init() {
	RootCmd.AddCommand(streamCmd)

	streamCmd.PersistentFlags().StringVarP(&tickers, "tickers", "t", "", "Comma separated BVSP tickers")
	streamCmd.PersistentFlags().StringVarP(&startDate, "start-date", "s", "", "Start date")
	streamCmd.PersistentFlags().StringVarP(&endDate, "end-date", "e", "", "End date")
}

func parseTickers() []string {
	return strings.Split(tickers, ",")
}

func parseJSON(json string) {
	var prefix string = "chart.result.0."
	fmt.Println(gjson.Get(json, prefix+"meta.symbol"),
		gjson.Get(json, prefix+"indicators.quote"))
}

func getData(ticker string, wait chan int) {
	for {
		t1 := time.Now()
		t2 := t1.Local().Add(time.Minute * 1)

		v := url.Values{}
		v.Set("interval", "1m")
		v.Set("symbol", fmt.Sprintf("%s.SA", ticker))
		v.Set("period1", fmt.Sprintf("%d", t1.Unix()))
		v.Set("period2", fmt.Sprintf("%d", t2.Unix()))

		var urlQuery = fmt.Sprintf("https://query1.finance.yahoo.com/v8/finance/chart/%s.SA?%s", ticker, v.Encode())

		resp, err := http.Get(urlQuery)

		if err != nil {
			panic(err)
		}
		b, err := ioutil.ReadAll(resp.Body)
		parseJSON(string(b))

		time.Sleep(15 * time.Second)
	}
}

func startStream() {
	wait := make(chan int)

	for _, ticker := range parseTickers() {
		go func(ticker string, wait chan int) {
			getData(ticker, wait)
		}(ticker, wait)
	}

	<-wait
}
