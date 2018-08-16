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
	"context"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"reflect"
	"time"

	"github.com/knabben/bov-stream/live/company"
	"github.com/segmentio/kafka-go"

	"github.com/spf13/cobra"
	"github.com/tidwall/gjson"
)

type priceServer struct{}

var (
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

	streamCmd.PersistentFlags().StringVarP(&startDate, "start-date", "s", "", "Start date")
	streamCmd.PersistentFlags().StringVarP(&endDate, "end-date", "e", "", "End date")
}

func parseJSON(json string) map[time.Time]float64 {
	var prefix string = "chart.result.0."
	prices := make(map[time.Time]float64)

	results := gjson.GetMany(json, prefix+"indicators.quote.0.close", prefix+"timestamp")

	closePrice := reflect.ValueOf(results[0].Value())
	timestamp := reflect.ValueOf(results[1].Value())

	for i := 0; i < closePrice.Len(); i++ {
		price := closePrice.Index(i).Interface()
		if price == nil {
			continue
		}

		ts := int64(timestamp.Index(i).Interface().(float64))
		prices[time.Unix(ts, 0)] = price.(float64)
	}

	return prices
}

func getData(ticker string, wait chan int) {
	w := kafka.NewWriter(
		kafka.WriterConfig{
			Brokers:  []string{"192.168.99.252:9092"},
			Topic:    ticker,
			Balancer: &kafka.LeastBytes{},
		})

	v := url.Values{}
	v.Set("interval", "1d")
	v.Set("range", "5d")
	v.Set("symbol", fmt.Sprintf("%s.SA", ticker))

	var urlQuery = fmt.Sprintf(
		"https://query1.finance.yahoo.com/v8/finance/chart/%s.SA?%s",
		ticker, v.Encode())

	fmt.Println(urlQuery)
	resp, err := http.Get(urlQuery)
	if err != nil {
		panic(err)
	}

	b, err := ioutil.ReadAll(resp.Body)
	closePrice := parseJSON(string(b))

	for key, value := range closePrice {
		w.WriteMessages(context.Background(),
			kafka.Message{
				Value: []byte(fmt.Sprintf("%s|%f",
					key.Format("2006-01-02 15:04"), value),
				),
			},
		)
		fmt.Println(key, value)
	}
	w.Close()
	time.Sleep(5 * time.Second)
}

func startStream() {
	db := company.StartDatabase()
	company.ListCompanies(db)
	wait := make(chan int)

	for _, ticker := range company.Companies {
		go func(ticker company.Company, wait chan int) {
			getData(ticker.Symbol, wait)
		}(ticker, wait)
	}

	<-wait
}
