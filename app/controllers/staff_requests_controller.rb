# frozen_string_literal: true

class StaffRequestsController < ApplicationController
  include PersonnelRequestController
  alias allowed_defaults allowed
  def allowed
    allowed_defaults + %i[annual_base_pay employee_name]
  end

  private

    def model_klass
      StaffRequest
    end
end
