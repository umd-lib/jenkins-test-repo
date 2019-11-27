# frozen_string_literal: true

require 'test_helper'

# Tests for the "User" model
class ContractorRequestTest < ActiveSupport::TestCase
  def setup
    @request = ContractorRequest.where('unit_id IS NOT NULL').first
    @archived = ArchivedContractorRequest.where(employee_type: 'Contract Faculty').first
  end

  test 'when moving from archive, employee type contract faculty should be mapped to PTK Faculty' do
    attrs = %w[ contractor_name organization_id employee_type hours_per_week justification
                nonop_funds nonop_source number_of_months position_title
                request_type ]
    spawned = ContractorRequest.from_archived(@archived.attributes.select { |a| attrs.include? a })
    spawned.annual_base_pay = @archived.annual_base_pay

    assert spawned.valid?
    assert_equal spawned.employee_type, 'PTK Faculty'
    assert_equal @archived.employee_type, 'Contract Faculty'
  end
end
