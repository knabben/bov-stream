defmodule WebWeb.Schema do
  use Absinthe.Schema
  use Absinthe.Relay.Schema, :modern

  alias Web.{Bovespa, Repo}
  alias WebWeb.Resolvers

  node interface do
    resolve_type fn
      %Web.Bovespa.Company{}, _ ->
        :company
      _, _ ->
        nil
    end
  end

  import_types __MODULE__.CompanyTypes

   subscription do
    field :money, :company do

      config fn _args, _info ->
        {:ok, topic: "*"}
      end
    end
  end

  mutation do
    field :company, :company_result do
      arg :input, non_null(:company_input)
      resolve &Resolvers.Company.create_company/3
    end
  end

  query do
    connection field :company_items, node_type: :company do
      arg :order, type: :sort_order, default_value: :asc
      resolve &Resolvers.Company.company_filter/3
    end

    field :companies, list_of(:company) do
      resolve fn _, _, _ ->
        {:ok, Bovespa.list_companies()}
      end
    end
  end

  enum :sort_order do
    value :asc
    value :desc
  end
  
end