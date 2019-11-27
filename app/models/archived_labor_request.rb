# frozen_string_literal: true

class ArchivedLaborRequest < LaborRequest
  self.table_name = 'archived_requests'
  class << self
    def policy_class
      ArchivedRequestPolicy
    end

    # all the fields associated to the model
    def fields
      %i[fiscal_year] + LaborRequest.fields
    end

    # Returns an ordered array used in the index pages
    def index_fields
      fields - %i[nonop_source justification review_comment created_at updated_at]
    end
  end
end
