defmodule ScrapperWeb.Schema do
  use Absinthe.Schema

  alias Scrapper.{Bovespa, Repo}
  alias ScrapperWeb.Resolvers

  query do
    field :companies, list_of(:company) do
      resolve fn _, _, _ ->
        {:ok, Bovespa.list_companies}
      end
    end

    field :company_days, list_of(:quote) do
      arg :id, :integer
      arg :days, :integer
      resolve &Resolvers.Company.find_data/3
    end
  end

  subscription do
    field :money, :return do
      config fn _args, _info ->
        {:ok, topic: "*"}
      end
    end
  end

  object :return do
    field :id, :id
    field :pnl, :float
    field :portfolio_value, :float
    field :returns, :float
    field :timestamp, :integer
  end

  object :company do
    field :id, :id
    field :name, :string
    field :symbol, :string
  end

  object :quote do
    field :date, :string
    field :open, :float
    field :high, :float
    field :low, :float
    field :close, :float
  end
end
