# frozen_string_literal: true

module Cutoffable
  extend ActiveSupport::Concern

  included do
    enum organization_type: { root: 1, division: 2, department: 3, unit: 4 }
  end
end
