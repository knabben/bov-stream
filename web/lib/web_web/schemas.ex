defmodule WebWeb.Schema do
  use Absinthe.Schema

  alias Web.{Bovespa, Repo}
  alias WebWeb.Resolvers

  query do
    field :companies, list_of(:company) do
      resolve fn _, _, _ ->
        {:ok, Bovespa.list_companies()}
      end
    end
  end

  object :company do
    field :id, :id
    field :name, :string
    field :symbol, :string
    field :segment, :string
    field :ibovespa, :boolean
  end

end