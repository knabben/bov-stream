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
	"reflect"
	"strings"
	"time"

	"github.com/spf13/cobra"
	"github.com/tidwall/gjson"

	pb "github.com/knabben/bov-stream/src_proto"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

type priceServer struct{}

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

func getData(ticker string, wait chan int, conn *grpc.ClientConn) {
	for {
		client := pb.NewRoutePriceClient(conn)
		t2 := time.Now()
		t1 := t2.Local().Add(-1 * time.Hour)

		v := url.Values{}
		v.Set("interval", "1m")
		v.Set("symbol", fmt.Sprintf("%s.SA", ticker))
		v.Set("period1", fmt.Sprintf("%d", t1.Unix()))
		v.Set("period2", fmt.Sprintf("%d", t2.Unix()))

		var urlQuery = fmt.Sprintf("https://query1.finance.yahoo.com/v8/finance/chart/%s.SA?%s",
			ticker, v.Encode())
		fmt.Println(urlQuery)

		resp, err := http.Get(urlQuery)
		if err != nil {
			panic(err)
		}

		b, err := ioutil.ReadAll(resp.Body)
		closePrice := parseJSON(string(b))

		ctx, cancel := context.WithTimeout(context.Background(), time.Second)

		for key, value := range closePrice {
			_, err := client.TraversePrice(ctx, &pb.InputPrice{
				Symbol:   ticker,
				Datetime: key.Format("2006-01-02 15:04"),
				Close:    float32(value),
			})
			if err != nil {
				fmt.Println(err)
			}

		}
		defer cancel()
		time.Sleep(5 * time.Second)
	}
}

func startStream() {
	wait := make(chan int)

	conn, err := grpc.Dial("localhost:10000", grpc.WithInsecure())
	if err != nil {
		panic(err)
	}

	for _, ticker := range parseTickers() {
		go func(ticker string, wait chan int, conn *grpc.ClientConn) {
			getData(ticker, wait, conn)
		}(ticker, wait, conn)
	}

	defer conn.Close()
	<-wait
}
