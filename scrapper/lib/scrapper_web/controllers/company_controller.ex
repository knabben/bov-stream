defmodule ScrapperWeb.CompanyController do
  use ScrapperWeb, :controller

  alias Scrapper.Bovespa
  alias Scrapper.Bovespa.Company

  action_fallback ScrapperWeb.FallbackController

  def index(conn, _params) do
    companies = Bovespa.list_companies()
    render(conn, "index.json", companies: companies)
  end

  def create(conn, %{"company" => company_params}) do
    with {:ok, %Company{} = company} <- Bovespa.create_company(company_params) do
      conn
      |> put_status(:created)
      |> render("show.json", company: company)
    end
  end

  def show(conn, %{"id" => id}) do
    company = Bovespa.get_company!(id)
    render(conn, "show.json", company: company)
  end

  def update(conn, %{"id" => id, "company" => company_params}) do
    company = Bovespa.get_company!(id)

    with {:ok, %Company{} = company} <- Bovespa.update_company(company, company_params) do
      render(conn, "show.json", company: company)
    end
  end

  def delete(conn, %{"id" => id}) do
    company = Bovespa.get_company!(id)
    with {:ok, %Company{}} <- Bovespa.delete_company(company) do
      send_resp(conn, :no_content, "")
    end
  end
end
