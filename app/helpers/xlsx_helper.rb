# frozen_string_literal: true

module XlsxHelper
  # Returns a list of the widths used for styling export outputs
  #
  # @param fields [Array] the fields to generate a list of formats
  # @return [Array] list of widths to the fields
  def field_widths(fields)
    fields.map { |field| LENGTHY_FIELDS.include?(field) ? 30 : nil }
  end

  # Returns a list of the formats used for styling export outputs
  #
  # @param fields [Array] the fields to generate a list of formats
  # @return [Array] list of associated formats to the fields
  def field_formats(fields)
    fields.map { |field| CURRENCY_FIELDS.include?(field) ? :currency : nil }
  end

  def formats_and_widths(fields)
    [field_formats(fields), field_widths(fields)]
  end

  def currency_field?(field)
    CURRENCY_FIELDS.include? field
  end
end
