# Contributing

## Enable git hooks

First install: https://pre-commit.com/

Then run:

`pre-commit install`

## Submitting patches

Create a github pull request from a [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) or a branch of fcp-core.

Don't forget to add your name to the [AUTHORS](./AUTHORS) file.

## Testing changes locally

I recommend using [uv](https://github.com/astral-sh/uv) to ensure you use the same tool versions as the ci.

```
make RUN_UNDER="uvx -p 3.12" ci # Running all the ci checks
make RUN_UNDER="uvx -p 3.12" tests # Run unit tests
make RUN_UNDER="uvx -p 3.12" lint # Run the linter
make RUN_UNDER="uvx -p 3.12" format # Format the source files
```
