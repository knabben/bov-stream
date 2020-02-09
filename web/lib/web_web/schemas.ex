defmodule WebWeb.Schema do
  use Absinthe.Schema

  alias Web.{Bovespa, Repo}
  alias WebWeb.Resolvers

  import_types __MODULE__.CompanyTypes

  mutation do
    field :company, :company_result do
      arg :input, non_null(:company_input)
      resolve &Resolvers.Company.create_company/3
    end
  end

  query do
    field :companies, list_of(:company) do
      resolve fn _, _, _ ->
        {:ok, Bovespa.list_companies()}
      end
    end
  end
end