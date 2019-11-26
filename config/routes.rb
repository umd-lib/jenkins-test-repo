Rails.application.routes.draw do
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
  root 'home#index', as: 'terms_of_service'

  get '/orcid_auth_code_request' => 'orcid#auth_code_request'
  get '/orcid_auth_code_callback' => 'orcid#auth_code_callback'

  get '/ping' => 'ping#verify'
end
