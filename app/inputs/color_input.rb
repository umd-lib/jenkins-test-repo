# frozen_string_literal: true

# defines a color picker input for simple form
class ColorInput < SimpleForm::Inputs::Base
  def input(wrapper_options)
    merged_input_options = merge_wrapper_options(input_html_options, wrapper_options)
    merged_input_options[:type] = 'color'
    @builder.text_field(attribute_name, merged_input_options)
  end
end
