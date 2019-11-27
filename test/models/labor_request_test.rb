# frozen_string_literal: true

require 'test_helper'

# Tests for the "User" model
class LaborRequestTest < ActiveSupport::TestCase
  def setup
    @request = LaborRequest.where('unit_id IS NOT NULL').first
  end

  test 'unit should be in the department' do
    assert @request.valid?
    @request.unit = Organization.where('organization_id IS NOT ?', @request.organization.id)
                                .where(organization_type: Organization.organization_types['unit']).first
    assert_not @request.valid?
  end

  test 'should give annual_cost the same even when cast as request' do
    plain_request = Request.find(@request.id)

    annual_cost_or_base_pay_in_cents = plain_request.annual_cost_or_base_pay * 100

    annual_cost_or_base_pay_as_money = Money.new(annual_cost_or_base_pay_in_cents, 'USD')
    assert_equal annual_cost_or_base_pay_as_money, @request.annual_cost
  end

  test 'should give the real source class even when cast as request' do
    plain_request = Request.find(@request.id)
    assert_equal plain_request.source_class, @request.class
  end

  test 'should give a blank string when a weird field is called' do
    assert_equal @request.call_field(:cluckcluck), ''
  end

  test 'should tell if its spawned' do
    assert_not @request.spawned?
    @request.spawned = 1
    assert @request.spawned?
  end

  test 'justifcation length should be less than 125 words (unless its archived)' do
    assert @request.valid?
    @request.justification = ' word ' * 126
    assert_not @request.valid?

    archived = ArchivedLaborRequest.first
    assert archived.valid?
    archived.justification = ' word ' * 126
    assert archived.valid?
  end
end
