# frozen_string_literal: true

# a mixin to add ability for organization to express themselves as flat trees
module Flattenable
  extend ActiveSupport::Concern

  class_methods do
    # this turns the
    def flat_tree
      child_mapper = lambda do |tree, node|
        tree << node
        tree += node.children.reduce([], &child_mapper) unless node.children.empty?
        return tree.flatten
      end
      includes(children: { children: [:children] })
        .where(organization_type: organization_types[:root]).inject([], &child_mapper)
    end
  end

  included do
    def flat_tree_description
      prefix = +''
      org_parent = parent
      while org_parent
        prefix << '--'
        org_parent = org_parent.parent
      end
      "#{prefix} #{description}"
    end

    def as_json(options = {})
      org = super
      org[:id] = org['id']
      org[:parent] = org['organization_id'] || '#'
      org[:icon] = type_icon
      org[:text] ||= text
      org[:state] = { opened: true }
      org
    end
  end
end
