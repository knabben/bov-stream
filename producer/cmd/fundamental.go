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
	"os"
	"strings"
	"text/tabwriter"

	"net/http"
	"net/url"

	"github.com/knabben/bov-stream/producer/company"
	"github.com/spf13/cobra"
	"github.com/tidwall/gjson"
)

var fundamentalCmd = &cobra.Command{
	Use:   "fundamental",
	Short: "Fundamental data from Yahoo for BVSP stocks",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		fetchFundamental()
	},
}

func init() {
	RootCmd.AddCommand(fundamentalCmd)
}

func fetchFundamental() {
	db := company.StartDatabase()

	w := tabwriter.NewWriter(os.Stdout, 0, 0, 3, '-',
		tabwriter.AlignRight|tabwriter.Debug)

	fmt.Fprintln(w,
		"Name", "\t",
		"Symbol", "\t",
		"Segment", "\t",
		"Current Price", "\t",
		"Beta", "\t",
		"Ebitda", "\t",
		"Enterprise Value", "\t",
		"Price/Book", "\t",
		"TotalRevenue", "\t",
		"Revenue Per Share", "\t",
		"Total Debt", "\t",
		"Total Cash", "\t",
	)

	defaultKeyStats := "quoteSummary.result.0.defaultKeyStatistics"
	financialData := "quoteSummary.result.0.financialData"

	for _, company := range company.Companies {
		v := url.Values{}
		v.Set("formatted", "true")
		v.Set("modules", "defaultKeyStatistics,financialData,calendarEvents")
		var url string = fmt.Sprintf(
			"https://query2.finance.yahoo.com/v10/finance/quoteSummary/%s.SA?%s",
			company.Symbol, v.Encode())

		resp, err := http.Get(url)
		if err != nil {
			panic(err)
		}

		b, err := ioutil.ReadAll(resp.Body)
		currentPrice := gjson.Get(string(b), financialData+".currentPrice.fmt")
		beta := gjson.Get(string(b), defaultKeyStats+".beta.fmt")
		enpValue := gjson.Get(string(b), defaultKeyStats+".enterpriseValue.fmt")
		priceToBook := gjson.Get(string(b), defaultKeyStats+".priceToBook.fmt")

		revenuePerShare := gjson.Get(string(b), financialData+".revenuePerShare.fmt")
		totalCash := gjson.Get(string(b), financialData+".totalCash.fmt")
		totalRevenue := gjson.Get(string(b), financialData+".totalRevenue.fmt")
		totalDebt := gjson.Get(string(b), financialData+".totalDebt.fmt")
		ebitda := gjson.Get(string(b), financialData+".ebitda.fmt")

		fmt.Fprintln(w,
			company.Name, "\t",
			company.Symbol, "\t",
			strings.Split(company.Segment, "/")[0], "\t",
			currentPrice, "\t",
			beta, "\t",
			ebitda, "\t",
			enpValue, "\t",
			priceToBook, "\t",
			totalRevenue, "\t",
			revenuePerShare, "\t",
			totalDebt, "\t",
			totalCash, "\t",
		)

		resp.Body.Close()
	}

	defer db.Close()
	w.Flush()
}
