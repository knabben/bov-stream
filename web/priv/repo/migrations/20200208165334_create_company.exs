defmodule Web.Repo.Migrations.CreateCompany do
  use Ecto.Migration

  def change do
    create table(:companies) do
      add :ibovespa, :boolean, default: false
      add :main_url, :string
      add :name, :string
      add :segment, :string
      add :symbol, :string
    end

  end
end
