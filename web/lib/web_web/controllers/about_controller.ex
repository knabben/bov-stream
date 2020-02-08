defmodule WebWeb.AboutController do
  use WebWeb, :controller
  def index(conn, _params) do
    render(conn, "about.html")
  end
end