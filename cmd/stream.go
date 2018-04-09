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

func getData(url string) string {
	resp, err := http.Get(url)

	if err != nil {
		panic(err)
	}
	b, err := ioutil.ReadAll(resp.Body)
	return string(b)
}

func startStream() {
	t1, _ := time.Parse("2006-01-02", startDate)
	t2, _ := time.Parse("2006-01-02", endDate)

	for _, ticker := range parseTickers() {
		v := url.Values{}
		v.Set("interval", "1m")
		v.Set("symbol", fmt.Sprintf("%s.SA", ticker))
		v.Set("period1", fmt.Sprintf("%d", t1.Unix()))
		v.Set("period2", fmt.Sprintf("%d", t2.Unix()))

		var url string = fmt.Sprintf("https://query1.finance.yahoo.com/v8/finance/chart/?%s", v.Encode())

		fmt.Println(getData(url))
	}
}
