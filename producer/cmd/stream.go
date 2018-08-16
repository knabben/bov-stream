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

	"github.com/knabben/bov-stream/producer/company"
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

func parseJSON(json string) []string {
	var prefix string = "chart.result.0"
	prices := []string{}

	results := gjson.GetMany(json, prefix+".timestamp")
	timestamp := reflect.ValueOf(results[0].Value())

	open := reflect.ValueOf(gjson.GetMany(json, prefix+".indicators.quote.0.open")[0].Value())
	high := reflect.ValueOf(gjson.GetMany(json, prefix+".indicators.quote.0.high")[0].Value())
	low := reflect.ValueOf(gjson.GetMany(json, prefix+".indicators.quote.0.low")[0].Value())
	close := reflect.ValueOf(gjson.GetMany(json, prefix+".indicators.quote.0.close")[0].Value())
	volume := reflect.ValueOf(gjson.GetMany(json, prefix+".indicators.quote.0.volume")[0].Value())

	for i := 0; i < timestamp.Len(); i++ {
		p := fmt.Sprintf("%s,%.2f,%.2f,%.2f,%.2f,%.2f",
			time.Unix(
				int64(timestamp.Index(i).Interface().(float64)), 0).Format("2006-01-02"),
			open.Index(i).Interface().(float64),
			high.Index(i).Interface().(float64),
			low.Index(i).Interface().(float64),
			close.Index(i).Interface().(float64),
			volume.Index(i).Interface().(float64))
		prices = append(prices, p)
	}
	return prices
}

func getData(ticker string, wait chan int) {
	for {
		w := kafka.NewWriter(
			kafka.WriterConfig{
				Brokers:  []string{"192.168.99.252:9092"},
				Topic:    ticker,
				Balancer: &kafka.LeastBytes{},
			})

		v := url.Values{}
		v.Set("interval", "1d")
		v.Set("range", "30d")
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
		prices := parseJSON(string(b))

		for _, value := range prices {
			w.WriteMessages(context.Background(), kafka.Message{Value: []byte(value)})
		}
		w.Close()
		time.Sleep(15 * time.Second)
	}
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
