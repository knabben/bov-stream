defmodule WebWeb.Schema.CompanyTypes do
  use Absinthe.Schema.Notation
  use Absinthe.Relay.Schema.Notation, :modern

  input_object :company_input do
    field :symbol, non_null(:string)
    field :name, non_null(:string)
    field :main_url, non_null(:string)
    field :segment, non_null(:string)
  end

  object :input_error do
    field :key, non_null(:string)
    field :message, non_null(:string)
  end

  object :company_result do
    field :company, :company
    field :errors, list_of(:input_error)
  end

  object :company do
    field :id, :id
    field :name, :string
    field :symbol, :string
    field :segment, :string
    field :ibovespa, :boolean
  end

  interface :company_result do
    field :name, :string
    resolve_type fn
      %Web.Bovespa.Company{}, _ ->
        :company
      _, _ ->
      nil
    end
  end

  connection node_type: :company

  node object :company do
    interfaces [:company_result]

    field :name, :string
    field :symbol, :string
    field :segment, :string
  end

end