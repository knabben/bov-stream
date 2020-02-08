defmodule Web.Bovespa.Company do
  use Ecto.Schema
  import Ecto.Changeset

  schema "companies" do
    field :ibovespa, :boolean, default: false
    field :main_url, :string
    field :name, :string
    field :segment, :string
    field :symbol, :string

    timestamps()
  end

  @doc false
  def changeset(company, attrs) do
    company
    |> cast(attrs, [:symbol, :name, :main_url, :ibovespa, :segment])
    |> validate_required([:symbol, :name, :main_url, :ibovespa, :segment])
  end
end
