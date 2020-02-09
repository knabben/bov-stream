defmodule WebWeb.Schema.CompanyTypes do
  use Absinthe.Schema.Notation

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

end