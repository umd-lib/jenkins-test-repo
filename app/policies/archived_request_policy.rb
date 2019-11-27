# frozen_string_literal: true

class ArchivedRequestPolicy < RequestPolicy
  def create?
    false
  end

  def new?
    create?
  end

  def edit?
    create?
  end

  def update?
    create?
  end

  def destroy?
    create?
  end

  class Scope
    attr_reader :user, :scope

    def initialize(user, scope)
      @user = user
      @scope = scope
    end

    def resolve
      @user.admin? ? @scope.all : scoped_query
    end

    private

      def scoped_query
        @scope.where(@scope.arel_table[:organization_id].in(@user.all_organizations.map(&:id))
            .or(@scope.arel_table[:unit_id].in(@user.all_organizations
            .select { |o| o.organization_type == 'unit' }.map(&:id))))
      end
  end
end
