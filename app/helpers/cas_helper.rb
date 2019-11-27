# frozen_string_literal: true

# Provides CAS Authentication and whitelist authorization
module CasHelper
  def fix_cas_session
    session[:cas] ||= HashWithIndifferentAccess.new
    return if session[:cas].is_a?(HashWithIndifferentAccess)

    session[:cas] = session[:cas].with_indifferent_access
  end

  def ensure_auth
    if session[:cas].nil? || session[:cas][:user].nil?
      render status: :unauthorized, plain: 'Redirecting to SSO...'
    else
      update_current_user(User.find_by(cas_directory_id: session[:cas][:user]))
      render status: :forbidden, plain: 'Unrecognized user' unless @current_user
    end
    nil
  end

  # Returns true if a user is being impersonated, false otherwise
  def impersonating_user?
    !session[ImpersonateController::IMPERSONATE_USER_PARAM].nil?
  end

  # Returns the impersonated user
  def impersonated_user
    if @current_user.nil? || session[ImpersonateController::IMPERSONATE_USER_PARAM] != @current_user.id
      user = User.find_by(id: session[ImpersonateController::IMPERSONATE_USER_PARAM])
      update_current_user(user)
    end
    @current_user
  end

  # Returns the actual logged in user, ignoring impersonation
  def actual_user
    if @current_user.nil? || session[:cas][:user] != @current_user.cas_directory_id
      update_current_user(User.find_by(cas_directory_id: session[:cas][:user]))
    end
    @current_user
  end

  # Retrieves the User for the current request from the database, using the
  # "cas_user" id from the session, the impersonated user, or nil
  # if the User cannot be found.
  def current_user
    impersonating_user? ? impersonated_user : actual_user
  end

  def clear_current_user
    update_current_user(nil)
  end

  private

    attr_writer :current_user

    # Simply updates the current user
    def update_current_user(user)
      @current_user = user if user
    end
end
