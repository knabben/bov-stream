defmodule WebWeb.CompanyController do
  use WebWeb, :controller

  alias Web.Bovespa
  alias Web.Bovespa.Company

  def index(conn, _params) do
    companies = Bovespa.list_companies()
    render(conn, "index.json", companies: companies)
  end
end