# frozen_string_literal: true

class OrganizationCutoffsController < ApplicationController
  after_action :verify_authorized
  rescue_from Pundit::NotAuthorizedError, with: :not_authorized

  def index
    authorize Organization
    @cutoffs = OrganizationCutoff.all
    respond_to do |format|
      format.html
    end
  end

  def update
    authorize Organization
    @cutoff = OrganizationCutoff.find(params[:id])
    respond_to do |format|
      # we have to do an update column here bc of funny primary key business...
      if @cutoff.update_columns(organization_cutoff_params.to_h)
        format.html { redirect_to organization_cutoffs_url, notice: "Organization Cutoff #{@cutoff.organization_type} was successfully updated to #{@cutoff.cutoff_date}" }
      else
        format.html { render :index, error: "There was a problem updating #{@cutoff.organization_type} " }
      end
    end
  end

  private

    def organization_cutoff_params
      params.require(:organization_cutoff).permit(:cutoff_date, :organization_type)
    end
end
