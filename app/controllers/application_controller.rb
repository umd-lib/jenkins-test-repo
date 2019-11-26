# frozen_string_literal: true

class ApplicationController < ActionController::Base
  before_action :fix_cas_session

  def fix_cas_session
    if session[:cas] && !session[:cas].is_a?(HashWithIndifferentAccess)
      session[:cas] = session[:cas].with_indifferent_access
    elsif session[:cas].nil? || session[:cas][:user].nil?
      head :unauthorized
    end
  end

  def cas_uid
    session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'][ENV['CAS_UID_ATTRIBUTE']]
  end

  def cas_first_name
    session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'][ENV['CAS_FIRST_NAME_ATTRIBUTE']]
  end

  def cas_last_name
    session[ENV['CAS_SESSION_ATTRIBUTE']]['extra_attributes'][ENV['CAS_LAST_NAME_ATTRIBUTE']]
  end

  # Renders an error page with the provided information
  # Each of the parameters in optional.
  # In "error_description" parameter, lines will be split on "\n" and rendered
  # on separate lines
  #
  # Method also logs an ERROR to the log
  def render_error_page(error_code: nil, error_code_type: nil, error_message:, error_description:)
    @error_code = error_code || '400'
    @error_code_type = error_code_type || nil
    @error_message = error_message || nil
    @error_description = error_description || nil

    # Convert error_description into array, splitting on newlines
    @error_description = @error_description.split('\n') if @error_description

    @timestamp = Time.now.utc.to_s
    logger.error("#{@timestamp} - #{@error_code} - #{@error_code_type} - #{@error_message} - #{@error_description}")
    render status: @error_code, file: 'shared/error'
  end

  # Single location for "ORCHID@UMD" link, as it is used in multiple places
  def orcid_at_umd_link
    'https://www.lib.umd.edu/orcid'
  end
  helper_method :orcid_at_umd_link
end
