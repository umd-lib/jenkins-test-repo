# frozen_string_literal: true

class OrganizationsController < ApplicationController
  after_action :verify_authorized
  rescue_from Pundit::NotAuthorizedError, with: :not_authorized

  def index
    authorize Organization
    @organizations = Organization.all
    respond_to do |format|
      format.html
      format.json { render json: Organization.all.to_json }
    end
  end

  def new
    authorize Organization
    @organizations = Organization.all
    @organization = Organization.new(organization_id: Organization.root_org.id)
  end

  def show
    authorize Organization
    @organizations = Organization.all
    @organization = Organization.find(params[:id])
  end

  def edit
    authorize Organization
    @organizations = Organization.all
    @organization = Organization.includes(:parent, :roles).find(params[:id])
  end

  def update
    authorize Organization
    @organization = Organization.find(params[:id])

    respond_to do |format|
      if @organization.update(organization_params)
        format.html { redirect_to organizations_url, notice: "Organization #{@organization.name} was successfully updated." }
      else
        format.html { render :edit, error: @organization.errors }
      end
    end
  end

  def create
    authorize Organization
    @organization = Organization.new(organization_params)
    respond_to do |format|
      if @organization.save(organization_params)
        format.html { redirect_to organizations_url, notice: "Organization #{@organization.name} was successfully created." }
      else
        format.html { render :new }
      end
    end
  end

  # DELETE /review_status/1
  def destroy
    authorize Organization
    @organization = Organization.find(params[:id])
    if @organization.destroy
      flash[:notice] = "Organization #{@organization.name} was successfully deleted."
    else
      flash[:error] = "ERROR Deleting #{@organization.name} #{@organization.errors}"
    end
    respond_to do |format|
      format.html { redirect_to organizations_url }
    end
  end

  private

    def organization_params
      params.require(:organization).permit(:code, :name, :organization_type, :deactivated,
                                           :organization_id, roles_attributes: %i[id user_id _destroy])
    end
end
