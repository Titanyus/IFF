Rails.application.routes.draw do
  root "care_cases#index"
  resource :session, only: [:new, :create, :destroy]
  resources :care_cases, only: [:index, :show, :new, :create] do
    member do
      patch :activate
      patch :close
      patch :trash
      patch :restore
    end
  end
end
