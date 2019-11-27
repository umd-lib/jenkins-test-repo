# frozen_string_literal: true

class ContractorRequestsController < ApplicationController
  include PersonnelRequestController
  alias allowed_defaults allowed
  def allowed
    allowed_defaults + %i[annual_base_pay employee_name number_of_months]
  end

  private

    def model_klass
      ContractorRequest
    end
end
