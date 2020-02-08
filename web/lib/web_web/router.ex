defmodule WebWeb.Router do
  use WebWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_flash
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api" do
    pipe_through :api
    resources "/company", CompanyController, only: [:index]
  end

  scope "/" do
    pipe_through :api

    forward "/graphql", Absinthe.Plug, schema: WebWeb.Schema
    forward "/graphiql", Absinthe.Plug.GraphiQL, schema: WebWeb.Schema
  end

end
