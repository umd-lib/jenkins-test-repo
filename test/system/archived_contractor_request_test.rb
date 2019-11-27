# frozen_string_literal: true

require 'application_system_test_case'

class ArchivedContractorRequestTest < ApplicationSystemTestCase
  def setup
    login_admin
  end

  test 'Employee type field should show "PTK Faculty" for archived records when appropriate' do
    # Create a new archive PTK Faculty record from an existing record
    contractor_record = ContractorRequest.where('unit_id IS NOT NULL').first
    fiscal_year = 2001
    fy = Date.new(fiscal_year, 1, 1).end_of_financial_year

    target_klass = 'ArchivedContractorRequest'.constantize
    archived_record = target_klass.create!(contractor_record.attributes.slice(*target_klass.attribute_names).merge(fiscal_year: fy))
    contractor_record.delete

    archived_record.employee_type = 'PTK Faculty'
    archived_record.save!

    ptk_faculty_archived = ArchivedContractorRequest.where(employee_type: 'PTK Faculty').first
    request_id = ptk_faculty_archived.id

    visit contractor_request_path(id: request_id)
    assert_equal 'PTK Faculty', find('#contractor_request_employee_type').value
  end
end
