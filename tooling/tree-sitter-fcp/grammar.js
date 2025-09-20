module.exports = grammar({
  name: 'fcp',
  extras: $ => [
    /\s|\\\r?\n/,
    $.comment,
  ],
  inline: $ => [
    $._struct_name,
    $._struct_field_name,
    $._composed_type,
    $._param_name,
    $._enum_name,
    $._enum_field_name,
    $._method_name,
    $._service_name,
    $._method_input_type,
    $._method_output_type,
  ],
  rules: {
    source_file: $ => seq($.preamble, repeat1(choice($.struct, $.enum_block, $.impl, $.service, $.device, $.mod_expr))),

    preamble: $ => seq('version', ':', $.string),

    struct: $ => seq('struct', $._struct_name, '{', repeat1($.struct_field), '}'),
    _struct_name: $ => alias(
      $.identifier,
      $.struct_name,
    ),
    struct_field: $ => seq($._struct_field_name, '@', $.number, ':', $.type, repeat($.param), ','),
    _struct_field_name: $ => alias(
      $.identifier,
      $.struct_field_name
    ),

    type: $ => seq(choice($.base_type, $.array_type, $._composed_type, $.dynamic_array_type, $.optional_type), optional('|')),
    base_type: $ => /u\d\d|u\d|i\d\d|i\d|f32|f64/,
    array_type: $ => seq('[', $.type, ',', $.number ,']'),
    dynamic_array_type: $ => seq('[', $.type, ']'),
    optional_type: $ => seq('Optional', '[',  $.type, ']'),
    _composed_type: $ => alias(
      $.identifier,
      $.composed_type
    ),

    param: $ => prec.left(seq($._param_name, optional('('), repeat($.param_argument), optional(')'), optional('|'))),
    _param_name: $ => alias(
      $.identifier,
      $.param_name
    ),

    param_argument: $ => prec.left(seq($.value, optional(','))),

    enum_block: $ => seq('enum', $._enum_name, '{', repeat1($.enum_field), '}'),
    _enum_name: $ => alias($.identifier, $.enum_name),
    enum_field: $ => seq($._enum_field_name, '=', $.value, ','),
    _enum_field_name: $ => alias($.identifier, $.enum_field_name),

    impl: $ => seq('impl', $.identifier, 'for', $.identifier, '{', repeat1(choice($.extension_field, $.signal_block)), '}'),
    extension_field: $ => seq($.identifier, ':', $.value, ','),
    signal_block: $ => seq('signal', $.identifier, '{', repeat1($.extension_field), '}', ','),

    service: $ => seq('service', $._service_name, '@', $.number, '{', repeat1($.method), '}'),
    _service_name: $ => alias($.identifier, $.service_name),
    method: $ => seq('method', $._method_name, '(', $._method_input_type, ')', '@', $.number, 'returns', $._method_output_type),
    _method_name: $ => alias($.identifier, $.method_name),
    _method_input_type: $ => alias($.identifier, $.method_input_type),
    _method_output_type: $ => alias($.identifier, $.method_output_type),

    device: $ => seq('device', $.identifier, '{', repeat1($.device_field), '}'),
    device_field: $ => seq($.device_field_name, ':', $.value, ','),
    device_field_name: $ => $.identifier,

    mod_expr: $ => seq('mod', $._mod_name, ';'),
    _mod_name: $ => alias($.identifier, $.mod_name),

    value: $ => choice($.identifier, $.number, $.string),
    identifier: _ => /[a-zA-Z_][a-zA-Z_\d]*/,
    string: _ => /(".*?")/,
    number: _ => /\d+/,

    comment: _ => token(choice(
      seq('//', /(\\+(.|\r?\n)|[^\\\n])*/),
      seq(
        '/*',
        /[^*]*\*+([^/*][^*]*\*+)*/,
        '/',
      ),
    )),
  }
});
