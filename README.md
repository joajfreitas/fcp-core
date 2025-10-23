![](https://github.com/joajfreitas/fcp-core/actions/workflows/ci.yml/badge.svg)

# FCP

FCP is an interface description language to exchange information independently of language and platform.

## Install

	$ pip install fcp

## Example

![Code showcase](https://raw.githubusercontent.com/joajfreitas/fcp-core/master/assets/code_showcase.png)

## Documentation

See [readthedocs.io](https://fcp-core.readthedocs.io/en/latest/)

 * [Contributing](./CONTRIBUTING.md)
 * [Authors](./AUTHORS)
 * [License](./LICENSE)

## Supported features

|                            | core  | dbc  | c  | cpp  | python  |
|----------------------------|-------|------|----|------|---------|
| Flat struct                |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| 1-64 bit signed integers   |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| 1-64 bit unsigned integers |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| 32/64 bit float            |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| Composite struct           |   ✅  |  ✅  | ❌ |  ✅  |    ✅   |
| Enum                       |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| Array                      |   ✅  |  ✅  | ❌ |  ✅  |    ✅   |
| Dynamic array              |   ✅  |  ❌  | ❌ |  ✅  |    ✅   |
| String                     |   ✅  |  ❌  | ❌ |  ✅  |    ✅   |
| Optional                   |   ❌  |  ❌  | ❌ |  ✅  |    ✅   |
| Frame id                   |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| Device designation         |   ✅  |  ✅  | ✅ |  ✅  |    ✅   |
| Bus designation            |   ✅  |  ✅  | ❌ |  ❌  |    ❌   |
| Big endian                 |   ✅  |  ✅  | ✅ |  ❌  |    ❌   |
| Muxes                      |   ✅  |  ✅  | ✅ |  ❌  |    ❌   |

## Plugins

 * [dbc](https://github.com/joajfreitas/fcp-core/tree/master/plugins/fcp_dbc)
 * [can_c](https://github.com/joajfreitas/fcp-core/tree/master/plugins/fcp_can_c)
 * [cpp](https://github.com/joajfreitas/fcp-core/tree/master/plugins/fcp_cpp)

## Editor support

 * [neovim](https://github.com/joajfreitas/fcp.vim)
 * [DiogoFerreira.fcp on Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=DiogoFerreira.fcp)