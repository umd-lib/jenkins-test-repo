# frozen_string_literal: true

class HomeController < ApplicationController
  include PersonnelRequestController

  def index
    @requests = @model_klass
                .select('requests.*,  ( coalesce(annual_base_pay_cents,0) + ( coalesce(number_of_positions,0) * coalesce(hourly_rate_cents,0) * coalesce(hours_per_week,0) * coalesce(number_of_weeks, 0)) ) AS annual_cost_or_base_pay')
                .includes(:organization, :user, :review_status)
                .joins('LEFT JOIN organizations as units ON units.id = Requests.unit_id')
                .where(user: current_user).order(params[:sort])
    respond_to do |format|
      format.html { @requests = @requests.paginate(page: params[:page]) }
      format.xlsx { send_xlsx(@requests, @model_klass) }
    end
  end

  def show; end

  private

    def model_klass
      Request
    end

    # we just override this with nothing.
    def set_request; end
end
