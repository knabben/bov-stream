defmodule ScrapperWeb.Resolvers.Company do
  alias Scrapper.Bovespa

  @main_url Application.get_env(:scrapper, :url)

  def resume_portfolio(%{days: days, id: id}) do
    company = Bovespa.get_company!(id)
    period2 = DateTime.to_unix DateTime.utc_now
    period1 = period2 - 60*60*24*days

    "#{@main_url}?period1=#{period1}&period2=#{period2}&interval=1d&symbol=#{company.symbol}.SA"
  end

  def handle_response({:ok, %{status_code: 200, body: body}}) do
    result = Enum.at(Poison.decode!(body)["chart"]["result"], 0)
    {:ok, parse_data(result["indicators"]["quote"], result["timestamp"])}
  end

  def parse_data(indicators, timestamp) do
    data = Enum.at(indicators, 0)

    Enum.zip([data["open"], data["close"], data["high"], data["low"], timestamp])
    |> Enum.map(fn ({open, close, high, low, timestamp}) ->
      %{:date => to_string(DateTime.from_unix!(timestamp)),
        :open => open, :close => close, :high => high, :low => low} end)
  end

  def find_data(_parent, args, _resolution) do
    resume_portfolio(args)
    |> HTTPoison.get
    |> handle_response
  end
end
