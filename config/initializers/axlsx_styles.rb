module Axlsx
  # Workbook class from the Axlsx xlsx_package
  class Workbook
    # Returns style definitions for axlsx workbook formatting.
    #
    # @param [xlsx_package.workbook] object for creating the styles
    # @return [Hash] style definitions that can be used to format workbook
    # rubocop:disable Metrics/AbcSize,Metrics/MethodLength
    def define_styles
      # Define style components
      title_font_size = 16
      header_font_size = 14
      summary_description_font_size = 14
      summary_result_font_size = 12
      title_font = { sz: title_font_size, b: true }
      header_font = { sz: header_font_size, b: true }
      summary_description_font = { sz: summary_description_font_size, b: true, i: true }
      summary_result_font = { sz: summary_result_font_size, b: true }
      currency_format = { format_code: '$#,##0.00;($#,##0.00)' }
      top_border = { border: { style: :thick, color: '000000', name: :top, edges: [:top] } }
      bottom_border = { border: { style: :thick, color: '000000', name: :bottom, edges: [:bottom] } }

      # Style definitions
      styles = {}
      styles[:currency] = self.styles.add_style(currency_format)
      styles[:extra_title] = self.styles.add_style(title_font)
      styles[:title] = self.styles.add_style title_font.merge(bg_color: 'FFFF00')
      styles[:header] = self.styles.add_style header_font.merge(bg_color: 'D9D9D9')
      styles[:header_bottom_border] = self.styles.add_style header_font.merge(bg_color: 'D9D9D9')
                                      .merge(bottom_border)
      styles[:summary_description] = self.styles.add_style summary_description_font
      styles[:summary_result] = self.styles.add_style summary_result_font.merge(bg_color: 'D9D9D9')
      styles[:summary_result_currency] = self.styles.add_style summary_result_font.merge(currency_format)
                                         .merge(bg_color: 'D9D9D9')
      styles[:summary_result_top_border] = self.styles.add_style summary_result_font
                                           .merge(bg_color: 'D9D9D9').merge(top_border)
      styles[:summary_result_top_border_currency] = self.styles.add_style summary_result_font.merge(currency_format)
                                                    .merge(bg_color: 'D9D9D9').merge(top_border)
      styles
    end
    # rubocop:enable Metrics/AbcSize,Metrics/MethodLength
  end
end
