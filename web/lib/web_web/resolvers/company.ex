defmodule WebWeb.Resolvers.Company do
  alias Web.Bovespa

  def create_company(_, %{input: company_input}, _) do
    case Bovespa.create_company(company_input) do
      {:ok, company} ->
        {:ok, %{company: company}}
      {:error, changeset} ->
        {:ok, %{errors: transform_errors(changeset)}}
    end
  end

  defp transform_errors(changeset) do
    changeset
    |> Ecto.Changeset.traverse_errors(&format_error/1)
    |> Enum.map(fn
      {key, value} ->
        %{key: key, message: value}
    end)
  end

  defp format_error({msg, opts}) do
    Enum.reduce(opts, msg, fn {key, value}, acc ->
      String.replace(acc, "%{#{key}}", to_string(value))
    end)
  end

end