defmodule ScrapperWeb.PageController do
  use ScrapperWeb, :controller

  def index(conn, _params) do
    render conn, "index.html"
  end
end
