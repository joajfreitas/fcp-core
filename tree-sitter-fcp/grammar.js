module.exports = grammar({
  name: 'fcp',
  extras: $ => [
    /\s|\\\r?\n/,
    $.comment,
  ],
  rules: {
    source_file: $ => seq($.preamble, repeat1(choice($.struct, $.enum_block, $.impl, $.service, $.device, $.mod_expr))),

    preamble: $ => seq('version', ':', $.string),

    struct: $ => seq('struct', $.struct_name, '{', repeat1($.struct_field), '}'),
    struct_name: $ => $.identifier,
    struct_field: $ => seq($.struct_field_name, '@', $.number, ':', $.type, repeat($.param), ','),
    struct_field_name: $ => $.identifier,

    type: $ => seq(choice($.base_type, $.array_type, $.composed_type, $.dynamic_array_type, $.optional_type), optional('|')),
    base_type: $ => /u\d\d|u\d|i\d\d|i\d|f32|f64/,
    array_type: $ => seq('[', $.type, ',', $.number ,']'),
    dynamic_array_type: $ => seq('[', $.type, ']'),
    optional_type: $ => seq('Optional', '[',  $.type, ']'),
    composed_type: $ => $.identifier,

    param: $ => prec.left(seq($.param_name, optional('('), repeat($.param_argument), optional(')'), optional('|'))),
    param_name: $ => $.identifier,

    param_argument: $ => prec.left(seq($.value, optional(','))),

    enum_block: $ => seq('enum', $.enum_name, '{', repeat1($.enum_field), '}'),
    enum_name: $ => $.identifier,
    enum_field: $ => seq($.enum_field_name, '=', $.value, ','),
    enum_field_name: $ => $.identifier,

    impl: $ => seq('impl', $.identifier, 'for', $.identifier, '{', repeat1(choice($.extension_field, $.signal_block)), '}'),
    extension_field: $ => seq($.identifier, ':', $.value, ','),
    signal_block: $ => seq('signal', $.identifier, '{', repeat1($.extension_field), '}', ','),

    service: $ => seq('service', $.identifier, '@', $.number, '{', repeat1($.method), '}'),
    method: $ => seq('method', $.method_name, '(', $.method_input_type, ')', '@', $.number, 'returns', $.method_output_type),
    method_name: $ => $.identifier,
    method_input_type: $ => $.identifier,
    method_output_type: $ => $.identifier,

    device: $ => seq('device', $.identifier, '{', repeat1($.device_field), '}'),
    device_field: $ => seq($.device_field_name, ':', $.value, ','),
    device_field_name: $ => $.identifier,

    mod_expr: $ => seq('mod', $.identifier, ';'),

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
