# frozen_string_literal: true

class ArchivedStaffRequest < StaffRequest
  self.table_name = 'archived_requests'
  class << self
    def policy_class
      ArchivedRequestPolicy
    end

    # all the fields associated to the model
    def fields
      %i[fiscal_year] + StaffRequest.fields
    end
  end
end
