Rails.application.routes.draw do
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
  root 'home#show'
  get '/my_requests' => 'home#index'

  resources :contractor_requests
  resources :labor_requests
  resources :staff_requests

  resources :users
  get '/logout' => 'users#logout'
  get 'impersonate/user/:user_id' => 'impersonate#create', as: :impersonate_user
  delete 'impersonate/revert' => 'impersonate#destroy', as: :revert_impersonate_user

  resources :organizations
  resources :organization_cutoffs
  resources :review_statuses
  resources :links

  resources :reports
  get '/reports/:id/download' => 'reports#download', as: :report_download

  get '/ping' => 'ping#verify'
end
