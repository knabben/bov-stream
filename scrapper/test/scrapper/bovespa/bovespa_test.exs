defmodule Scrapper.BovespaTest do
  use Scrapper.DataCase

  alias Scrapper.Bovespa

  describe "companies" do
    alias Scrapper.Bovespa.Company

    @valid_attrs %{ibovespa: true, main_url: "some main_url", name: "some name", segment: "some segment", symbol: "some symbol"}
    @update_attrs %{ibovespa: false, main_url: "some updated main_url", name: "some updated name", segment: "some updated segment", symbol: "some updated symbol"}
    @invalid_attrs %{ibovespa: nil, main_url: nil, name: nil, segment: nil, symbol: nil}

    def company_fixture(attrs \\ %{}) do
      {:ok, company} =
        attrs
        |> Enum.into(@valid_attrs)
        |> Bovespa.create_company()

      company
    end

    test "list_companies/0 returns all companies" do
      company = company_fixture()
      assert Bovespa.list_companies() == [company]
    end

    test "get_company!/1 returns the company with given id" do
      company = company_fixture()
      assert Bovespa.get_company!(company.id) == company
    end

    test "create_company/1 with valid data creates a company" do
      assert {:ok, %Company{} = company} = Bovespa.create_company(@valid_attrs)
      assert company.ibovespa == true
      assert company.main_url == "some main_url"
      assert company.name == "some name"
      assert company.segment == "some segment"
      assert company.symbol == "some symbol"
    end

    test "create_company/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Bovespa.create_company(@invalid_attrs)
    end

    test "update_company/2 with valid data updates the company" do
      company = company_fixture()
      assert {:ok, company} = Bovespa.update_company(company, @update_attrs)
      assert %Company{} = company
      assert company.ibovespa == false
      assert company.main_url == "some updated main_url"
      assert company.name == "some updated name"
      assert company.segment == "some updated segment"
      assert company.symbol == "some updated symbol"
    end

    test "update_company/2 with invalid data returns error changeset" do
      company = company_fixture()
      assert {:error, %Ecto.Changeset{}} = Bovespa.update_company(company, @invalid_attrs)
      assert company == Bovespa.get_company!(company.id)
    end

    test "delete_company/1 deletes the company" do
      company = company_fixture()
      assert {:ok, %Company{}} = Bovespa.delete_company(company)
      assert_raise Ecto.NoResultsError, fn -> Bovespa.get_company!(company.id) end
    end

    test "change_company/1 returns a company changeset" do
      company = company_fixture()
      assert %Ecto.Changeset{} = Bovespa.change_company(company)
    end
  end
end
