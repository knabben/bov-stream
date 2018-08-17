defmodule ScrapperWeb.MoneyChannel do
  use ScrapperWeb, :channel

  def join("money:" <> money_id, _params, socket) do
    {:ok, assign(socket, :money_id, String.to_integer(money_id))}
  end

  def handle_in("money", params, socket) do
    return_value = Enum.at(Map.values(params),0)
    values = Enum.at(Map.values(return_value), 0)
    data = %{
      id: Map.keys(params),
      pnl: values["pnl"],
      portfolio_value: values["portfolio_value"],
      returns: values["returns"],
      timestamp: Enum.at(Map.keys(return_value), 0)
    }

    IO.inspect data
    Absinthe.Subscription.publish(ScrapperWeb.Endpoint, data , money: "*")
    broadcast! socket, "money", params
    {:noreply, socket}
  end
end
