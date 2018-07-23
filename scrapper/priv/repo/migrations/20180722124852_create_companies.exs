defmodule Scrapper.Repo.Migrations.CreateCompanies do
  use Ecto.Migration

  def change do
    create table(:companies) do
      add :symbol, :string
      add :name, :string
      add :main_url, :string
      add :ibovespa, :boolean, default: false, null: false
      add :segment, :string

      timestamps()
    end

  end
end
