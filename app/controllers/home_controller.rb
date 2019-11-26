# frozen_string_literal: true

class HomeController < ApplicationController
  def index # rubocop:disable Metrics/MethodLength
    @cas_uid = session.to_hash.dig(ENV['CAS_SESSION_ATTRIBUTE'], 'extra_attributes', ENV['CAS_UID_ATTRIBUTE'])

    # If we can't get the unique identifier from CAS, show an error page.
    # This may occur user is a member of a group we haven't asked DIT to
    # release attributes for.
    if @cas_uid.blank?
      render_error_page(
        error_message: 'CAS Error',
        error_description: 'An error occurred retrieving your attributes from CAS.'
      )
      return
    end

    orcid_record = OrcidRecord.find_by(uid: @cas_uid)

    if orcid_record
      # Record exists, so just show the "Previously Captured" page
      @first_name = session.to_hash.dig(ENV['CAS_SESSION_ATTRIBUTE'], 'extra_attributes', ENV['CAS_FIRST_NAME_ATTRIBUTE'])
      @last_name = session.to_hash.dig(ENV['CAS_SESSION_ATTRIBUTE'], 'extra_attributes', ENV['CAS_LAST_NAME_ATTRIBUTE'])
      @orcid_id = orcid_record.orcid_id
      @registration_date = orcid_record.registered_at.strftime('%B %e, %Y')

      render 'previously_captured'
    else
      # Record not found, so show "Terms of Service" page
      render 'terms_of_service'
    end
  end
end
