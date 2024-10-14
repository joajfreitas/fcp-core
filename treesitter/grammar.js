module.exports = grammar({
  name: 'fcp',

  rules: {
    source_file: $ => seq($.preamble, choice($.struct)),

    preamble: $ => seq('version', ':', $.string),

    struct: $ => seq(repeat($.comment), 'struct', field('name', $.identifier), '{', field('fields', repeat1($.struct_field)), '}'),
    struct_field: $ => seq(repeat($.comment), field('name', $.identifier), '@', $.number, ':', $.type, repeat($.param), ','),
    type: $ => seq(choice($.base_type, $.array_type, $.compound_type), optional('|')),
    base_type: $ => /u\d\d|u\d|i\d\d|i\d|f32|f64/,
    array_type: $ => seq('[', $.type, ',', $.number ,']'),
    compound_type: $ => $.identifier,

    param: $ => prec.left(seq($.identifier, optional('('), repeat($.param_argument), optional(')'), optional('|'))),

    param_argument: $ => prec.left(seq($.value, optional(','))),

    enum: $ => seq(optional($.comment), 'enum', $.string),

    value: $ => choice($.identifier, $.number, $.string),
    identifier: _ => /[a-zA-Z_][a-zA-Z_\d]*/,
    string: _ => /(".*?")/,
    comment: _ => /\/\/[^\n\r]+[\n\r]|\*\)/,
    number: _ => /\d+/,
  }
});
