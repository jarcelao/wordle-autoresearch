# Self-Optimizing Programs using Autoresearch

Slides and code for my lightning talk during PythonAsia 2026.

## Running Experiments

`src/` contains a full harness to build Wordle agents and an autoresearch experiment log.

I used [pi-autoresearch](https://github.com/davebcn87/pi-autoresearch/) to run the main experiment loop. Refer to [autoresearch.md](src/autoresearch.md) for an overview of the experiment.

Simply run `/autoresearch continue` from the `src/` directory to continue the loop.

## Slides

Slides are available in `slides/`. I used [presenterm](https://github.com/mfontanini/presenterm) to generate the slides.

```bash
cd slides/
presenterm --present autoresearch.md
```

