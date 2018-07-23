defmodule ScrapperWeb.CompanyControllerTest do
  use ScrapperWeb.ConnCase

  alias Scrapper.Bovespa
  alias Scrapper.Bovespa.Company

  @create_attrs %{ibovespa: true, main_url: "some main_url", name: "some name", segment: "some segment", symbol: "some symbol"}
  @update_attrs %{ibovespa: false, main_url: "some updated main_url", name: "some updated name", segment: "some updated segment", symbol: "some updated symbol"}
  @invalid_attrs %{ibovespa: nil, main_url: nil, name: nil, segment: nil, symbol: nil}

  def fixture(:company) do
    {:ok, company} = Bovespa.create_company(@create_attrs)
    company
  end

  setup %{conn: conn} do
    {:ok, conn: put_req_header(conn, "accept", "application/json")}
  end

  describe "index" do
    test "lists all companies", %{conn: conn} do
      conn = get conn, company_path(conn, :index)
      assert json_response(conn, 200)["data"] == []
    end
  end

  describe "create company" do
    test "renders company when data is valid", %{conn: conn} do
      conn = post conn, company_path(conn, :create), company: @create_attrs
      assert %{"id" => id} = json_response(conn, 201)["data"]

      conn = get conn, company_path(conn, :show, id)
      assert json_response(conn, 200)["data"] == %{
        "id" => id,
        "ibovespa" => true,
        "main_url" => "some main_url",
        "name" => "some name",
        "segment" => "some segment",
        "symbol" => "some symbol"}
    end

    test "renders errors when data is invalid", %{conn: conn} do
      conn = post conn, company_path(conn, :create), company: @invalid_attrs
      assert json_response(conn, 422)["errors"] != %{}
    end
  end

  describe "update company" do
    setup [:create_company]

    test "renders company when data is valid", %{conn: conn, company: %Company{id: id} = company} do
      conn = put conn, company_path(conn, :update, company), company: @update_attrs
      assert %{"id" => ^id} = json_response(conn, 200)["data"]

      conn = get conn, company_path(conn, :show, id)
      assert json_response(conn, 200)["data"] == %{
        "id" => id,
        "ibovespa" => false,
        "main_url" => "some updated main_url",
        "name" => "some updated name",
        "segment" => "some updated segment",
        "symbol" => "some updated symbol"}
    end

    test "renders errors when data is invalid", %{conn: conn, company: company} do
      conn = put conn, company_path(conn, :update, company), company: @invalid_attrs
      assert json_response(conn, 422)["errors"] != %{}
    end
  end

  describe "delete company" do
    setup [:create_company]

    test "deletes chosen company", %{conn: conn, company: company} do
      conn = delete conn, company_path(conn, :delete, company)
      assert response(conn, 204)
      assert_error_sent 404, fn ->
        get conn, company_path(conn, :show, company)
      end
    end
  end

  defp create_company(_) do
    company = fixture(:company)
    {:ok, company: company}
  end
end
