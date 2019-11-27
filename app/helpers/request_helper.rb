# frozen_string_literal: true

module RequestHelper
  # Calls the field on the record and attempts to display it.
  # If there is special formatting on the field, define a "render_FIELD_NAME"
  # method that takes the record and tweaks the field
  #
  # @param record [ActiveRecord] the record with the field
  # @param field [Symbol] the field name ( use __ to indicate associations )
  # @param format [Symbol] any special format to call a specific render method
  # @return [String] value from record field
  def call_record_field(record, field, format = nil)
    method = "render_#{field}_#{format}".chomp('_').intern
    if respond_to? method
      send(method, record)
    else
      record.call_field(field)
    end
  end

  def render_fiscal_year(record)
    FiscalYear.to_fy record.fiscal_year.year
  end

  # Formats review status based on the code
  # @param record [ActiveRecord] the record to be called
  def render_review_status__name(record)
    record.review_status.name == 'Under Review' ? '' : record.review_status.name
  end

  # Returns if we are in the arcihve mode
  def archive?
    params[:archive] == 'true' || params[:archive] == true
  end

  def reset_sorts_link
    if @model_klass.name == 'Request'
      link_to(t('reset_sorting'), my_requests_path, class: 'btn btn-link')
    elsif sorted?
      link_to(t('reset_sorting'), polymorphic_path(@model_klass.source_class,
                                                   archive: params[:archive]), class: 'btn btn-link')
    end
  end

  # Returns a list of fields for a record
  #
  # @param klass [Class] the active record klass being displayed
  # @param show_all [Boolean] option to include all fields in class
  # @return [Array] the list of fields being displayed
  def fields(klass, show_all = false)
    fields = send(:"#{klass.to_s.underscore}_fields") unless show_all
    fields = send(:"#{klass.to_s.underscore}_all_fields") if show_all
    fields
  end

  # Generate methods that renders fields as currency
  CURRENCY_FIELDS.each do |m|
    define_method("render_#{m}".intern) { |r| number_to_currency r.call_field(m.intern) }
  end

  # Returns an array of the fields used in labor_requests
  #
  # @return [Array] list of fields
  def labor_request_fields
    labor_request_all_fields - %i[nonop_source justification review_comment created_at updated_at]
  end

  # Returns an ordered array of all the fields used in labor_requests
  #
  # @return [Array] list of fields
  def labor_request_all_fields
    LaborRequest.fields
  end

  # Returns an  array of the fields used in staff_requests
  #
  # @return [Array] list of fields
  def staff_request_fields
    staff_request_all_fields - %i[nonop_source justification review_comment created_at updated_at]
  end

  # Returns an ordered array of all the fields used in contractor_requests
  #
  # @return [Array] list of fields
  def staff_request_all_fields
    StaffRequest.fields
  end

  # Returns an array of the fields used in contractor_requests
  #
  # @return [Array] list of fields
  def contractor_request_fields
    contractor_request_all_fields - %i[nonop_source justification review_comment created_at updated_at]
  end

  # Returns an ordered array of all the fields used in contractor_requests
  #
  # @return [Array] list of fields
  def contractor_request_all_fields
    ContractorRequest.fields
  end
end
