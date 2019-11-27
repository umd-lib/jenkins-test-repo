# frozen_string_literal: true

class ArchivedContractorRequest < ContractorRequest
  self.table_name = 'archived_requests'
  VALID_EMPLOYEE_TYPES = ['Contingent 2', 'Contract Faculty', 'PTK Faculty'].freeze
  class << self
    def policy_class
      ArchivedRequestPolicy
    end

    # all the fields associated to the model
    def fields
      %i[fiscal_year] + ContractorRequest.fields
    end
  end
end
