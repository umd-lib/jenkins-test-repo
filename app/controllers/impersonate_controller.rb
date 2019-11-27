# frozen_string_literal: true

class ImpersonateController < ApplicationController
  after_action :verify_authorized, only: :create

  # Session parameter name for impersonation id
  IMPERSONATE_USER_PARAM = 'impersonate_user_id'

  # GET /impersonate/user/123
  def create
    impersonated_user = User.find_by(id: params[:user_id])
    authorize impersonated_user || User.new, :impersonate?
    impersonate(impersonated_user)
    redirect_to root_path
  end

  # Revert the user impersonation
  # DELETE /impersonate/revert
  def destroy
    revert_impersonate
    redirect_to root_path
  end

  private

    # Sets session parameter for performing impersonations
    #
    # +impersonated_user+: the user to impersonate
    def impersonate(impersonated_user)
      clear_current_user # just a sanity check
      session[IMPERSONATE_USER_PARAM] = impersonated_user.id
      logger.info "#{actual_user.cas_directory_id} now impersonating #{current_user.cas_directory_id}"
    end

    # Stops impersonation
    def revert_impersonate
      return if session[IMPERSONATE_USER_PARAM].nil?

      clear_current_user
      impersonated_user = current_user
      session[IMPERSONATE_USER_PARAM] = nil
      logger.info "#{actual_user.cas_directory_id} has stopped impersonating #{impersonated_user.cas_directory_id}"
    end
end
