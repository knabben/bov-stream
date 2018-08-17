defmodule ScrapperWeb.UserSocket do
  use Phoenix.Socket
  use Absinthe.Phoenix.Socket, schema: ScrapperWeb.Schema

  transport :websocket, Phoenix.Transports.WebSocket
  channel "money:*", ScrapperWeb.MoneyChannel

  def connect(_params, socket) do
    IO.puts "Connecting"
    {:ok, socket}
  end

  def id(_socket), do: nil
end
