defmodule ScrapperWeb.Router do
  use ScrapperWeb, :router

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

  scope "/", ScrapperWeb do
    pipe_through :browser

    get "/", PageController, :index
  end

  scope "/api" do
    pipe_through :api
    resources "/companies", CompanyController, only: [:index]
  end

  scope "/" do
    pipe_through :api
    forward "/graphql", Absinthe.Plug, schema: ScrapperWeb.Schema
    forward "/graphiql", Absinthe.Plug.GraphiQL,
      schema: ScrapperWeb.Schema,
      socket: ScrapperWeb.UserSocket,
      interface: :simple
  end

end
