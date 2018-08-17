defmodule ScrapperWeb.MoneyChannel do
  use ScrapperWeb, :channel

  def join("money:" <> money_id, _params, socket) do
    {:ok, assign(socket, :money_id, String.to_integer(money_id))}
  end
end
