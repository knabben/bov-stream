defmodule WebWeb.CompanyView do
  use WebWeb, :view
  alias WebWeb.CompanyView

  def render("index.json", %{companies: companies}) do
    %{data: render_many(companies, CompanyView, "company.json")}
  end

  def render("company.json", %{company: company}) do
    %{id: company.id,
      symbol: company.symbol,
      name: company.name,
      main_url: company.main_url,
      ibovespa: company.ibovespa,
      segment: company.segment}
  end
end