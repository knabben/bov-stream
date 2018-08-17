defmodule Scrapper.Application do
  use Application

  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  def start(_type, _args) do
    import Supervisor.Spec

    # Define workers and child supervisors to be supervised
    children = [
      # Start the Ecto repository
      supervisor(Scrapper.Repo, []),
      # Start the endpoint when the application starts
      supervisor(ScrapperWeb.Endpoint, []),
      supervisor(Absinthe.Subscription, [ScrapperWeb.Endpoint]),
    ]

    opts = [strategy: :one_for_one, name: Scrapper.Supervisor]
    Supervisor.start_link(children, opts)
  end

  def config_change(changed, _new, removed) do
    ScrapperWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
