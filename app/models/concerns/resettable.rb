# frozen_string_literal: true

# this just patchs rails reset_counters methods to work with the monkey
# business we're doing with our associations
# disabling rubocop...this is taken from Rails core.
#
#rubocop:disable all
module Resettable
  extend ActiveSupport::Concern

  # this is used to generate the organization's associated icon
  TYPE_MAPPING = { 'root' => 'queen', 'division' => 'bishop', 'department' => 'knight', 'unit' => 'pawn' }.freeze
  # fields that cna't be changed if there are records in teh archive
  UNEDITABLE_IF_ARCHIVED = %w[organization_id name code organization_type].freeze

  class_methods do
    def reset_counters(id, *counters)
      object = find(id)
      counters.each do |counter_association|
        has_many_association = _reflect_on_association(counter_association)
        unless has_many_association
          has_many = reflect_on_all_associations(:has_many)
          has_many_association = has_many.find do |association|
            association.counter_cache_column &&
              association.counter_cache_column.to_sym == counter_association.to_sym
          end
          counter_association = has_many_association.plural_name if has_many_association
        end
        raise ArgumentError, "'#{name}' has no association called '#{counter_association}'" unless has_many_association

        if has_many_association.is_a? ActiveRecord::Reflection::ThroughReflection
          has_many_association = has_many_association.through_reflection
        end

        foreign_key  = has_many_association.foreign_key.to_s
        child_class  = has_many_association.klass
        reflection   = child_class._reflections.values.find do |e|
          e.belongs_to? &&
            e.foreign_key.to_s == foreign_key &&
            e.options[:counter_cache].present?
        end
        counter_name = reflection.counter_cache_column

        count = object.send(counter_association).count(:all)
        count += object.send("unit_#{counter_association}").count(:all) if object.organization_type == 'unit'
        stmt = unscoped.where(arel_table[primary_key].eq(object.id))
                       .arel.compile_update({ arel_table[counter_name] => count }, primary_key)
        connection.update stmt
      end
      true
    end
  end
end
